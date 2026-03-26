"""
leader_node.py
==============
MDE Step 4: Full Implementation — Leader Robot Node

Implements the complete 6-state coordination state machine for the
leader TurtleBot3 Burger robot.

State machine:
  INIT → WAITING_FOR_FOLLOWER (if follower far)
       → EXPLORING             (if follower close)

  EXPLORING → WAITING_FOR_FOLLOWER   (follower drifted too far)
            → DEAD_END               (LiDAR detects no escape route)
            → WAITING_FOR_LOST_FOLLOWER (follower timeout)

  DEAD_END  → REVERSING              (follower acked CMD_DEAD_END)

  REVERSING → EXPLORING              (forward path clear again)

  WAITING_FOR_FOLLOWER      → EXPLORING   (follower approches & ready)
  WAITING_FOR_LOST_FOLLOWER → EXPLORING   (follower found us)

Navigation strategy:
  - Simple reactive navigation: drive forward in clear direction (frontier).
  - Dead-end detection via LiDAR sector analysis.
  - For a real SLAM-driven system, integrate Nav2 frontier exploration
    (e.g. explore_lite or nav2_frontier_exploration package).

Usage:
  ros2 run leader_node leader_node
  (or via simulation.launch.py)
"""

import math
import time
from enum import IntEnum
from typing import Optional, List

import rclpy
from rclpy.action import ActionClient
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy, DurabilityPolicy

from geometry_msgs.msg import Twist, PoseStamped, Quaternion
from nav_msgs.msg import Odometry
from sensor_msgs.msg import LaserScan
from std_msgs.msg import Header

from nav2_msgs.action import NavigateToPose

from leader_follower_msgs.msg import RobotStatus, CoordinationCommand


# ============================================================
# STATE ENUM
# ============================================================

class LeaderState(IntEnum):
    INIT = 0
    WAITING_FOR_FOLLOWER = 1
    EXPLORING = 2
    DEAD_END = 5
    REVERSING = 6
    WAITING_FOR_LOST_FOLLOWER = 11


# ============================================================
# TUNABLE PARAMETERS
# ============================================================

# Distance thresholds (meters)
FOLLOW_DISTANCE_OK = 1.0        # Follower close enough → start/resume exploring
FOLLOW_DISTANCE_FAR = 1.5       # Follower too far → leader pauses
DEAD_END_RANGE = 0.40           # Obstacle closer than this = "blocked"
REVERSAL_CLEAR_RANGE = 0.80     # Forward must be > this to stop reversing

# Angular half-widths for LiDAR sectors (degrees)
FORWARD_HALF_DEG = 30           # ±30° = 60° forward cone
LEFT_START_DEG = 60
LEFT_END_DEG = 120
RIGHT_START_DEG = 240
RIGHT_END_DEG = 300

# Timeouts (seconds)
FOLLOWER_TIMEOUT = 5.0          # No msg → lost
DEAD_END_ACK_TIMEOUT = 15.0     # Max wait for CMD_BACKED_UP
WAIT_FOLLOWER_TIMEOUT = 60.0    # Max wait for follower to approach
LOST_FOLLOWER_TIMEOUT = 120.0   # Max wait when searching

# Dead-end retry interval (seconds)
DEAD_END_BROADCAST_INTERVAL = 2.0

# Velocities
EXPLORE_LINEAR = 0.15           # m/s forward while exploring
EXPLORE_ANGULAR_MAX = 1.0       # rad/s max turn rate while navigating
REVERSE_LINEAR = -0.10          # m/s backward
HEARTBEAT_HZ = 2.0              # I_AM_HERE broadcast frequency
STATUS_HZ = 10.0                # Status publish frequency

# Sector counts to confirm dead end (avoid single-scan false positives)
DEAD_END_CONFIRM_SCANS = 3


def _euler_to_quat(yaw: float) -> Quaternion:
    """Convert a yaw angle (rad) to a ROS Quaternion."""
    q = Quaternion()
    q.z = math.sin(yaw / 2.0)
    q.w = math.cos(yaw / 2.0)
    return q


def _yaw_from_quat(q: Quaternion) -> float:
    return math.atan2(
        2.0 * (q.w * q.z + q.x * q.y),
        1.0 - 2.0 * (q.y * q.y + q.z * q.z),
    )


class LeaderNode(Node):
    """Full-implementation leader coordination node."""

    def __init__(self) -> None:
        super().__init__("leader_node")

        # ── State machine ──────────────────────────────────────────────
        self.state = LeaderState.INIT
        self.state_entry_time: float = time.monotonic()

        # ── Sensor cache ───────────────────────────────────────────────
        self.latest_scan: Optional[LaserScan] = None
        self.current_pose: Optional[PoseStamped] = None
        self.current_yaw: float = 0.0

        # ── Follower tracking ──────────────────────────────────────────
        self.follower_status: Optional[RobotStatus] = None
        self.last_follower_time: float = 0.0          # monotonic timestamp
        self.follower_distance: float = float("inf")

        # ── Dead-end bookkeeping ───────────────────────────────────────
        self.dead_end_confirm_count: int = 0           # consecutive dead-end scans
        self.dead_end_ack_received: bool = False
        self.last_dead_end_broadcast: float = 0.0

        # ── Exploration: simple turn-and-go reactive navigator ─────────
        # We track the direction of the most open LiDAR sector
        self.explore_turn_direction: float = 0.0      # +1 left, -1 right, 0 forward

        # ── QoS ────────────────────────────────────────────────────────
        sensor_qos = QoSProfile(
            reliability=ReliabilityPolicy.BEST_EFFORT,
            durability=DurabilityPolicy.VOLATILE,
            depth=5,
        )
        rel_qos = QoSProfile(
            reliability=ReliabilityPolicy.RELIABLE,
            durability=DurabilityPolicy.VOLATILE,
            depth=10,
        )

        # ── Subscriptions ──────────────────────────────────────────────
        self.create_subscription(LaserScan, "/leader/scan", self._cb_scan, sensor_qos)
        self.create_subscription(Odometry, "/leader/odom", self._cb_odom, sensor_qos)
        self.create_subscription(
            RobotStatus, "/follower/status", self._cb_follower_status, rel_qos
        )
        self.create_subscription(
            CoordinationCommand,
            "/leader/command",
            self._cb_follower_command,
            rel_qos,
        )

        # ── Publishers ─────────────────────────────────────────────────
        self.pub_cmd = self.create_publisher(Twist, "/leader/cmd_vel", 10)
        self.pub_status = self.create_publisher(RobotStatus, "/leader/status", rel_qos)
        self.pub_follower_cmd = self.create_publisher(
            CoordinationCommand, "/follower/command", rel_qos
        )

        # ── Nav2 (optional, for real frontier goals) ───────────────────
        self._nav2 = ActionClient(self, NavigateToPose, "/leader/navigate_to_pose")

        # ── Timers ─────────────────────────────────────────────────────
        self.create_timer(1.0 / STATUS_HZ, self._tick)
        self.create_timer(1.0 / HEARTBEAT_HZ, self._heartbeat)

        self.get_logger().info("LeaderNode ready — INIT")

    # ================================================================
    # CALLBACKS
    # ================================================================

    def _cb_scan(self, msg: LaserScan) -> None:
        self.latest_scan = msg

    def _cb_odom(self, msg: Odometry) -> None:
        p = PoseStamped()
        p.header = msg.header
        p.pose = msg.pose.pose
        self.current_pose = p
        self.current_yaw = _yaw_from_quat(msg.pose.pose.orientation)

    def _cb_follower_status(self, msg: RobotStatus) -> None:
        self.follower_status = msg
        self.last_follower_time = time.monotonic()
        if self.current_pose:
            dx = msg.x - self.current_pose.pose.position.x
            dy = msg.y - self.current_pose.pose.position.y
            self.follower_distance = math.sqrt(dx * dx + dy * dy)

    def _cb_follower_command(self, msg: CoordinationCommand) -> None:
        cmd = msg.command
        self.get_logger().info(f"← follower cmd {cmd}")

        if cmd == CoordinationCommand.CMD_READY:
            if self.state in (LeaderState.INIT, LeaderState.WAITING_FOR_FOLLOWER):
                self._transition(LeaderState.EXPLORING)

        elif cmd == CoordinationCommand.CMD_BACKED_UP:
            self.dead_end_ack_received = True

        elif cmd == CoordinationCommand.CMD_LOST_YOU:
            if self.state == LeaderState.EXPLORING:
                self._transition(LeaderState.WAITING_FOR_LOST_FOLLOWER)

        elif cmd == CoordinationCommand.CMD_FOUND_YOU:
            if self.state == LeaderState.WAITING_FOR_LOST_FOLLOWER:
                self._transition(LeaderState.EXPLORING)

    # ================================================================
    # MAIN STATE MACHINE
    # ================================================================

    def _tick(self) -> None:
        """10 Hz state machine dispatcher + status publisher."""
        {
            LeaderState.INIT: self._s_init,
            LeaderState.WAITING_FOR_FOLLOWER: self._s_waiting_for_follower,
            LeaderState.EXPLORING: self._s_exploring,
            LeaderState.DEAD_END: self._s_dead_end,
            LeaderState.REVERSING: self._s_reversing,
            LeaderState.WAITING_FOR_LOST_FOLLOWER: self._s_waiting_for_lost,
        }[self.state]()

        self._publish_status()

    def _heartbeat(self) -> None:
        """Broadcast I_AM_HERE while waiting for lost follower."""
        if self.state == LeaderState.WAITING_FOR_LOST_FOLLOWER and self.current_pose:
            p = self.current_pose.pose.position
            self._send(CoordinationCommand.CMD_I_AM_HERE, f"{p.x:.4f},{p.y:.4f}")

    # ================================================================
    # STATE HANDLERS
    # ================================================================

    def _s_init(self) -> None:
        """
        INIT: Wait until we have follower status, then decide where to go.
        If follower is already close → explore; else → wait for it.
        """
        self._stop()
        if self.follower_status is None:
            return  # not yet heard from follower
        if self.follower_distance <= FOLLOW_DISTANCE_OK:
            self._transition(LeaderState.EXPLORING)
        else:
            self._transition(LeaderState.WAITING_FOR_FOLLOWER)

    def _s_waiting_for_follower(self) -> None:
        """
        WAITING_FOR_FOLLOWER: Halt and wait for follower to catch up.
        Transition triggered by CMD_READY from follower OR by distance check.
        """
        self._stop()
        if self._secs() > WAIT_FOLLOWER_TIMEOUT:
            self.get_logger().warn("Follower wait timeout — staying paused")
            return
        # Also check live distance (in case follower approaches without sending CMD_READY)
        if self.follower_distance <= FOLLOW_DISTANCE_OK and self._follower_alive():
            self._transition(LeaderState.EXPLORING)

    def _s_exploring(self) -> None:
        """
        EXPLORING: Reactive frontier exploration with dead-end detection.
        Priority checks (in order):
          1. Follower connectivity timeout → WAITING_FOR_LOST_FOLLOWER
          2. Follower too far → WAITING_FOR_FOLLOWER
          3. Dead end confirmed → DEAD_END
          4. Otherwise: reactive navigation (turn toward open space)
        """
        # 1. Connectivity
        if not self._follower_alive():
            self.get_logger().warn("Follower timeout → WAITING_FOR_LOST_FOLLOWER")
            self._transition(LeaderState.WAITING_FOR_LOST_FOLLOWER)
            return

        # 2. Distance
        if self.follower_distance > FOLLOW_DISTANCE_FAR:
            self.get_logger().info(
                f"Follower too far ({self.follower_distance:.2f}m) → WAITING_FOR_FOLLOWER"
            )
            self._stop()
            self._transition(LeaderState.WAITING_FOR_FOLLOWER)
            return

        # 3. Dead end
        if self._is_dead_end():
            self.dead_end_confirm_count += 1
            if self.dead_end_confirm_count >= DEAD_END_CONFIRM_SCANS:
                self.get_logger().warn("Dead end confirmed → DEAD_END")
                self.dead_end_confirm_count = 0
                self._stop()
                self._send(CoordinationCommand.CMD_DEAD_END)
                self.last_dead_end_broadcast = time.monotonic()
                self.dead_end_ack_received = False
                self._transition(LeaderState.DEAD_END)
                return
        else:
            self.dead_end_confirm_count = 0

        # 4. Reactive navigation
        self._reactive_navigate()

    def _s_dead_end(self) -> None:
        """
        DEAD_END: Wait for follower to back up (CMD_BACKED_UP), then reverse.
        Re-broadcast CMD_DEAD_END every DEAD_END_BROADCAST_INTERVAL seconds.
        Force reversal after ACK_TIMEOUT.
        """
        self._stop()
        now = time.monotonic()

        # Re-broadcast
        if now - self.last_dead_end_broadcast > DEAD_END_BROADCAST_INTERVAL:
            self._send(CoordinationCommand.CMD_DEAD_END)
            self.last_dead_end_broadcast = now

        # ACK received → begin reversal
        if self.dead_end_ack_received:
            self.get_logger().info("Follower backed up → REVERSING")
            self._transition(LeaderState.REVERSING)
            return

        # Timeout → force reversal
        if self._secs() > DEAD_END_ACK_TIMEOUT:
            self.get_logger().warn("Dead-end ACK timeout → force REVERSING")
            self._transition(LeaderState.REVERSING)

    def _s_reversing(self) -> None:
        """
        REVERSING: Back out of dead end until forward sector is clear.
        Then notify follower (CMD_RESUME) and resume exploration.
        """
        # Check forward clearance
        fwd_min = self._sector_min(self.latest_scan, -FORWARD_HALF_DEG, FORWARD_HALF_DEG)
        if fwd_min >= REVERSAL_CLEAR_RANGE:
            self._stop()
            self.get_logger().info(f"Path clear ({fwd_min:.2f}m) → EXPLORING")
            self._send(CoordinationCommand.CMD_RESUME)
            self._transition(LeaderState.EXPLORING)
            return

        # Drive backward
        twist = Twist()
        twist.linear.x = REVERSE_LINEAR
        self.pub_cmd.publish(twist)

    def _s_waiting_for_lost(self) -> None:
        """
        WAITING_FOR_LOST_FOLLOWER: Halt; _heartbeat() broadcasts I_AM_HERE.
        CMD_FOUND_YOU from follower triggers transition back to EXPLORING.
        """
        self._stop()
        if self._secs() > LOST_FOLLOWER_TIMEOUT:
            self.get_logger().error(
                "Follower search TIMEOUT (120s) — operator intervention required"
            )

    # ================================================================
    # REACTIVE NAVIGATION (simple LiDAR-based exploration)
    # ================================================================

    def _reactive_navigate(self) -> None:
        """
        Drive forward; steer toward the most open LiDAR sector.
        This gives a simple wall-following / open-space-seeking behavior
        suitable for basic SLAM exploration in the simulated room.
        For real frontier exploration, replace with Nav2 action calls.
        """
        if self.latest_scan is None:
            return

        # Find best heading: sample 8 directions, pick widest open one
        best_angle_deg = 0.0
        best_clearance = 0.0
        for ang in range(-150, 180, 30):
            center = ang
            half = 20
            clearance = self._sector_min(self.latest_scan, center - half, center + half)
            if clearance > best_clearance:
                best_clearance = clearance
                best_angle_deg = float(ang)

        # Current forward is 0°; positive best_angle_deg → turn left
        angle_err = math.radians(best_angle_deg)
        # Normalise to [-π, π]
        angle_err = math.atan2(math.sin(angle_err), math.cos(angle_err))

        # If we're pointing roughly forward (best direction), drive forward;
        # otherwise turn in place slowly.
        fwd_clear = self._sector_min(self.latest_scan, -FORWARD_HALF_DEG, FORWARD_HALF_DEG)

        twist = Twist()
        if abs(angle_err) < math.radians(20) and fwd_clear > DEAD_END_RANGE:
            twist.linear.x = EXPLORE_LINEAR
        twist.angular.z = float(
            max(-EXPLORE_ANGULAR_MAX, min(EXPLORE_ANGULAR_MAX, angle_err * 0.8))
        )
        self.pub_cmd.publish(twist)

    # ================================================================
    # DEAD-END DETECTION
    # ================================================================

    def _is_dead_end(self) -> bool:
        """
        True when the forward cone is blocked AND there is no viable
        escape route to the left or right.

        Three-sector analysis:
          forward  = ±FORWARD_HALF_DEG
          left     = 60° – 120°
          right    = 240° – 300°   (or -120° – -60°)
        """
        if self.latest_scan is None:
            return False
        fwd = self._sector_min(
            self.latest_scan, -FORWARD_HALF_DEG, FORWARD_HALF_DEG
        )
        left = self._sector_min(self.latest_scan, LEFT_START_DEG, LEFT_END_DEG)
        right = self._sector_min(
            self.latest_scan, RIGHT_START_DEG, RIGHT_END_DEG
        )

        forward_blocked = fwd < DEAD_END_RANGE
        left_blocked = left < DEAD_END_RANGE
        right_blocked = right < DEAD_END_RANGE

        return forward_blocked and (left_blocked or right_blocked)

    # ================================================================
    # LIDAR HELPERS
    # ================================================================

    def _sector_min(
        self,
        scan: Optional[LaserScan],
        deg_start: float,
        deg_end: float,
    ) -> float:
        """
        Return the minimum valid range in the angular sector [deg_start, deg_end].
        Angles in degrees, 0° = robot forward, CCW positive.
        Returns inf if no valid readings found.
        """
        if scan is None:
            return float("inf")

        rad_start = math.radians(deg_start)
        rad_end = math.radians(deg_end)

        min_r = float("inf")
        angle = scan.angle_min
        for r in scan.ranges:
            if rad_start <= angle <= rad_end:
                if scan.range_min < r < scan.range_max and math.isfinite(r):
                    min_r = min(min_r, r)
            angle += scan.angle_increment
        return min_r

    # ================================================================
    # UTILITIES
    # ================================================================

    def _stop(self) -> None:
        self.pub_cmd.publish(Twist())

    def _transition(self, new: LeaderState) -> None:
        self.get_logger().info(f"  ↳ {self.state.name} → {new.name}")
        self.state = new
        self.state_entry_time = time.monotonic()

    def _secs(self) -> float:
        return time.monotonic() - self.state_entry_time

    def _follower_alive(self) -> bool:
        return (
            self.last_follower_time > 0
            and time.monotonic() - self.last_follower_time < FOLLOWER_TIMEOUT
        )

    def _send(self, command: int, data: str = "") -> None:
        msg = CoordinationCommand()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.command = command
        msg.data = data
        self.pub_follower_cmd.publish(msg)

    def _publish_status(self) -> None:
        msg = RobotStatus()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.header.frame_id = "leader/base_footprint"
        msg.state = int(self.state)
        msg.state_name = self.state.name
        if self.current_pose:
            msg.x = self.current_pose.pose.position.x
            msg.y = self.current_pose.pose.position.y
            msg.heading = self.current_yaw
        msg.distance_to_other = self.follower_distance
        self.pub_status.publish(msg)


def main(args=None) -> None:
    rclpy.init(args=args)
    node = LeaderNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()

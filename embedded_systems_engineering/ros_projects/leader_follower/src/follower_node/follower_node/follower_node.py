"""
follower_node.py
================
MDE Step 4: Full Implementation — Follower Robot Node

Implements the complete 7-state coordination state machine for the
follower TurtleBot3 Burger robot.

State machine:
  INIT → APPROACHING (on first leader status)
  APPROACHING → FOLLOWING (distance ≤ APPROACH_THRESHOLD, sends CMD_READY)
              → SEARCHING (leader timeout)
  FOLLOWING   → APPROACHING (leader drifted too far)
              → BACKING_UP  (CMD_DEAD_END / CMD_BACK_UP received)
              → SEARCHING   (leader timeout)
  BACKING_UP  → LEADING_TEMPORARILY (backed up BACKUP_DISTANCE, sends CMD_BACKED_UP)
  LEADING_TEMPORARILY → FOLLOWING (CMD_RESUME received)
                      → SEARCHING (leader timeout)
  SEARCHING   → APPROACHING (leader status received again)

Following control:
  Proportional controller:
    v     = KP_v * (distance - TARGET_DISTANCE)
    omega = KP_w * bearing_to_leader
  Clipped to robot limits. Safety stop if forward obstacle < 0.20m.

Search algorithm:
  1. Navigate to last known leader position (simple Twist controller toward point).
  2. Rotate 360° in place if at destination but leader not found.
  3. After 15 s without finding, expand outward in a square spiral.
  4. Broadcasts CMD_LOST_YOU to leader at 0.5 Hz throughout search.
"""

import math
import time
from enum import IntEnum
from typing import Optional

import rclpy
from rclpy.action import ActionClient
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy, DurabilityPolicy

from geometry_msgs.msg import Twist, PoseStamped, Quaternion
from nav_msgs.msg import Odometry
from sensor_msgs.msg import LaserScan

from nav2_msgs.action import NavigateToPose

from leader_follower_msgs.msg import RobotStatus, CoordinationCommand


# ============================================================
# STATE ENUM
# ============================================================

class FollowerState(IntEnum):
    INIT = 0
    APPROACHING = 4
    FOLLOWING = 3
    BACKING_UP = 9
    LEADING_TEMPORARILY = 7
    SEARCHING_FOR_LEADER = 8
    WAITING_CMD = 10


# ============================================================
# TUNABLE PARAMETERS
# ============================================================

# Distances (m)
TARGET_DISTANCE = 0.50          # Ideal gap leader↔follower
APPROACH_THRESHOLD = 0.70       # Switch APPROACHING → FOLLOWING
FAR_THRESHOLD = 1.50            # Switch FOLLOWING → APPROACHING
SAFETY_STOP = 0.20              # Emergency stop if forward obstacle closer
LEADING_OBSTACLE_STOP = 0.40    # Stop leading if too close to wall
BACKUP_DISTANCE = 1.50          # How far to reverse during dead-end recovery

# Velocities (m/s, rad/s)
MAX_LINEAR = 0.22
MAX_ANGULAR = 1.82
KP_LINEAR = 0.35                # Linear proportional gain
KP_ANGULAR = 0.90               # Angular proportional gain
BACKUP_SPEED = -0.10            # Backward speed
APPROACH_SPEED = 0.18           # Approach linear speed cap
LEADING_SPEED = 0.06            # Slow forward speed while leading temporarily

# Timeouts (s)
LEADER_TIMEOUT = 5.0            # No msg → lost
APPROACH_TIMEOUT = 60.0
SEARCH_TIMEOUT = 90.0

# Search phase timing
ROTATE_PHASE_DURATION = 8.0     # seconds of in-place rotation
EXPAND_PHASE_STEP = 0.60        # expand square side length increment

# Publish rates
STATUS_HZ = 10.0
HEARTBEAT_HZ = 0.5              # CMD_LOST_YOU broadcast interval


def _yaw_from_quat(q: Quaternion) -> float:
    return math.atan2(
        2.0 * (q.w * q.z + q.x * q.y),
        1.0 - 2.0 * (q.y * q.y + q.z * q.z),
    )


def _norm_angle(a: float) -> float:
    """Normalize angle to [-π, π]."""
    return math.atan2(math.sin(a), math.cos(a))


class FollowerNode(Node):
    """Full-implementation follower coordination node."""

    def __init__(self) -> None:
        super().__init__("follower_node")

        # ── State machine ──────────────────────────────────────────────
        self.state = FollowerState.INIT
        self.state_entry_time: float = time.monotonic()

        # ── Sensor cache ───────────────────────────────────────────────
        self.latest_scan: Optional[LaserScan] = None
        self.current_pose: Optional[PoseStamped] = None
        self.current_yaw: float = 0.0

        # ── Leader tracking ────────────────────────────────────────────
        self.leader_status: Optional[RobotStatus] = None
        self.last_leader_time: float = 0.0
        self.leader_distance: float = float("inf")
        self.leader_bearing: float = 0.0      # rad, robot-relative

        # ── Last known leader position ─────────────────────────────────
        self.lkl_x: float = 0.0              # last known leader x
        self.lkl_y: float = 0.0

        # ── Backup tracking ────────────────────────────────────────────
        self.backup_start_x: float = 0.0
        self.backup_start_y: float = 0.0

        # ── Search sub-state ───────────────────────────────────────────
        self.search_phase: int = 0            # 0=go_to_lkl, 1=rotate, 2=expand
        self.search_phase_start: float = 0.0
        self.search_expand_len: float = EXPAND_PHASE_STEP
        self.search_expand_step: int = 0

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
        self.create_subscription(LaserScan, "/follower/scan", self._cb_scan, sensor_qos)
        self.create_subscription(Odometry, "/follower/odom", self._cb_odom, sensor_qos)
        self.create_subscription(
            RobotStatus, "/leader/status", self._cb_leader_status, rel_qos
        )
        self.create_subscription(
            CoordinationCommand,
            "/follower/command",
            self._cb_leader_command,
            rel_qos,
        )

        # ── Publishers ─────────────────────────────────────────────────
        self.pub_cmd = self.create_publisher(Twist, "/follower/cmd_vel", 10)
        self.pub_status = self.create_publisher(RobotStatus, "/follower/status", rel_qos)
        self.pub_leader_cmd = self.create_publisher(
            CoordinationCommand, "/leader/command", rel_qos
        )

        # ── Nav2 ───────────────────────────────────────────────────────
        self._nav2 = ActionClient(self, NavigateToPose, "/follower/navigate_to_pose")

        # ── Timers ─────────────────────────────────────────────────────
        self.create_timer(1.0 / STATUS_HZ, self._tick)
        self.create_timer(1.0 / HEARTBEAT_HZ, self._lost_heartbeat)

        self.get_logger().info("FollowerNode ready — INIT")

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

    def _cb_leader_status(self, msg: RobotStatus) -> None:
        self.leader_status = msg
        self.last_leader_time = time.monotonic()
        self.lkl_x = msg.x
        self.lkl_y = msg.y

        if self.current_pose:
            dx = msg.x - self.current_pose.pose.position.x
            dy = msg.y - self.current_pose.pose.position.y
            self.leader_distance = math.sqrt(dx * dx + dy * dy)
            world_bearing = math.atan2(dy, dx)
            self.leader_bearing = _norm_angle(world_bearing - self.current_yaw)

            # Transition SEARCHING → APPROACHING when leader reappears
            if self.state == FollowerState.SEARCHING_FOR_LEADER:
                self.get_logger().info("Leader found! → APPROACHING")
                self._send(CoordinationCommand.CMD_FOUND_YOU)
                self._transition(FollowerState.APPROACHING)

    def _cb_leader_command(self, msg: CoordinationCommand) -> None:
        cmd = msg.command
        self.get_logger().info(f"← leader cmd {cmd}")

        if cmd in (CoordinationCommand.CMD_DEAD_END, CoordinationCommand.CMD_BACK_UP):
            if self.state == FollowerState.FOLLOWING:
                self._start_backup()
                self._transition(FollowerState.BACKING_UP)

        elif cmd == CoordinationCommand.CMD_RESUME:
            if self.state in (
                FollowerState.LEADING_TEMPORARILY,
                FollowerState.WAITING_CMD,
            ):
                self._transition(FollowerState.FOLLOWING)

        elif cmd == CoordinationCommand.CMD_SEARCH_FOR_ME:
            if self.state != FollowerState.SEARCHING_FOR_LEADER:
                self._begin_search()
                self._transition(FollowerState.SEARCHING_FOR_LEADER)

        elif cmd == CoordinationCommand.CMD_WAIT:
            self._transition(FollowerState.WAITING_CMD)

        elif cmd == CoordinationCommand.CMD_I_AM_HERE:
            # Update last known leader position from heartbeat data
            try:
                x, y = msg.data.split(",")
                self.lkl_x = float(x)
                self.lkl_y = float(y)
            except ValueError:
                pass

    # ================================================================
    # MAIN TICK
    # ================================================================

    def _tick(self) -> None:
        {
            FollowerState.INIT: self._s_init,
            FollowerState.APPROACHING: self._s_approaching,
            FollowerState.FOLLOWING: self._s_following,
            FollowerState.BACKING_UP: self._s_backing_up,
            FollowerState.LEADING_TEMPORARILY: self._s_leading,
            FollowerState.SEARCHING_FOR_LEADER: self._s_searching,
            FollowerState.WAITING_CMD: self._s_waiting,
        }[self.state]()
        self._publish_status()

    def _lost_heartbeat(self) -> None:
        if self.state == FollowerState.SEARCHING_FOR_LEADER:
            self._send(CoordinationCommand.CMD_LOST_YOU)

    # ================================================================
    # STATE HANDLERS
    # ================================================================

    def _s_init(self) -> None:
        self._stop()
        if self.leader_status is not None:
            self.get_logger().info("Leader found → APPROACHING")
            self._transition(FollowerState.APPROACHING)

    def _s_approaching(self) -> None:
        """
        Navigate toward (TARGET_DISTANCE behind leader).
        Uses a simple bearing + distance proportional controller.
        """
        # Timeout guard
        if self._secs() > APPROACH_TIMEOUT:
            self.get_logger().warn("Approach timeout — still trying")

        # Leader lost during approach
        if not self._leader_alive():
            self.get_logger().warn("Leader lost during approach → SEARCHING")
            self._begin_search()
            self._transition(FollowerState.SEARCHING_FOR_LEADER)
            return

        # Close enough → switch to following
        if self.leader_distance <= APPROACH_THRESHOLD:
            self.get_logger().info("In position → FOLLOWING (sending CMD_READY)")
            self._send(CoordinationCommand.CMD_READY)
            self._transition(FollowerState.FOLLOWING)
            return

        # Drive toward a point TARGET_DISTANCE behind leader
        # goal_x/y = leader position - TARGET_DISTANCE in leader's heading direction
        if self.leader_status and self.current_pose:
            lh = self.leader_status.heading
            goal_x = self.leader_status.x - TARGET_DISTANCE * math.cos(lh)
            goal_y = self.leader_status.y - TARGET_DISTANCE * math.sin(lh)

            dx = goal_x - self.current_pose.pose.position.x
            dy = goal_y - self.current_pose.pose.position.y
            dist_to_goal = math.sqrt(dx * dx + dy * dy)
            bearing_to_goal = _norm_angle(math.atan2(dy, dx) - self.current_yaw)

            twist = Twist()
            # Linear: proportional to remaining distance, capped
            twist.linear.x = float(
                max(0.0, min(APPROACH_SPEED, KP_LINEAR * dist_to_goal))
            )
            # Angular: steer toward goal
            twist.angular.z = float(
                max(-MAX_ANGULAR, min(MAX_ANGULAR, KP_ANGULAR * bearing_to_goal))
            )
            # Safety
            if self._fwd_min() < SAFETY_STOP:
                twist.linear.x = 0.0
            self.pub_cmd.publish(twist)

    def _s_following(self) -> None:
        """
        Proportional-control following: maintain TARGET_DISTANCE behind leader.
        """
        # Leader timeout → search
        if not self._leader_alive():
            self.get_logger().warn("Leader lost while following → SEARCHING")
            self._send(CoordinationCommand.CMD_LOST_YOU)
            self._begin_search()
            self._transition(FollowerState.SEARCHING_FOR_LEADER)
            return

        # Leader too far → re-approach
        if self.leader_distance > FAR_THRESHOLD:
            self.get_logger().info(
                f"Leader too far ({self.leader_distance:.2f}m) → APPROACHING"
            )
            self._transition(FollowerState.APPROACHING)
            return

        # Proportional controller
        dist_err = self.leader_distance - TARGET_DISTANCE
        v = KP_LINEAR * dist_err
        omega = KP_ANGULAR * self.leader_bearing

        # Clamp
        v = max(-MAX_LINEAR, min(MAX_LINEAR, v))
        omega = max(-MAX_ANGULAR, min(MAX_ANGULAR, omega))

        # Safety: forward obstacle stop
        if v > 0 and self._fwd_min() < SAFETY_STOP:
            v = 0.0

        twist = Twist()
        twist.linear.x = float(v)
        twist.angular.z = float(omega)
        self.pub_cmd.publish(twist)

    def _s_backing_up(self) -> None:
        """
        Reverse BACKUP_DISTANCE to clear path for leader reversal.
        """
        if self.current_pose:
            dx = self.current_pose.pose.position.x - self.backup_start_x
            dy = self.current_pose.pose.position.y - self.backup_start_y
            backed = math.sqrt(dx * dx + dy * dy)
        else:
            backed = 0.0

        if backed >= BACKUP_DISTANCE:
            self._stop()
            self.get_logger().info("Backed up — sending CMD_BACKED_UP → LEADING_TEMP")
            self._send(CoordinationCommand.CMD_BACKED_UP)
            self._transition(FollowerState.LEADING_TEMPORARILY)
            return

        # Drive backward
        twist = Twist()
        twist.linear.x = BACKUP_SPEED
        self.pub_cmd.publish(twist)

    def _s_leading(self) -> None:
        """
        Move slowly forward to keep space open while leader reverses.
        Stop if obstacle ahead. Wait for CMD_RESUME (handled in callback).
        """
        if not self._leader_alive():
            self.get_logger().warn("Leader lost while leading temp → SEARCHING")
            self._begin_search()
            self._transition(FollowerState.SEARCHING_FOR_LEADER)
            return

        if self._fwd_min() < LEADING_OBSTACLE_STOP:
            self._stop()
            return

        twist = Twist()
        twist.linear.x = LEADING_SPEED
        self.pub_cmd.publish(twist)

    def _s_searching(self) -> None:
        """
        Three-phase search:
          Phase 0: Drive toward last known leader position
          Phase 1: Rotate 360° in place
          Phase 2: Expanding square pattern

        Leader reappearance is caught by _cb_leader_status → transitions to APPROACHING.
        """
        if self._secs() > SEARCH_TIMEOUT:
            self.get_logger().error(
                "Search timeout (90s) — operator intervention required"
            )
            self._stop()
            return

        if not self.current_pose:
            return

        now = time.monotonic()

        if self.search_phase == 0:
            # ── Phase 0: Navigate to last known leader position ─────────
            dx = self.lkl_x - self.current_pose.pose.position.x
            dy = self.lkl_y - self.current_pose.pose.position.y
            dist = math.sqrt(dx * dx + dy * dy)
            if dist < 0.30:
                # Arrived at LKL — start rotating
                self.search_phase = 1
                self.search_phase_start = now
                return
            bearing = _norm_angle(math.atan2(dy, dx) - self.current_yaw)
            twist = Twist()
            twist.linear.x = float(min(APPROACH_SPEED, KP_LINEAR * dist))
            twist.angular.z = float(max(-MAX_ANGULAR, min(MAX_ANGULAR, KP_ANGULAR * bearing)))
            if self._fwd_min() < SAFETY_STOP:
                twist.linear.x = 0.0
            self.pub_cmd.publish(twist)

        elif self.search_phase == 1:
            # ── Phase 1: Rotate 360° ───────────────────────────────────
            if now - self.search_phase_start > ROTATE_PHASE_DURATION:
                self.search_phase = 2
                self.search_phase_start = now
                self.search_expand_step = 0
                return
            twist = Twist()
            twist.angular.z = float(MAX_ANGULAR * 0.5)
            self.pub_cmd.publish(twist)

        else:
            # ── Phase 2: Expanding square pattern ─────────────────────
            # Drive forward search_expand_len, turn 90°, repeat
            phase_duration = self.search_expand_len / (APPROACH_SPEED * 0.5)
            if now - self.search_phase_start > phase_duration:
                # Turn 90° left
                self.search_expand_step += 1
                if self.search_expand_step % 2 == 0:
                    self.search_expand_len += EXPAND_PHASE_STEP
                self.search_phase_start = now
                # Execute a quick 90° turn
                twist = Twist()
                twist.angular.z = float(MAX_ANGULAR * 0.6)
                self.pub_cmd.publish(twist)
                return

            twist = Twist()
            twist.linear.x = float(APPROACH_SPEED * 0.5)
            if self._fwd_min() < LEADING_OBSTACLE_STOP:
                twist.linear.x = 0.0
                twist.angular.z = float(MAX_ANGULAR * 0.5)
            self.pub_cmd.publish(twist)

    def _s_waiting(self) -> None:
        self._stop()

    # ================================================================
    # HELPERS
    # ================================================================

    def _start_backup(self) -> None:
        if self.current_pose:
            self.backup_start_x = self.current_pose.pose.position.x
            self.backup_start_y = self.current_pose.pose.position.y

    def _begin_search(self) -> None:
        self.search_phase = 0
        self.search_phase_start = time.monotonic()
        self.search_expand_len = EXPAND_PHASE_STEP
        self.search_expand_step = 0

    def _fwd_min(self) -> float:
        """Minimum LiDAR range in ±30° forward sector."""
        if self.latest_scan is None:
            return float("inf")
        n = len(self.latest_scan.ranges)
        sector = n // 12  # 30° each side
        indices = list(range(sector)) + list(range(n - sector, n))
        min_r = float("inf")
        for i in indices:
            r = self.latest_scan.ranges[i]
            if (
                self.latest_scan.range_min < r < self.latest_scan.range_max
                and math.isfinite(r)
            ):
                min_r = min(min_r, r)
        return min_r

    def _stop(self) -> None:
        self.pub_cmd.publish(Twist())

    def _transition(self, new: FollowerState) -> None:
        self.get_logger().info(f"  ↳ {self.state.name} → {new.name}")
        self.state = new
        self.state_entry_time = time.monotonic()

    def _secs(self) -> float:
        return time.monotonic() - self.state_entry_time

    def _leader_alive(self) -> bool:
        return (
            self.last_leader_time > 0
            and time.monotonic() - self.last_leader_time < LEADER_TIMEOUT
        )

    def _send(self, command: int, data: str = "") -> None:
        msg = CoordinationCommand()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.command = command
        msg.data = data
        self.pub_leader_cmd.publish(msg)

    def _publish_status(self) -> None:
        msg = RobotStatus()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.header.frame_id = "follower/base_footprint"
        msg.state = int(self.state)
        msg.state_name = self.state.name
        if self.current_pose:
            msg.x = self.current_pose.pose.position.x
            msg.y = self.current_pose.pose.position.y
            msg.heading = self.current_yaw
        msg.distance_to_other = self.leader_distance
        self.pub_status.publish(msg)


def main(args=None) -> None:
    rclpy.init(args=args)
    node = FollowerNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()

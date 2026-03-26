"""
follower_node_skeleton.py
==========================
MDE Step 3: Student Skeleton Code — Follower Robot Node

This file is the STUDENT TEMPLATE for the follower robot coordination node.
It provides the complete infrastructure (ROS2 plumbing, state enum, timer,
callbacks) but leaves the core state machine logic for students to implement.

=== HOW TO USE THIS FILE ===
1. Read the PlantUML statechart (models/statecharts/follower_statechart.puml)
2. Review the Uppaal model for expected behavior
3. Fill in every method marked with # TODO
4. Test in simulation first

=== STATE MACHINE ===
                          CMD_BACK_UP          backed_up
   INIT ──► APPROACHING ──► FOLLOWING ──► BACKING_UP ──► LEADING_TEMPORARILY
                ▲                │                                  │
                │         leader_lost                          CMD_RESUME
                │                ▼                                  │
                └──────── SEARCHING_FOR_LEADER ◄───────────────────┘
                         (on leader found)

=== KEY ALGORITHM: FOLLOWING ===
  The follower tracks the leader using a simple proportional controller:
    distance_error = current_distance - TARGET_DISTANCE (0.5m)
    v = Kp_v * distance_error     (approach if too far, slow if too close)
    bearing = atan2(dy, dx) to leader
    omega = Kp_w * bearing_error  (turn to face leader)

=== TOPICS ===
  Subscribe:
    /follower/scan      sensor_msgs/LaserScan
    /follower/odom      nav_msgs/Odometry
    /leader/status      RobotStatus
    /follower/command   CoordinationCommand  (from leader)

  Publish:
    /follower/cmd_vel   geometry_msgs/Twist
    /follower/status    RobotStatus
    /leader/command     CoordinationCommand  (to leader)
"""

import math
from enum import IntEnum
from typing import Optional

import rclpy
from rclpy.action import ActionClient
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy, DurabilityPolicy

from geometry_msgs.msg import Twist, PoseStamped
from nav_msgs.msg import Odometry
from sensor_msgs.msg import LaserScan

from nav2_msgs.action import NavigateToPose

from leader_follower_msgs.msg import RobotStatus, CoordinationCommand


# ============================================================
# STATE ENUM
# ============================================================

class FollowerState(IntEnum):
    """State machine states for the follower robot."""
    INIT = 0
    APPROACHING = 4
    FOLLOWING = 3
    BACKING_UP = 9
    LEADING_TEMPORARILY = 7
    SEARCHING_FOR_LEADER = 8
    WAITING_CMD = 10


# ============================================================
# CONSTANTS
# ============================================================

# Following control
TARGET_DISTANCE = 0.5          # Target gap to maintain (meters)
APPROACH_THRESHOLD = 0.7       # Transition APPROACHING → FOLLOWING
FAR_THRESHOLD = 1.5            # Transition FOLLOWING → APPROACHING
SAFETY_STOP_RANGE = 0.2        # Emergency stop if obstacle closer than this

# Controller gains
KP_LINEAR = 0.3                # Proportional gain for linear velocity
KP_ANGULAR = 0.8               # Proportional gain for angular velocity
MAX_LINEAR_VEL = 0.22          # TurtleBot3 Burger max forward speed
MAX_ANGULAR_VEL = 1.82         # TurtleBot3 Burger max angular speed

# Backup distance
BACKUP_DISTANCE = 1.5          # How far to back up when leader hits dead end (meters)
BACKUP_SPEED = -0.1            # Backward speed (m/s)

# Timeouts
LEADER_STATUS_TIMEOUT = 5.0    # No leader msg → assume lost
APPROACH_TIMEOUT = 60.0        # Max time to approach
SEARCH_TIMEOUT = 90.0          # Max time to search for leader

# Publish rates
STATUS_PUBLISH_HZ = 10.0       # Hz
HEARTBEAT_LOST_HZ = 0.5        # Hz for CMD_LOST_YOU broadcasts


class FollowerNode(Node):
    """
    Follower robot coordination node.

    Implements the 7-state state machine that follows the leader,
    handles dead-end recovery, and searches for lost leader.
    """

    def __init__(self):
        super().__init__("follower_node")

        # ---- State machine ----
        self.state = FollowerState.INIT
        self.state_entry_time = self.get_clock().now()

        # ---- Sensor data ----
        self.latest_scan: Optional[LaserScan] = None
        self.current_pose: Optional[PoseStamped] = None

        # ---- Leader tracking ----
        self.leader_status: Optional[RobotStatus] = None
        self.last_leader_msg_time: Optional[rclpy.time.Time] = None
        self.leader_distance: float = float("inf")
        self.leader_bearing: float = 0.0            # rad, relative to follower heading

        # ---- Last known leader position (for search) ----
        self.last_known_leader_x: float = 0.0
        self.last_known_leader_y: float = 0.0

        # ---- Backup tracking ----
        self.backup_start_x: float = 0.0
        self.backup_start_y: float = 0.0
        self.distance_backed_up: float = 0.0

        # ---- Pending command from leader ----
        self.pending_command: Optional[int] = None

        # ---- QoS ----
        sensor_qos = QoSProfile(
            reliability=ReliabilityPolicy.BEST_EFFORT,
            durability=DurabilityPolicy.VOLATILE,
            depth=5,
        )
        reliable_qos = QoSProfile(
            reliability=ReliabilityPolicy.RELIABLE,
            durability=DurabilityPolicy.VOLATILE,
            depth=10,
        )

        # ---- Subscribers ----
        self.scan_sub = self.create_subscription(
            LaserScan, "/follower/scan", self._scan_callback, sensor_qos
        )
        self.odom_sub = self.create_subscription(
            Odometry, "/follower/odom", self._odom_callback, sensor_qos
        )
        self.leader_status_sub = self.create_subscription(
            RobotStatus, "/leader/status", self._leader_status_callback, reliable_qos
        )
        self.leader_command_sub = self.create_subscription(
            CoordinationCommand,
            "/follower/command",
            self._command_from_leader_callback,
            reliable_qos,
        )

        # ---- Publishers ----
        self.cmd_vel_pub = self.create_publisher(Twist, "/follower/cmd_vel", 10)
        self.status_pub = self.create_publisher(RobotStatus, "/follower/status", reliable_qos)
        self.leader_cmd_pub = self.create_publisher(
            CoordinationCommand, "/leader/command", reliable_qos
        )

        # ---- Nav2 action client ----
        self._nav2_client = ActionClient(self, NavigateToPose, "/follower/navigate_to_pose")

        # ---- Timers ----
        self.create_timer(1.0 / STATUS_PUBLISH_HZ, self._state_machine_tick)
        self.create_timer(1.0 / HEARTBEAT_LOST_HZ, self._lost_heartbeat_tick)

        self.get_logger().info("FollowerNode initialized — state: INIT")

    # ===========================================================
    # SENSOR CALLBACKS (provided — do not modify)
    # ===========================================================

    def _scan_callback(self, msg: LaserScan) -> None:
        """Store latest LiDAR scan."""
        self.latest_scan = msg

    def _odom_callback(self, msg: Odometry) -> None:
        """Store current pose from odometry."""
        pose = PoseStamped()
        pose.header = msg.header
        pose.pose = msg.pose.pose
        self.current_pose = pose

    def _leader_status_callback(self, msg: RobotStatus) -> None:
        """Update leader tracking from status broadcasts."""
        self.leader_status = msg
        self.last_leader_msg_time = self.get_clock().now()

        # Remember last known position (for search)
        self.last_known_leader_x = msg.x
        self.last_known_leader_y = msg.y

        # Compute distance and bearing
        if self.current_pose is not None:
            dx = msg.x - self.current_pose.pose.position.x
            dy = msg.y - self.current_pose.pose.position.y
            self.leader_distance = math.sqrt(dx * dx + dy * dy)

            # Bearing relative to world frame
            world_bearing = math.atan2(dy, dx)

            # Robot's current heading (yaw from quaternion)
            q = self.current_pose.pose.orientation
            yaw = math.atan2(
                2.0 * (q.w * q.z + q.x * q.y),
                1.0 - 2.0 * (q.y * q.y + q.z * q.z),
            )
            # Relative bearing (positive = leader is to the left)
            self.leader_bearing = world_bearing - yaw
            # Normalize to [-pi, pi]
            self.leader_bearing = math.atan2(
                math.sin(self.leader_bearing), math.cos(self.leader_bearing)
            )

    def _command_from_leader_callback(self, msg: CoordinationCommand) -> None:
        """Handle commands from the leader robot."""
        self.get_logger().info(f"Received command from leader: {msg.command}")
        self.pending_command = msg.command

        if msg.command in (
            CoordinationCommand.CMD_DEAD_END,
            CoordinationCommand.CMD_BACK_UP,
        ):
            if self.state == FollowerState.FOLLOWING:
                self._transition_to(FollowerState.BACKING_UP)
                self._start_backup()

        elif msg.command == CoordinationCommand.CMD_RESUME:
            if self.state in (
                FollowerState.LEADING_TEMPORARILY,
                FollowerState.WAITING_CMD,
            ):
                self._transition_to(FollowerState.FOLLOWING)

        elif msg.command == CoordinationCommand.CMD_SEARCH_FOR_ME:
            if self.state != FollowerState.SEARCHING_FOR_LEADER:
                self._transition_to(FollowerState.SEARCHING_FOR_LEADER)

        elif msg.command == CoordinationCommand.CMD_I_AM_HERE:
            if self.state == FollowerState.SEARCHING_FOR_LEADER:
                # Parse leader position from data field "x,y"
                try:
                    x_str, y_str = msg.data.split(",")
                    self.last_known_leader_x = float(x_str)
                    self.last_known_leader_y = float(y_str)
                    self.get_logger().info(
                        f"Leader is at ({self.last_known_leader_x:.2f}, "
                        f"{self.last_known_leader_y:.2f})"
                    )
                except ValueError:
                    pass

    # ===========================================================
    # STATE MACHINE MAIN LOOP
    # ===========================================================

    def _state_machine_tick(self) -> None:
        """Called at 10 Hz. Dispatches to current state handler."""
        handlers = {
            FollowerState.INIT: self._handle_init,
            FollowerState.APPROACHING: self._handle_approaching,
            FollowerState.FOLLOWING: self._handle_following,
            FollowerState.BACKING_UP: self._handle_backing_up,
            FollowerState.LEADING_TEMPORARILY: self._handle_leading_temporarily,
            FollowerState.SEARCHING_FOR_LEADER: self._handle_searching,
            FollowerState.WAITING_CMD: self._handle_waiting,
        }
        handler = handlers.get(self.state)
        if handler:
            handler()

        self._publish_status()

    def _lost_heartbeat_tick(self) -> None:
        """Broadcast CMD_LOST_YOU while searching for leader."""
        if self.state == FollowerState.SEARCHING_FOR_LEADER:
            self._send_command_to_leader(CoordinationCommand.CMD_LOST_YOU)

    # ===========================================================
    # STATE HANDLERS — STUDENT EXERCISES
    # ===========================================================

    def _handle_init(self) -> None:
        """
        INIT state handler.

        Behavior:
        - Wait until leader_status has been received.
        - When received, transition to APPROACHING.
        - Stop motors while waiting.

        Hint: Check self.leader_status is not None.
        """
        # TODO: Stop robot
        # TODO: If self.leader_status is not None → transition to APPROACHING
        pass

    def _handle_approaching(self) -> None:
        """
        APPROACHING state handler.

        Behavior:
        - Navigate toward a point TARGET_DISTANCE behind the leader's pose.
        - Use Nav2 NavigateToPose for navigation (or a simple Twist controller).
        - Check leader_distance every tick; when ≤ APPROACH_THRESHOLD → FOLLOWING.
        - Check leader connectivity; if lost → SEARCHING_FOR_LEADER.
        - Check timeout (APPROACH_TIMEOUT); if exceeded → log warning.

        Goal computation (simple version without Nav2):
          - Use _compute_approach_goal() to get the target PoseStamped
          - Publish a Twist to drive toward it (bearing + distance control)

        On transition to FOLLOWING:
          - Send CMD_READY to leader

        Hint: Use self._leader_is_connected() to check connectivity.
              Use self.leader_bearing and self.leader_distance for control.
        """
        # TODO: Check leader connectivity → SEARCHING_FOR_LEADER
        # TODO: Check if close enough → FOLLOWING, send CMD_READY
        # TODO: Check timeout → warn
        # TODO: Otherwise: drive toward leader using proportional controller
        pass

    def _handle_following(self) -> None:
        """
        FOLLOWING state handler — the main operating mode.

        Control law (proportional controller):
          distance_error = leader_distance - TARGET_DISTANCE
          v = KP_LINEAR * distance_error
          omega = KP_ANGULAR * leader_bearing
          clamp v to [-MAX_LINEAR_VEL, MAX_LINEAR_VEL]
          clamp omega to [-MAX_ANGULAR_VEL, MAX_ANGULAR_VEL]

        Safety:
          - If forward obstacle (from LiDAR) < SAFETY_STOP_RANGE → v = 0

        State transitions:
          - leader_distance > FAR_THRESHOLD → APPROACHING
          - leader not connected (timeout) → SEARCHING_FOR_LEADER
          - CMD_DEAD_END / CMD_BACK_UP received (handled in callback) → BACKING_UP

        Hint: Use self.leader_bearing and self.leader_distance.
              Use _get_forward_min_range() for safety check.
        """
        # TODO: Check leader connectivity → SEARCHING_FOR_LEADER, send CMD_LOST_YOU
        # TODO: Check if leader too far → APPROACHING
        # TODO: Safety check: forward obstacle
        # TODO: Compute v and omega using proportional control
        # TODO: Clamp and publish Twist
        pass

    def _handle_backing_up(self) -> None:
        """
        BACKING_UP state handler.

        Behavior:
        - Drive backward at BACKUP_SPEED.
        - Track distance backed up using odometry.
        - When distance_backed_up ≥ BACKUP_DISTANCE:
            → Send CMD_BACKED_UP to leader
            → Transition to LEADING_TEMPORARILY

        Hint: Use self.backup_start_x, self.backup_start_y and current_pose
              to compute distance_backed_up.
              Call _start_backup() on entry to set these reference points.
        """
        # TODO: Publish backward Twist
        # TODO: Update distance_backed_up from current_pose
        # TODO: Check if backed up enough → send CMD_BACKED_UP, transition to LEADING_TEMPORARILY
        pass

    def _handle_leading_temporarily(self) -> None:
        """
        LEADING_TEMPORARILY state handler.

        Behavior:
        - Drive slowly forward (v = 0.05 m/s) to clear space for the leader.
        - Stop if forward obstacle detected (LiDAR < 0.4m).
        - CMD_RESUME (from leader) triggers FOLLOWING transition (handled in callback).
        - Leader connectivity lost → SEARCHING_FOR_LEADER.

        Hint: Check _get_forward_min_range() for obstacles.
        """
        # TODO: Check leader connectivity → SEARCHING_FOR_LEADER
        # TODO: Check forward obstacle → stop
        # TODO: Otherwise: publish slow forward Twist
        pass

    def _handle_searching(self) -> None:
        """
        SEARCHING_FOR_LEADER state handler.

        Search algorithm:
        1. Navigate to last_known_leader_x, last_known_leader_y.
        2. Rotate 360° in place.
        3. If still not found: execute an expanding square search.

        Transitions:
        - When leader_status received AND leader_distance ≤ FAR_THRESHOLD:
            → Transition to APPROACHING

        Timeout: SEARCH_TIMEOUT → log critical error

        Hint: This is the most complex handler. For the skeleton,
              just implement the timeout check and the leader-found transition.
              The navigation can use Nav2 or simple Twist commands.
        """
        # TODO: Check if leader found (leader_status received recently) → APPROACHING
        # TODO: Check timeout → critical error
        # TODO: Navigate toward last_known_leader position (simple: send Nav2 goal once)
        pass

    def _handle_waiting(self) -> None:
        """
        WAITING_CMD state handler.

        Behavior:
        - Stop motors.
        - Wait for next command (handled by callback).

        Hint: Just call _stop_robot() here.
        """
        # TODO: Stop robot
        pass

    # ===========================================================
    # HELPER METHODS (provided)
    # ===========================================================

    def _compute_approach_goal(self) -> Optional[PoseStamped]:
        """
        Compute the goal position: TARGET_DISTANCE behind the leader.

        Returns a PoseStamped in the map frame pointing at the position
        TARGET_DISTANCE behind the leader's current heading.
        """
        if self.leader_status is None:
            return None

        # Position TARGET_DISTANCE behind leader's heading
        leader_heading = self.leader_status.heading
        goal = PoseStamped()
        goal.header.stamp = self.get_clock().now().to_msg()
        goal.header.frame_id = "map"
        goal.pose.position.x = (
            self.leader_status.x - TARGET_DISTANCE * math.cos(leader_heading)
        )
        goal.pose.position.y = (
            self.leader_status.y - TARGET_DISTANCE * math.sin(leader_heading)
        )
        goal.pose.position.z = 0.0
        # Face the same direction as leader
        goal.pose.orientation.z = math.sin(leader_heading / 2.0)
        goal.pose.orientation.w = math.cos(leader_heading / 2.0)
        return goal

    def _start_backup(self) -> None:
        """Record entry position for backup distance tracking."""
        if self.current_pose is not None:
            self.backup_start_x = self.current_pose.pose.position.x
            self.backup_start_y = self.current_pose.pose.position.y
            self.distance_backed_up = 0.0

    def _get_forward_min_range(self) -> float:
        """Return minimum LiDAR range in ±30° forward sector."""
        if self.latest_scan is None:
            return float("inf")
        n = len(self.latest_scan.ranges)
        # Forward sector: indices centered on 0 (first and last 1/12th of array)
        sector_width = n // 12
        min_range = float("inf")
        indices = list(range(sector_width)) + list(range(n - sector_width, n))
        for i in indices:
            r = self.latest_scan.ranges[i]
            if self.latest_scan.range_min < r < self.latest_scan.range_max:
                min_range = min(min_range, r)
        return min_range

    def _stop_robot(self) -> None:
        """Publish zero velocity."""
        self.cmd_vel_pub.publish(Twist())

    def _transition_to(self, new_state: FollowerState) -> None:
        """Transition to new state and log it."""
        old = self.state
        self.state = new_state
        self.state_entry_time = self.get_clock().now()
        self.get_logger().info(f"State: {old.name} → {new_state.name}")

    def _seconds_in_state(self) -> float:
        """Return seconds since state entry."""
        return (self.get_clock().now() - self.state_entry_time).nanoseconds / 1e9

    def _leader_is_connected(self) -> bool:
        """Return True if leader message received recently."""
        if self.last_leader_msg_time is None:
            return False
        elapsed = (self.get_clock().now() - self.last_leader_msg_time).nanoseconds / 1e9
        return elapsed < LEADER_STATUS_TIMEOUT

    def _send_command_to_leader(self, command: int, data: str = "") -> None:
        """Publish a CoordinationCommand to the leader."""
        msg = CoordinationCommand()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.command = command
        msg.data = data
        self.leader_cmd_pub.publish(msg)

    def _publish_status(self) -> None:
        """Publish current follower status."""
        msg = RobotStatus()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.header.frame_id = "follower/base_footprint"
        msg.state = int(self.state)
        msg.state_name = self.state.name
        if self.current_pose:
            msg.x = self.current_pose.pose.position.x
            msg.y = self.current_pose.pose.position.y
            q = self.current_pose.pose.orientation
            msg.heading = math.atan2(
                2.0 * (q.w * q.z + q.x * q.y),
                1.0 - 2.0 * (q.y * q.y + q.z * q.z),
            )
        msg.distance_to_other = self.leader_distance
        self.status_pub.publish(msg)


def main(args=None):
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

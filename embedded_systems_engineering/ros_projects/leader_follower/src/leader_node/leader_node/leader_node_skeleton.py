"""
leader_node_skeleton.py
========================
MDE Step 3: Student Skeleton Code — Leader Robot Node

This file is the STUDENT TEMPLATE for the leader robot coordination node.
It provides the complete infrastructure (ROS2 plumbing, state enum, timer,
message callbacks) but leaves the core state machine logic for students
to implement.

=== HOW TO USE THIS FILE ===
1. Read the PlantUML statechart (models/statecharts/leader_statechart.puml)
   to understand the expected behavior.
2. Review the Uppaal model (models/uppaal/leader_follower.xml) for the
   abstract state transitions.
3. Fill in every method marked with # TODO.
4. Test in Gazebo simulation before deploying to real robot.

=== STATE MACHINE ===
                    ┌─────────────────────────────────────────┐
                    │                                         │
   start ──► INIT ──► WAITING_FOR_FOLLOWER ──► EXPLORING ────┤
                                               │      ▲      │
                                               ▼      │      │
                                            DEAD_END  │      │
                                               │      │      │
                                               ▼      │      │
                                            REVERSING─┘      │
                                                             │
                                      WAITING_FOR_LOST_FOLLOWER ◄─┘

=== TOPICS ===
  Subscribe:
    /leader/scan             sensor_msgs/LaserScan  — LiDAR data
    /leader/odom             nav_msgs/Odometry      — robot position
    /follower/status         RobotStatus            — follower state
    /leader/command          CoordinationCommand    — commands from follower

  Publish:
    /leader/cmd_vel          geometry_msgs/Twist    — motor commands
    /leader/status           RobotStatus            — own state broadcast
    /follower/command        CoordinationCommand    — commands to follower

  Nav2 Action Client:
    /leader/navigate_to_pose  nav2_msgs/NavigateToPose
"""

import math
from enum import IntEnum, auto
from typing import Optional

import rclpy
from rclpy.action import ActionClient
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy, DurabilityPolicy

from geometry_msgs.msg import Twist, PoseStamped
from nav_msgs.msg import Odometry
from sensor_msgs.msg import LaserScan
from std_msgs.msg import Header

from nav2_msgs.action import NavigateToPose

from leader_follower_msgs.msg import RobotStatus, CoordinationCommand


# ============================================================
# STATE ENUM
# ============================================================

class LeaderState(IntEnum):
    """State machine states for the leader robot."""
    INIT = 0
    WAITING_FOR_FOLLOWER = 1
    EXPLORING = 2
    DEAD_END = 5
    REVERSING = 6
    WAITING_FOR_LOST_FOLLOWER = 11


# ============================================================
# CONSTANTS (tune these parameters during testing)
# ============================================================

# Distance thresholds (meters)
FOLLOW_DISTANCE_OK = 1.0       # Max acceptable gap: follower close enough to start
FOLLOW_DISTANCE_FAR = 1.5      # Gap too large: leader should wait
DEAD_END_RANGE = 0.4           # LiDAR range below which we call it "blocked"

# Angular sectors for dead-end detection (degrees)
FORWARD_SECTOR_DEG = 30        # ±30° around heading = forward cone
SIDE_SECTOR_DEG = 60           # 60° each side

# Timeouts (seconds)
FOLLOWER_STATUS_TIMEOUT = 5.0  # No follower msg → assume lost
DEAD_END_WAIT_TIMEOUT = 15.0   # Max wait for follower to ack dead end
FOLLOWER_WAIT_TIMEOUT = 60.0   # Max wait for follower to approach
LOST_FOLLOWER_TIMEOUT = 120.0  # Max wait for follower to be found

# Control parameters
LINEAR_REVERSE_SPEED = -0.1    # m/s, backward
STATUS_PUBLISH_HZ = 10.0       # Hz for status topic
HEARTBEAT_HZ = 2.0             # Hz for I_AM_HERE broadcasts when lost


class LeaderNode(Node):
    """
    Leader robot coordination node.

    Implements the 6-state state machine coordinating the leader's
    SLAM exploration with follower robot synchronization.
    """

    def __init__(self):
        super().__init__("leader_node")

        # ---- State machine ----
        self.state = LeaderState.INIT
        self.state_entry_time = self.get_clock().now()

        # ---- Sensor data (filled by callbacks) ----
        self.latest_scan: Optional[LaserScan] = None
        self.current_pose: Optional[PoseStamped] = None   # from odom

        # ---- Follower tracking ----
        self.follower_status: Optional[RobotStatus] = None
        self.last_follower_msg_time: Optional[rclpy.time.Time] = None
        self.follower_distance: float = float("inf")

        # ---- Dead-end recovery ----
        self.dead_end_ack_received: bool = False
        self.backed_up_meters: float = 0.0
        self.entry_pose_at_dead_end: Optional[PoseStamped] = None

        # ---- QoS profiles ----
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
            LaserScan, "/leader/scan", self._scan_callback, sensor_qos
        )
        self.odom_sub = self.create_subscription(
            Odometry, "/leader/odom", self._odom_callback, sensor_qos
        )
        self.follower_status_sub = self.create_subscription(
            RobotStatus, "/follower/status", self._follower_status_callback, reliable_qos
        )
        self.follower_command_sub = self.create_subscription(
            CoordinationCommand,
            "/leader/command",
            self._command_from_follower_callback,
            reliable_qos,
        )

        # ---- Publishers ----
        self.cmd_vel_pub = self.create_publisher(Twist, "/leader/cmd_vel", 10)
        self.status_pub = self.create_publisher(RobotStatus, "/leader/status", reliable_qos)
        self.follower_cmd_pub = self.create_publisher(
            CoordinationCommand, "/follower/command", reliable_qos
        )

        # ---- Nav2 action client ----
        self._nav2_client = ActionClient(self, NavigateToPose, "/leader/navigate_to_pose")

        # ---- Timers ----
        # Main state machine loop at 10 Hz
        self.create_timer(1.0 / STATUS_PUBLISH_HZ, self._state_machine_tick)
        # Heartbeat when waiting for lost follower at 2 Hz
        self.create_timer(1.0 / HEARTBEAT_HZ, self._heartbeat_tick)

        self.get_logger().info("LeaderNode initialized — state: INIT")

    # ===========================================================
    # SENSOR CALLBACKS (provided — do not modify)
    # ===========================================================

    def _scan_callback(self, msg: LaserScan) -> None:
        """Store the latest LiDAR scan."""
        self.latest_scan = msg

    def _odom_callback(self, msg: Odometry) -> None:
        """Store current pose from odometry."""
        pose = PoseStamped()
        pose.header = msg.header
        pose.pose = msg.pose.pose
        self.current_pose = pose

    def _follower_status_callback(self, msg: RobotStatus) -> None:
        """Update follower tracking information."""
        self.follower_status = msg
        self.last_follower_msg_time = self.get_clock().now()
        if self.current_pose is not None:
            dx = msg.x - self.current_pose.pose.position.x
            dy = msg.y - self.current_pose.pose.position.y
            self.follower_distance = math.sqrt(dx * dx + dy * dy)

    def _command_from_follower_callback(self, msg: CoordinationCommand) -> None:
        """Handle coordination commands received from the follower."""
        self.get_logger().info(f"Received command from follower: {msg.command}")
        if msg.command == CoordinationCommand.CMD_READY:
            self._on_follower_ready()
        elif msg.command == CoordinationCommand.CMD_BACKED_UP:
            self.dead_end_ack_received = True
            self.get_logger().info("Follower backed up — can start reversing")
        elif msg.command == CoordinationCommand.CMD_LOST_YOU:
            self._on_follower_lost()
        elif msg.command == CoordinationCommand.CMD_FOUND_YOU:
            self._on_follower_found()

    # ===========================================================
    # STATE MACHINE MAIN LOOP
    # ===========================================================

    def _state_machine_tick(self) -> None:
        """
        Called at 10 Hz. Dispatches to the current state handler and
        publishes the status message.
        """
        # Dispatch to state handler
        handlers = {
            LeaderState.INIT: self._handle_init,
            LeaderState.WAITING_FOR_FOLLOWER: self._handle_waiting_for_follower,
            LeaderState.EXPLORING: self._handle_exploring,
            LeaderState.DEAD_END: self._handle_dead_end,
            LeaderState.REVERSING: self._handle_reversing,
            LeaderState.WAITING_FOR_LOST_FOLLOWER: self._handle_waiting_for_lost_follower,
        }
        handler = handlers.get(self.state)
        if handler:
            handler()

        # Publish current status
        self._publish_status()

    def _heartbeat_tick(self) -> None:
        """Broadcast I_AM_HERE when waiting for a lost follower."""
        if self.state == LeaderState.WAITING_FOR_LOST_FOLLOWER and self.current_pose:
            cmd = CoordinationCommand()
            cmd.header.stamp = self.get_clock().now().to_msg()
            cmd.command = CoordinationCommand.CMD_I_AM_HERE
            if self.current_pose:
                p = self.current_pose.pose.position
                cmd.data = f"{p.x:.3f},{p.y:.3f}"
            self.follower_cmd_pub.publish(cmd)

    # ===========================================================
    # STATE HANDLERS — STUDENT EXERCISES
    # ===========================================================

    def _handle_init(self) -> None:
        """
        INIT state handler.

        Behavior:
        - Wait for the follower to be ready (CMD_READY received via _on_follower_ready)
        - If the follower is already close (distance ≤ FOLLOW_DISTANCE_OK),
          transition directly to EXPLORING.
        - If the follower is far, transition to WAITING_FOR_FOLLOWER.

        Hint: Check self.follower_status and self.follower_distance.
              Use self._transition_to() to change state.
        """
        # TODO: Check if follower status has been received
        # TODO: If follower is close enough → _transition_to(EXPLORING)
        # TODO: If follower is far → _transition_to(WAITING_FOR_FOLLOWER)
        # TODO: If no follower status yet → stay in INIT, stop motors
        pass

    def _handle_waiting_for_follower(self) -> None:
        """
        WAITING_FOR_FOLLOWER state handler.

        Behavior:
        - Stop all motion (cmd_vel = zero).
        - Monitor follower_distance every tick.
        - When follower_distance ≤ FOLLOW_DISTANCE_OK → transition to EXPLORING.
        - If time in this state exceeds FOLLOWER_WAIT_TIMEOUT → transition to ERROR
          (for now just log a warning).

        Hint: Use self._seconds_in_state() to check timeout.
              Use self._stop_robot() to halt.
        """
        # TODO: Stop robot
        # TODO: Check follower_distance and transition if close enough
        # TODO: Check timeout and warn/transition on timeout
        pass

    def _handle_exploring(self) -> None:
        """
        EXPLORING state handler — the main working mode.

        Behavior (run every 100ms = 10 Hz):
        1. Check if follower is still connected (last msg < FOLLOWER_STATUS_TIMEOUT ago).
           If not → transition to WAITING_FOR_LOST_FOLLOWER.
        2. Check if follower is too far (distance > FOLLOW_DISTANCE_FAR).
           If so → stop and transition to WAITING_FOR_FOLLOWER.
        3. Check LiDAR for dead end using _is_dead_end().
           If dead end → send CMD_DEAD_END to follower, transition to DEAD_END.
        4. If all clear → continue navigating (send Nav2 frontier goal or keep moving).

        Hint: Navigation can be as simple as sending a constant forward velocity
              or using Nav2 navigate_to_pose goals for frontier-based exploration.
              For the skeleton, just implement the state transitions; navigation
              can be a simple forward Twist command.
        """
        # TODO: 1. Check follower connectivity timeout → WAITING_FOR_LOST_FOLLOWER
        # TODO: 2. Check follower distance → WAITING_FOR_FOLLOWER
        # TODO: 3. Check for dead end via _is_dead_end()
        #          If dead end: send CMD_DEAD_END, transition to DEAD_END
        # TODO: 4. Otherwise: publish a forward Twist (v=0.15 m/s)
        pass

    def _handle_dead_end(self) -> None:
        """
        DEAD_END state handler.

        Behavior:
        - Stop motors.
        - Periodically re-send CMD_DEAD_END to follower (every 2s).
        - Wait for dead_end_ack_received == True (set by _command_from_follower_callback
          when CMD_BACKED_UP is received).
        - If ack received → transition to REVERSING.
        - If timeout (DEAD_END_WAIT_TIMEOUT) → force transition to REVERSING anyway.

        Hint: Track when CMD_DEAD_END was last sent with self._dead_end_last_broadcast_time.
        """
        # TODO: Stop robot
        # TODO: Re-broadcast CMD_DEAD_END every 2 seconds
        # TODO: Check self.dead_end_ack_received → transition to REVERSING
        # TODO: Check timeout → transition to REVERSING
        pass

    def _handle_reversing(self) -> None:
        """
        REVERSING state handler.

        Behavior:
        - Drive backward at LINEAR_REVERSE_SPEED.
        - Monitor forward LiDAR sector: when the minimum range in the
          forward sector exceeds DEAD_END_RANGE * 2 (1.5× clearance),
          the path is clear.
        - Once path clear → stop, send CMD_RESUME to follower,
          transition back to EXPLORING.

        Hint: Use _get_sector_min_range() to check forward clearance.
              Reset dead_end_ack_received = False when entering REVERSING.
        """
        # TODO: Publish backward Twist
        # TODO: Check forward clearance
        # TODO: When clear: stop, send CMD_RESUME, transition to EXPLORING
        pass

    def _handle_waiting_for_lost_follower(self) -> None:
        """
        WAITING_FOR_LOST_FOLLOWER state handler.

        Behavior:
        - Stop all motion.
        - The _heartbeat_tick() broadcasts CMD_I_AM_HERE automatically.
        - Wait for follower to respond (CMD_FOUND_YOU triggers _on_follower_found()).
        - If timeout (LOST_FOLLOWER_TIMEOUT) → log critical error, emergency stop.

        Hint: This state mostly waits for _on_follower_found() to trigger.
              Just handle the timeout here.
        """
        # TODO: Stop robot
        # TODO: Check timeout → log critical error
        pass

    # ===========================================================
    # HELPER METHODS — provided, use these in your state handlers
    # ===========================================================

    def _is_dead_end(self) -> bool:
        """
        Detect dead end using LiDAR.

        Returns True if the forward sector is blocked AND there is no
        viable escape route to the left or right.

        Algorithm:
          - Forward sector (±FORWARD_SECTOR_DEG): all ranges < DEAD_END_RANGE
          - Left sector (60°-120°): all ranges < DEAD_END_RANGE
          - Right sector (240°-300°): all ranges < DEAD_END_RANGE
          - Dead end = forward blocked AND (left blocked OR right blocked)

        Uses: self.latest_scan (sensor_msgs/LaserScan)
        """
        if self.latest_scan is None:
            return False
        forward_min = self._get_sector_min_range(
            self.latest_scan, -FORWARD_SECTOR_DEG, FORWARD_SECTOR_DEG
        )
        left_min = self._get_sector_min_range(self.latest_scan, 60, 120)
        right_min = self._get_sector_min_range(self.latest_scan, 240, 300)

        forward_blocked = forward_min < DEAD_END_RANGE
        left_blocked = left_min < DEAD_END_RANGE
        right_blocked = right_min < DEAD_END_RANGE

        return forward_blocked and (left_blocked or right_blocked)

    def _get_sector_min_range(
        self, scan: LaserScan, angle_min_deg: float, angle_max_deg: float
    ) -> float:
        """
        Return the minimum range reading in the given angular sector.

        Parameters:
          scan:          LaserScan message
          angle_min_deg: sector start in degrees (0 = forward, CCW positive)
          angle_max_deg: sector end in degrees

        Returns minimum valid range in the sector, or inf if no valid readings.
        """
        angle_min_rad = math.radians(angle_min_deg)
        angle_max_rad = math.radians(angle_max_deg)

        min_range = float("inf")
        angle = scan.angle_min
        for r in scan.ranges:
            if angle_min_rad <= angle <= angle_max_rad:
                if scan.range_min < r < scan.range_max:
                    min_range = min(min_range, r)
            angle += scan.angle_increment
        return min_range

    def _stop_robot(self) -> None:
        """Publish zero velocity to stop the robot."""
        self.cmd_vel_pub.publish(Twist())

    def _transition_to(self, new_state: LeaderState) -> None:
        """Transition to a new state and reset the entry timer."""
        old = self.state
        self.state = new_state
        self.state_entry_time = self.get_clock().now()
        self.get_logger().info(f"State: {old.name} → {new_state.name}")

    def _seconds_in_state(self) -> float:
        """Return seconds elapsed since entering the current state."""
        elapsed = self.get_clock().now() - self.state_entry_time
        return elapsed.nanoseconds / 1e9

    def _follower_is_connected(self) -> bool:
        """Return True if follower status has been received recently."""
        if self.last_follower_msg_time is None:
            return False
        elapsed = self.get_clock().now() - self.last_follower_msg_time
        return elapsed.nanoseconds / 1e9 < FOLLOWER_STATUS_TIMEOUT

    def _send_command_to_follower(self, command: int, data: str = "") -> None:
        """Publish a CoordinationCommand to the follower."""
        msg = CoordinationCommand()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.command = command
        msg.data = data
        self.follower_cmd_pub.publish(msg)

    def _publish_status(self) -> None:
        """Publish the current robot status."""
        msg = RobotStatus()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.header.frame_id = "leader/base_footprint"
        msg.state = int(self.state)
        msg.state_name = self.state.name
        if self.current_pose:
            msg.x = self.current_pose.pose.position.x
            msg.y = self.current_pose.pose.position.y
            # Extract yaw from quaternion
            q = self.current_pose.pose.orientation
            msg.heading = math.atan2(
                2.0 * (q.w * q.z + q.x * q.y),
                1.0 - 2.0 * (q.y * q.y + q.z * q.z),
            )
        msg.distance_to_other = self.follower_distance
        self.status_pub.publish(msg)

    # ===========================================================
    # EVENT HANDLERS (called by _command_from_follower_callback)
    # ===========================================================

    def _on_follower_ready(self) -> None:
        """
        Called when CMD_READY is received from follower.
        If in INIT or WAITING_FOR_FOLLOWER, transition to EXPLORING.

        TODO: Implement this method.
        """
        # TODO: If state in (INIT, WAITING_FOR_FOLLOWER) → transition to EXPLORING
        pass

    def _on_follower_lost(self) -> None:
        """
        Called when CMD_LOST_YOU is received from follower.
        Transition to WAITING_FOR_LOST_FOLLOWER from any exploring state.

        TODO: Implement this method.
        """
        # TODO: If state is EXPLORING → transition to WAITING_FOR_LOST_FOLLOWER
        pass

    def _on_follower_found(self) -> None:
        """
        Called when CMD_FOUND_YOU is received from follower.
        Transition back to EXPLORING.

        TODO: Implement this method.
        """
        # TODO: If state is WAITING_FOR_LOST_FOLLOWER → transition to EXPLORING
        pass


def main(args=None):
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

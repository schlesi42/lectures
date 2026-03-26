"""
visualization_node.py
======================
Full implementation — Visualization Node

Subscribes to both robots' status topics and publishes a rich
MarkerArray to /visualization/markers for display in RViz2.

Markers published (id assignments):
  0  — Leader sphere (blue)
  1  — Follower sphere (orange)
  2  — Connection line between robots (colour = cooperation quality)
  3  — Leader state text label
  4  — Follower state text label
  5  — Leader velocity arrow
  6  — Follower velocity arrow
  7  — Leader heading arrow
  8  — Follower heading arrow
 10+ — Path history trail for leader  (10..10+TRAIL_LEN)
 60+ — Path history trail for follower (60..60+TRAIL_LEN)

Updates at 5 Hz.

Connection line colour key:
  Green  — both robots EXPLORING / FOLLOWING (normal)
  Yellow — one robot WAITING or APPROACHING
  Orange — dead-end recovery in progress
  Red    — one or both robots SEARCHING / ERROR
"""

import math
from collections import deque
from typing import Optional, Deque, Tuple

import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy, DurabilityPolicy

from builtin_interfaces.msg import Duration
from geometry_msgs.msg import Point, Vector3
from std_msgs.msg import ColorRGBA, Header
from visualization_msgs.msg import Marker, MarkerArray

from leader_follower_msgs.msg import RobotStatus, CoordinationCommand


# ── Constants ────────────────────────────────────────────────────────────────

TRAIL_LEN = 40           # Number of historical positions to show
TRAIL_SPHERE_SCALE = 0.04
ROBOT_SPHERE_SCALE = 0.20
TEXT_SCALE = 0.18
TEXT_Z_OFFSET = 0.40     # Place text above robot
ARROW_SCALE_X = 0.08
ARROW_SCALE_YZ = 0.04

VIZ_HZ = 5.0


# ── State colour mapping ─────────────────────────────────────────────────────

STATE_COLOURS = {
    # name fragment → (R, G, B)   [leader states]
    "EXPLORING": (0.0, 0.8, 0.2),
    "FOLLOWING": (0.0, 0.7, 0.9),
    "APPROACHING": (1.0, 0.9, 0.0),
    "WAITING_FOR_FOLLOWER": (1.0, 0.6, 0.0),
    "WAITING_FOR_LOST": (1.0, 0.3, 0.0),
    "DEAD_END": (1.0, 0.1, 0.0),
    "REVERSING": (0.8, 0.0, 0.8),
    "BACKING_UP": (0.9, 0.5, 0.0),
    "LEADING_TEMP": (0.2, 0.9, 0.6),
    "SEARCHING": (1.0, 0.0, 0.0),
    "WAITING_CMD": (0.8, 0.8, 0.0),
    "INIT": (0.5, 0.5, 0.5),
}


def _state_colour(state_name: str) -> Tuple[float, float, float]:
    for key, colour in STATE_COLOURS.items():
        if key in state_name:
            return colour
    return (0.5, 0.5, 0.5)


def _line_colour(
    leader_state: Optional[str], follower_state: Optional[str]
) -> Tuple[float, float, float]:
    """Choose connection-line colour based on combined robot states."""
    if leader_state is None or follower_state is None:
        return (0.3, 0.3, 0.3)
    if "SEARCHING" in (leader_state + follower_state) or "ERROR" in (leader_state + follower_state):
        return (1.0, 0.0, 0.0)
    if "DEAD_END" in leader_state or "REVERSING" in leader_state or "BACKING" in follower_state:
        return (1.0, 0.5, 0.0)
    if "WAITING" in (leader_state + follower_state) or "APPROACHING" in follower_state:
        return (1.0, 0.9, 0.0)
    if "EXPLORING" in leader_state and "FOLLOWING" in follower_state:
        return (0.0, 0.9, 0.2)
    return (0.6, 0.6, 0.6)


def _rgba(r: float, g: float, b: float, a: float = 1.0) -> ColorRGBA:
    c = ColorRGBA()
    c.r, c.g, c.b, c.a = r, g, b, a
    return c


def _point(x: float, y: float, z: float = 0.0) -> Point:
    p = Point()
    p.x, p.y, p.z = x, y, z
    return p


def _now_stamp(node: Node) -> Header:
    h = Header()
    h.stamp = node.get_clock().now().to_msg()
    h.frame_id = "map"
    return h


def _lifetime_secs(secs: float) -> Duration:
    d = Duration()
    d.sec = int(secs)
    d.nanosec = int((secs - int(secs)) * 1e9)
    return d


class VisualizationNode(Node):
    """Publishes rich MarkerArray for RViz2 display of both robots."""

    def __init__(self) -> None:
        super().__init__("visualization_node")

        rel_qos = QoSProfile(
            reliability=ReliabilityPolicy.RELIABLE,
            durability=DurabilityPolicy.VOLATILE,
            depth=10,
        )

        # ── Subscriptions ──────────────────────────────────────────────
        self.create_subscription(
            RobotStatus, "/leader/status", self._cb_leader, rel_qos
        )
        self.create_subscription(
            RobotStatus, "/follower/status", self._cb_follower, rel_qos
        )

        # ── Publishers ─────────────────────────────────────────────────
        self.pub_markers = self.create_publisher(
            MarkerArray, "/visualization/markers", rel_qos
        )

        # ── State cache ────────────────────────────────────────────────
        self.leader_status: Optional[RobotStatus] = None
        self.follower_status: Optional[RobotStatus] = None

        # ── Path history (deque of (x, y) tuples) ──────────────────────
        self.leader_trail: Deque[Tuple[float, float]] = deque(maxlen=TRAIL_LEN)
        self.follower_trail: Deque[Tuple[float, float]] = deque(maxlen=TRAIL_LEN)

        # ── Publish timer ──────────────────────────────────────────────
        self.create_timer(1.0 / VIZ_HZ, self._publish)

        self.get_logger().info("VisualizationNode ready")

    # ================================================================
    # CALLBACKS
    # ================================================================

    def _cb_leader(self, msg: RobotStatus) -> None:
        self.leader_status = msg
        self.leader_trail.append((msg.x, msg.y))

    def _cb_follower(self, msg: RobotStatus) -> None:
        self.follower_status = msg
        self.follower_trail.append((msg.x, msg.y))

    # ================================================================
    # MARKER CONSTRUCTION
    # ================================================================

    def _publish(self) -> None:
        markers = MarkerArray()
        h = _now_stamp(self)
        lt = _lifetime_secs(0.5)   # short lifetime → auto-disappear if stale

        # ── Leader sphere ──────────────────────────────────────────────
        if self.leader_status:
            ls = self.leader_status
            col = _state_colour(ls.state_name)
            markers.markers.append(
                self._sphere(h, lt, marker_id=0, x=ls.x, y=ls.y, z=0.10,
                             colour=_rgba(*col), scale=ROBOT_SPHERE_SCALE)
            )
            markers.markers.append(
                self._text(h, lt, marker_id=3,
                           x=ls.x, y=ls.y, z=TEXT_Z_OFFSET,
                           text=f"LEADER\n{ls.state_name}",
                           colour=_rgba(*col))
            )
            markers.markers.append(
                self._heading_arrow(h, lt, marker_id=7,
                                    x=ls.x, y=ls.y, yaw=ls.heading,
                                    colour=_rgba(0.0, 0.3, 1.0))
            )

        # ── Follower sphere ────────────────────────────────────────────
        if self.follower_status:
            fs = self.follower_status
            col = _state_colour(fs.state_name)
            markers.markers.append(
                self._sphere(h, lt, marker_id=1, x=fs.x, y=fs.y, z=0.10,
                             colour=_rgba(*col), scale=ROBOT_SPHERE_SCALE)
            )
            markers.markers.append(
                self._text(h, lt, marker_id=4,
                           x=fs.x, y=fs.y, z=TEXT_Z_OFFSET,
                           text=f"FOLLOWER\n{fs.state_name}",
                           colour=_rgba(*col))
            )
            markers.markers.append(
                self._heading_arrow(h, lt, marker_id=8,
                                    x=fs.x, y=fs.y, yaw=fs.heading,
                                    colour=_rgba(1.0, 0.5, 0.0))
            )

        # ── Connection line ────────────────────────────────────────────
        if self.leader_status and self.follower_status:
            ls, fs = self.leader_status, self.follower_status
            lname = ls.state_name if ls else ""
            fname = fs.state_name if fs else ""
            lc = _line_colour(lname, fname)
            line = Marker()
            line.header = h
            line.lifetime = lt
            line.ns = "connection"
            line.id = 2
            line.type = Marker.LINE_STRIP
            line.action = Marker.ADD
            line.scale.x = 0.03
            line.color = _rgba(*lc, 0.8)
            line.points = [_point(ls.x, ls.y, 0.05), _point(fs.x, fs.y, 0.05)]
            markers.markers.append(line)

            # Distance text (midpoint)
            mx = (ls.x + fs.x) / 2.0
            my = (ls.y + fs.y) / 2.0
            dist = math.sqrt((ls.x - fs.x) ** 2 + (ls.y - fs.y) ** 2)
            markers.markers.append(
                self._text(h, lt, marker_id=9,
                           x=mx, y=my, z=0.30,
                           text=f"{dist:.2f}m",
                           colour=_rgba(1.0, 1.0, 1.0),
                           scale=0.12)
            )

        # ── Leader trail ───────────────────────────────────────────────
        for i, (tx, ty) in enumerate(self.leader_trail):
            alpha = (i + 1) / TRAIL_LEN
            markers.markers.append(
                self._sphere(h, lt, marker_id=10 + i,
                             x=tx, y=ty, z=0.02,
                             colour=_rgba(0.0, 0.5, 1.0, alpha * 0.5),
                             scale=TRAIL_SPHERE_SCALE)
            )

        # ── Follower trail ─────────────────────────────────────────────
        for i, (tx, ty) in enumerate(self.follower_trail):
            alpha = (i + 1) / TRAIL_LEN
            markers.markers.append(
                self._sphere(h, lt, marker_id=60 + i,
                             x=tx, y=ty, z=0.02,
                             colour=_rgba(1.0, 0.5, 0.0, alpha * 0.5),
                             scale=TRAIL_SPHERE_SCALE)
            )

        self.pub_markers.publish(markers)

    # ================================================================
    # MARKER FACTORIES
    # ================================================================

    def _sphere(
        self, header: Header, lifetime: Duration,
        marker_id: int, x: float, y: float, z: float,
        colour: ColorRGBA, scale: float = ROBOT_SPHERE_SCALE,
    ) -> Marker:
        m = Marker()
        m.header = header
        m.lifetime = lifetime
        m.ns = "robots"
        m.id = marker_id
        m.type = Marker.SPHERE
        m.action = Marker.ADD
        m.pose.position = _point(x, y, z)
        m.pose.orientation.w = 1.0
        m.scale = Vector3(x=scale, y=scale, z=scale)
        m.color = colour
        return m

    def _text(
        self, header: Header, lifetime: Duration,
        marker_id: int, x: float, y: float, z: float,
        text: str, colour: ColorRGBA, scale: float = TEXT_SCALE,
    ) -> Marker:
        m = Marker()
        m.header = header
        m.lifetime = lifetime
        m.ns = "labels"
        m.id = marker_id
        m.type = Marker.TEXT_VIEW_FACING
        m.action = Marker.ADD
        m.pose.position = _point(x, y, z)
        m.pose.orientation.w = 1.0
        m.scale.z = scale
        m.color = colour
        m.text = text
        return m

    def _heading_arrow(
        self, header: Header, lifetime: Duration,
        marker_id: int, x: float, y: float, yaw: float,
        colour: ColorRGBA, length: float = 0.25,
    ) -> Marker:
        m = Marker()
        m.header = header
        m.lifetime = lifetime
        m.ns = "arrows"
        m.id = marker_id
        m.type = Marker.ARROW
        m.action = Marker.ADD
        m.scale.x = ARROW_SCALE_X
        m.scale.y = ARROW_SCALE_YZ
        m.scale.z = ARROW_SCALE_YZ
        m.color = colour
        # Arrow: start → end
        start = _point(x, y, 0.08)
        end = _point(
            x + length * math.cos(yaw),
            y + length * math.sin(yaw),
            0.08,
        )
        m.points = [start, end]
        return m


def main(args=None) -> None:
    rclpy.init(args=args)
    node = VisualizationNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()

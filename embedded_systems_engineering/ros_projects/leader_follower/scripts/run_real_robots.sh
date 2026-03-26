#!/usr/bin/env bash
# ============================================================
# run_real_robots.sh — Launch on real TurtleBot3 hardware
# ============================================================
# Prerequisites:
#   1. Both robots connected to same WiFi
#   2. Same ROS_DOMAIN_ID on all devices
#   3. TurtleBot3 bringup running on each robot's Raspberry Pi:
#
#      Leader Pi:
#        export TURTLEBOT3_MODEL=burger
#        export ROS_DOMAIN_ID=42
#        ros2 launch turtlebot3_bringup robot.launch.py namespace:=leader
#
#      Follower Pi:
#        export TURTLEBOT3_MODEL=burger
#        export ROS_DOMAIN_ID=42
#        ros2 launch turtlebot3_bringup robot.launch.py namespace:=follower
#
# Then run this script on the workstation.
# ============================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WS_DIR="$(dirname "$SCRIPT_DIR")"

if [ -z "${ROS_DISTRO:-}" ]; then
    echo "ERROR: ROS2 not sourced. Run:  source /opt/ros/humble/setup.bash"
    exit 1
fi

if [ -f "$WS_DIR/install/setup.bash" ]; then
    source "$WS_DIR/install/setup.bash"
else
    echo "ERROR: Workspace not built. Run:  ./scripts/build.sh"
    exit 1
fi

export TURTLEBOT3_MODEL=burger
export ROS_DOMAIN_ID=${ROS_DOMAIN_ID:-42}
export RMW_IMPLEMENTATION=${RMW_IMPLEMENTATION:-rmw_cyclonedds_cpp}

echo "=== Leader-Follower — Real Robots ==="
echo "ROS_DOMAIN_ID: $ROS_DOMAIN_ID"
echo "RMW: $RMW_IMPLEMENTATION"
echo ""
echo "Make sure both TurtleBot3 robots are running bringup!"
echo ""

ros2 launch simulation real_robot.launch.py open_rviz:=true

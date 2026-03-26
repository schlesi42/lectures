#!/usr/bin/env bash
# ============================================================
# build.sh — Build the Leader-Follower ROS2 workspace
# ============================================================
# Usage:  ./scripts/build.sh
# ============================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WS_DIR="$(dirname "$SCRIPT_DIR")"

echo "=== Leader-Follower Build ==="
echo "Workspace: $WS_DIR"

# Check ROS2 environment
if [ -z "${ROS_DISTRO:-}" ]; then
    echo "ERROR: ROS2 not sourced. Run:  source /opt/ros/humble/setup.bash"
    exit 1
fi
echo "ROS2 distro: $ROS_DISTRO"

# Set TurtleBot3 model
export TURTLEBOT3_MODEL=burger

cd "$WS_DIR"

# Build all packages
echo ""
echo "--- Building packages ---"
colcon build --symlink-install --packages-select \
    leader_follower_msgs \
    leader_node \
    follower_node \
    visualization_node \
    simulation

echo ""
echo "--- Build complete ---"
echo "Source the workspace:  source $WS_DIR/install/setup.bash"

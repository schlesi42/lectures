#!/usr/bin/env bash
# ============================================================
# run_simulation.sh — Launch the full Gazebo simulation
# ============================================================
# Usage:  ./scripts/run_simulation.sh
#
# This starts Gazebo, spawns both robots, launches SLAM, Nav2,
# the leader/follower coordination nodes, visualization, and RViz2.
# ============================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WS_DIR="$(dirname "$SCRIPT_DIR")"

# Check ROS2 environment
if [ -z "${ROS_DISTRO:-}" ]; then
    echo "ERROR: ROS2 not sourced. Run:  source /opt/ros/humble/setup.bash"
    exit 1
fi

# Source workspace
if [ -f "$WS_DIR/install/setup.bash" ]; then
    source "$WS_DIR/install/setup.bash"
else
    echo "ERROR: Workspace not built. Run:  ./scripts/build.sh"
    exit 1
fi

# Environment variables
export TURTLEBOT3_MODEL=burger
export RMW_IMPLEMENTATION=${RMW_IMPLEMENTATION:-rmw_cyclonedds_cpp}

echo "=== Leader-Follower Simulation ==="
echo "TurtleBot3 model: $TURTLEBOT3_MODEL"
echo "RMW: $RMW_IMPLEMENTATION"
echo ""
echo "Launching Gazebo + SLAM + Nav2 + behaviour nodes + RViz2..."
echo "This may take 15-20 seconds to fully start."
echo ""

ros2 launch simulation simulation.launch.py \
    use_sim_time:=true \
    open_rviz:=true

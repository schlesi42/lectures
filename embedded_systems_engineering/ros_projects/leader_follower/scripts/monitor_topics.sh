#!/usr/bin/env bash
# ============================================================
# monitor_topics.sh — Monitor ROS2 topics for debugging
# ============================================================
# Usage:  ./scripts/monitor_topics.sh [topic]
#
# Without arguments: lists all active topics.
# With argument:     echoes the specified topic.
#
# Examples:
#   ./scripts/monitor_topics.sh                       # list topics
#   ./scripts/monitor_topics.sh /leader/status        # watch leader status
#   ./scripts/monitor_topics.sh /follower/command      # watch follower commands
# ============================================================
set -euo pipefail

if [ -z "${ROS_DISTRO:-}" ]; then
    echo "ERROR: ROS2 not sourced."
    exit 1
fi

if [ $# -eq 0 ]; then
    echo "=== Active ROS2 Topics ==="
    ros2 topic list
    echo ""
    echo "--- Key topics ---"
    echo "  /leader/status         Leader state + pose (RobotStatus)"
    echo "  /follower/status       Follower state + pose (RobotStatus)"
    echo "  /follower/command      Leader → Follower commands"
    echo "  /leader/command        Follower → Leader commands"
    echo "  /leader/scan           Leader LiDAR"
    echo "  /follower/scan         Follower LiDAR"
    echo "  /leader/cmd_vel        Leader velocity commands"
    echo "  /follower/cmd_vel      Follower velocity commands"
    echo ""
    echo "Usage: $0 <topic_name>"
else
    echo "=== Monitoring: $1 ==="
    ros2 topic echo "$1"
fi

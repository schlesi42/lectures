"""
real_robot.launch.py
====================
Launch file for the Leader-Follower system on REAL TurtleBot3 Burger hardware.

Prerequisites:
  1. Both robots connected to the same WiFi network
  2. Same ROS_DOMAIN_ID on all devices (e.g., export ROS_DOMAIN_ID=42)
  3. export RMW_IMPLEMENTATION=rmw_cyclonedds_cpp on all devices
  4. TurtleBot3 packages installed: ros-humble-turtlebot3

Per-robot setup (run ON EACH ROBOT's Raspberry Pi):
  Leader Pi:
    export TURTLEBOT3_MODEL=burger
    export ROS_DOMAIN_ID=42
    export RMW_IMPLEMENTATION=rmw_cyclonedds_cpp
    ros2 launch turtlebot3_bringup robot.launch.py namespace:=leader

  Follower Pi:
    export TURTLEBOT3_MODEL=burger
    export ROS_DOMAIN_ID=42
    export RMW_IMPLEMENTATION=rmw_cyclonedds_cpp
    ros2 launch turtlebot3_bringup robot.launch.py namespace:=follower

Then on the workstation (this file):
  export ROS_DOMAIN_ID=42
  export RMW_IMPLEMENTATION=rmw_cyclonedds_cpp
  ros2 launch simulation real_robot.launch.py

This launch file starts:
  - SLAM toolbox for leader
  - Nav2 for both robots
  - leader_node and follower_node
  - visualization_node
  - RViz2
"""

import os

from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch.actions import (
    DeclareLaunchArgument,
    IncludeLaunchDescription,
    TimerAction,
)
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    # ----------------------------------------------------------------
    # Package directories
    # ----------------------------------------------------------------
    sim_pkg_dir = get_package_share_directory("simulation")
    nav2_bringup_pkg_dir = get_package_share_directory("nav2_bringup")

    # ----------------------------------------------------------------
    # Launch Arguments
    # ----------------------------------------------------------------
    open_rviz_arg = DeclareLaunchArgument(
        "open_rviz",
        default_value="true",
        description="Open RViz2 visualization",
    )

    open_rviz = LaunchConfiguration("open_rviz")

    # ----------------------------------------------------------------
    # SLAM Toolbox (leader only, real hardware mode)
    # ----------------------------------------------------------------
    slam_toolbox = Node(
        package="slam_toolbox",
        executable="async_slam_toolbox_node",
        name="slam_toolbox",
        namespace="leader",
        output="screen",
        parameters=[
            os.path.join(sim_pkg_dir, "config", "slam_params.yaml"),
            {"use_sim_time": False},
        ],
    )

    # ----------------------------------------------------------------
    # Nav2 for leader robot (real hardware: use_sim_time=false)
    # ----------------------------------------------------------------
    nav2_leader = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(nav2_bringup_pkg_dir, "launch", "navigation_launch.py")
        ),
        launch_arguments={
            "use_sim_time": "false",
            "namespace": "leader",
            "use_namespace": "true",
            "params_file": os.path.join(sim_pkg_dir, "config", "nav2_params.yaml"),
            "autostart": "true",
        }.items(),
    )

    # ----------------------------------------------------------------
    # Nav2 for follower robot (real hardware)
    # ----------------------------------------------------------------
    nav2_follower = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(nav2_bringup_pkg_dir, "launch", "navigation_launch.py")
        ),
        launch_arguments={
            "use_sim_time": "false",
            "namespace": "follower",
            "use_namespace": "true",
            "params_file": os.path.join(sim_pkg_dir, "config", "nav2_params.yaml"),
            "autostart": "true",
        }.items(),
    )

    # ----------------------------------------------------------------
    # Leader coordination node
    # ----------------------------------------------------------------
    leader_node = Node(
        package="leader_node",
        executable="leader_node",
        name="leader_node",
        namespace="leader",
        output="screen",
        parameters=[{"use_sim_time": False}],
    )

    # ----------------------------------------------------------------
    # Follower coordination node
    # ----------------------------------------------------------------
    follower_node = Node(
        package="follower_node",
        executable="follower_node",
        name="follower_node",
        namespace="follower",
        output="screen",
        parameters=[{"use_sim_time": False}],
    )

    # ----------------------------------------------------------------
    # Visualization node
    # ----------------------------------------------------------------
    visualization_node = Node(
        package="visualization_node",
        executable="visualization_node",
        name="visualization_node",
        output="screen",
        parameters=[{"use_sim_time": False}],
    )

    # ----------------------------------------------------------------
    # RViz2
    # ----------------------------------------------------------------
    rviz_node = Node(
        package="rviz2",
        executable="rviz2",
        name="rviz2",
        output="screen",
        arguments=[
            "-d", os.path.join(sim_pkg_dir, "rviz", "multi_robot.rviz")
        ],
        condition=IfCondition(open_rviz),
    )

    return LaunchDescription([
        open_rviz_arg,

        slam_toolbox,
        nav2_leader,
        nav2_follower,
        leader_node,
        follower_node,
        visualization_node,
        rviz_node,
    ])

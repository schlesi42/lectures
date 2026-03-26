"""
simulation.launch.py
====================
Master launch file for the Leader-Follower multi-robot simulation.

Launches:
  1. Gazebo Classic server + client (exploration_world.world)
  2. Robot State Publisher for /leader and /follower namespaces
  3. Spawn Leader TurtleBot3 Burger at (1.0, 0.0)
  4. Spawn Follower TurtleBot3 Burger at (-0.5, 0.0)
  5. SLAM Toolbox for the leader robot
  6. Nav2 bringup for both robots
  7. leader_node (coordination behavior)
  8. follower_node (coordination behavior)
  9. visualization_node (MarkerArray publisher)
 10. RViz2 with multi_robot.rviz config

Usage:
  export TURTLEBOT3_MODEL=burger
  export RMW_IMPLEMENTATION=rmw_cyclonedds_cpp
  ros2 launch simulation simulation.launch.py
"""

import os
import xacro

from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch.actions import (
    DeclareLaunchArgument,
    ExecuteProcess,
    IncludeLaunchDescription,
    RegisterEventHandler,
    TimerAction,
)
from launch.conditions import IfCondition
from launch.event_handlers import OnProcessExit
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import (
    Command,
    FindExecutable,
    LaunchConfiguration,
    PathJoinSubstitution,
    PythonExpression,
)
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    # ----------------------------------------------------------------
    # Package directories
    # ----------------------------------------------------------------
    sim_pkg_dir = get_package_share_directory("simulation")
    tb3_gazebo_pkg_dir = get_package_share_directory("turtlebot3_gazebo")
    nav2_bringup_pkg_dir = get_package_share_directory("nav2_bringup")

    # ----------------------------------------------------------------
    # Launch Arguments
    # ----------------------------------------------------------------
    use_sim_time_arg = DeclareLaunchArgument(
        "use_sim_time",
        default_value="true",
        description="Use simulation (Gazebo) clock if true",
    )
    open_rviz_arg = DeclareLaunchArgument(
        "open_rviz",
        default_value="true",
        description="Open RViz2 visualization",
    )
    world_arg = DeclareLaunchArgument(
        "world",
        default_value=os.path.join(sim_pkg_dir, "worlds", "exploration_world.world"),
        description="Full path to world file",
    )

    use_sim_time = LaunchConfiguration("use_sim_time")
    open_rviz = LaunchConfiguration("open_rviz")
    world = LaunchConfiguration("world")

    # ----------------------------------------------------------------
    # TurtleBot3 URDF (Burger model)
    # ----------------------------------------------------------------
    turtlebot3_urdf_file = os.path.join(
        get_package_share_directory("turtlebot3_description"),
        "urdf",
        "turtlebot3_burger.urdf",
    )

    # ----------------------------------------------------------------
    # 1. Gazebo
    # ----------------------------------------------------------------
    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(
                get_package_share_directory("gazebo_ros"), "launch", "gazebo.launch.py"
            )
        ),
        launch_arguments={
            "world": world,
            "verbose": "false",
        }.items(),
    )

    # ----------------------------------------------------------------
    # 2 & 3. Leader robot: state publisher + Gazebo spawn
    # ----------------------------------------------------------------
    leader_robot_state_publisher = Node(
        package="robot_state_publisher",
        executable="robot_state_publisher",
        name="robot_state_publisher",
        namespace="leader",
        output="screen",
        parameters=[
            {
                "use_sim_time": use_sim_time,
                "robot_description": Command(
                    [
                        FindExecutable(name="xacro"),
                        " ",
                        turtlebot3_urdf_file,
                        " ",
                        "frame_prefix:=leader/",
                    ]
                ),
            }
        ],
        remappings=[
            ("/tf", "tf"),
            ("/tf_static", "tf_static"),
        ],
    )

    spawn_leader = Node(
        package="gazebo_ros",
        executable="spawn_entity.py",
        arguments=[
            "-entity", "leader_tb3",
            "-topic", "/leader/robot_description",
            "-x", "1.0",
            "-y", "0.0",
            "-z", "0.01",
            "-Y", "0.0",
        ],
        output="screen",
    )

    # ----------------------------------------------------------------
    # 4 & 5. Follower robot: state publisher + Gazebo spawn
    # ----------------------------------------------------------------
    follower_robot_state_publisher = Node(
        package="robot_state_publisher",
        executable="robot_state_publisher",
        name="robot_state_publisher",
        namespace="follower",
        output="screen",
        parameters=[
            {
                "use_sim_time": use_sim_time,
                "robot_description": Command(
                    [
                        FindExecutable(name="xacro"),
                        " ",
                        turtlebot3_urdf_file,
                        " ",
                        "frame_prefix:=follower/",
                    ]
                ),
            }
        ],
        remappings=[
            ("/tf", "tf"),
            ("/tf_static", "tf_static"),
        ],
    )

    spawn_follower = Node(
        package="gazebo_ros",
        executable="spawn_entity.py",
        arguments=[
            "-entity", "follower_tb3",
            "-topic", "/follower/robot_description",
            "-x", "-0.5",
            "-y", "0.0",
            "-z", "0.01",
            "-Y", "0.0",
        ],
        output="screen",
    )

    # ----------------------------------------------------------------
    # 6. SLAM Toolbox (leader only)
    # ----------------------------------------------------------------
    slam_toolbox = Node(
        package="slam_toolbox",
        executable="async_slam_toolbox_node",
        name="slam_toolbox",
        namespace="leader",
        output="screen",
        parameters=[
            os.path.join(sim_pkg_dir, "config", "slam_params.yaml"),
            {"use_sim_time": use_sim_time},
        ],
        remappings=[
            ("/leader/scan", "/leader/scan"),
            ("/tf", "tf"),
            ("/tf_static", "tf_static"),
        ],
    )

    # ----------------------------------------------------------------
    # 7. Nav2 for leader robot
    # ----------------------------------------------------------------
    nav2_leader = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(nav2_bringup_pkg_dir, "launch", "navigation_launch.py")
        ),
        launch_arguments={
            "use_sim_time": use_sim_time,
            "namespace": "leader",
            "use_namespace": "true",
            "params_file": os.path.join(sim_pkg_dir, "config", "nav2_params.yaml"),
            "autostart": "true",
        }.items(),
    )

    # ----------------------------------------------------------------
    # 8. Nav2 for follower robot
    # ----------------------------------------------------------------
    nav2_follower = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(nav2_bringup_pkg_dir, "launch", "navigation_launch.py")
        ),
        launch_arguments={
            "use_sim_time": use_sim_time,
            "namespace": "follower",
            "use_namespace": "true",
            "params_file": os.path.join(sim_pkg_dir, "config", "nav2_params.yaml"),
            "autostart": "true",
        }.items(),
    )

    # ----------------------------------------------------------------
    # 9. Leader coordination node
    # ----------------------------------------------------------------
    leader_node = Node(
        package="leader_node",
        executable="leader_node",
        name="leader_node",
        namespace="leader",
        output="screen",
        parameters=[{"use_sim_time": use_sim_time}],
        remappings=[
            ("scan", "/leader/scan"),
            ("odom", "/leader/odom"),
            ("cmd_vel", "/leader/cmd_vel"),
        ],
    )

    # ----------------------------------------------------------------
    # 10. Follower coordination node
    # ----------------------------------------------------------------
    follower_node = Node(
        package="follower_node",
        executable="follower_node",
        name="follower_node",
        namespace="follower",
        output="screen",
        parameters=[{"use_sim_time": use_sim_time}],
        remappings=[
            ("scan", "/follower/scan"),
            ("odom", "/follower/odom"),
            ("cmd_vel", "/follower/cmd_vel"),
        ],
    )

    # ----------------------------------------------------------------
    # 11. Visualization node
    # ----------------------------------------------------------------
    visualization_node = Node(
        package="visualization_node",
        executable="visualization_node",
        name="visualization_node",
        output="screen",
        parameters=[{"use_sim_time": use_sim_time}],
    )

    # ----------------------------------------------------------------
    # 12. RViz2
    # ----------------------------------------------------------------
    rviz_node = Node(
        package="rviz2",
        executable="rviz2",
        name="rviz2",
        output="screen",
        arguments=[
            "-d", os.path.join(sim_pkg_dir, "rviz", "multi_robot.rviz")
        ],
        parameters=[{"use_sim_time": use_sim_time}],
        condition=IfCondition(open_rviz),
    )

    # ----------------------------------------------------------------
    # Launch with delay for Gazebo to load before spawning robots
    # ----------------------------------------------------------------
    delayed_spawn_leader = TimerAction(
        period=5.0,
        actions=[spawn_leader],
    )
    delayed_spawn_follower = TimerAction(
        period=6.0,
        actions=[spawn_follower],
    )
    delayed_slam = TimerAction(
        period=8.0,
        actions=[slam_toolbox],
    )
    delayed_nav2_leader = TimerAction(
        period=10.0,
        actions=[nav2_leader],
    )
    delayed_nav2_follower = TimerAction(
        period=10.0,
        actions=[nav2_follower],
    )
    delayed_behavior_nodes = TimerAction(
        period=15.0,
        actions=[leader_node, follower_node, visualization_node],
    )

    return LaunchDescription([
        use_sim_time_arg,
        open_rviz_arg,
        world_arg,

        # Gazebo
        gazebo,

        # Robot state publishers
        leader_robot_state_publisher,
        follower_robot_state_publisher,

        # Delayed spawns and nodes
        delayed_spawn_leader,
        delayed_spawn_follower,
        delayed_slam,
        delayed_nav2_leader,
        delayed_nav2_follower,
        delayed_behavior_nodes,

        # RViz
        rviz_node,
    ])

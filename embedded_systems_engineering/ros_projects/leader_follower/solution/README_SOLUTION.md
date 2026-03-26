# Leader-Follower Multi-Robot System — Full Solution

## Overview

This is the complete reference solution for the MDE (Model-Driven Engineering) lab
assignment. It includes all stages of the MDE workflow: modelling, formal verification,
implementation, simulation, and deployment scripts.

## Directory Structure

```
leader_follower/
├── models/                          # Stage 1-3: Models
│   ├── statecharts/
│   │   ├── leader_statechart.puml   # PlantUML statechart for the leader
│   │   └── follower_statechart.puml # PlantUML statechart for the follower
│   └── uppaal/
│       ├── leader_follower.xml      # Uppaal timed automata model (3 templates)
│       └── leader_follower.q        # 16 verification queries
│
├── src/                             # Stage 4: ROS2 Implementation
│   ├── leader_follower_msgs/        # Custom message definitions
│   │   └── msg/
│   │       ├── RobotStatus.msg      # Robot pose + state info
│   │       └── CoordinationCommand.msg  # Inter-robot commands
│   │
│   ├── leader_node/                 # Leader robot node
│   │   └── leader_node/
│   │       ├── leader_node.py       # FULL solution (539 lines)
│   │       └── leader_node_skeleton.py  # Student skeleton with TODOs
│   │
│   ├── follower_node/               # Follower robot node
│   │   └── follower_node/
│   │       ├── follower_node.py     # FULL solution (575 lines)
│   │       └── follower_node_skeleton.py  # Student skeleton with TODOs
│   │
│   ├── visualization_node/          # RViz2 marker publisher
│   │   └── visualization_node/
│   │       └── visualization_node.py  # State-colored markers + trails
│   │
│   └── simulation/                  # Gazebo simulation package
│       ├── launch/
│       │   ├── simulation.launch.py # Full simulation launch (Gazebo+SLAM+Nav2+nodes)
│       │   └── real_robot.launch.py # Real hardware launch
│       ├── worlds/
│       │   └── exploration_world.world  # 10x10m room with dead-end corridor
│       ├── config/
│       │   ├── slam_params.yaml     # SLAM Toolbox configuration
│       │   └── nav2_params.yaml     # Nav2 stack configuration
│       └── rviz/
│           └── multi_robot.rviz     # RViz2 display configuration
│
├── scripts/                         # Convenience scripts
│   ├── build.sh                     # Build the ROS2 workspace
│   ├── run_simulation.sh            # Launch Gazebo simulation
│   ├── run_real_robots.sh           # Launch on real TurtleBot3 hardware
│   ├── monitor_topics.sh            # Debug: list/echo ROS2 topics
│   └── clean.sh                     # Remove build artifacts
│
├── student_assignment.tex           # Original assignment document
├── student_assignment_v1.tex        # Revised assignment (more modelling freedom)
└── solution/
    └── README_SOLUTION.md           # This file
```

## Solution Details

### Stage 1-2: Statecharts (PlantUML)

**Leader Robot** — 6 states + ERROR:
- INIT → WAITING_FOR_FOLLOWER / EXPLORING (based on follower distance)
- EXPLORING → DEAD_END / WAITING_FOR_FOLLOWER / WAITING_FOR_LOST_FOLLOWER
- DEAD_END → REVERSING (on CMD_BACKED_UP or 15s timeout)
- REVERSING → EXPLORING (forward path clear, sends CMD_RESUME)
- WAITING_FOR_LOST_FOLLOWER → EXPLORING (on CMD_FOUND_YOU)

**Follower Robot** — 7 states + ERROR:
- INIT → APPROACHING (on first leader status)
- APPROACHING → FOLLOWING (distance ≤ 0.7m, sends CMD_READY)
- FOLLOWING → BACKING_UP (on CMD_DEAD_END) / SEARCHING (leader timeout)
- BACKING_UP → LEADING_TEMPORARILY (backed up 1.5m, sends CMD_BACKED_UP)
- LEADING_TEMPORARILY → FOLLOWING (on CMD_RESUME)
- SEARCHING_FOR_LEADER → APPROACHING (leader found, sends CMD_FOUND_YOU)

### Stage 3: Timed Automata (Uppaal)

Three templates in `models/uppaal/leader_follower.xml`:
- **LeaderRobot**: 7 locations (INIT through ERROR), clock `t`
- **FollowerRobot**: 8 locations (INIT through ERROR), clock `t`
- **Environment**: Non-deterministic event generator (obstacles, signal loss)

Key clock invariants:
| State                    | Invariant  |
|--------------------------|------------|
| WAITING_FOR_FOLLOWER     | t ≤ 60s    |
| DEAD_END                 | t ≤ 15s    |
| WAITING_FOR_LOST_FOLLOWER| t ≤ 120s   |
| SEARCHING_FOR_LEADER     | t ≤ 90s    |

**16 verification queries** in `leader_follower.q`:
- Safety: deadlock freedom, time bounds, state exclusion
- Reachability: normal operation, dead end, temporary leader
- Liveness: follower eventually follows, dead end recovery, search recovery
- Advanced: universal liveness (expected to fail due to ERROR states)

### Stage 4: ROS2 Implementation

**Communication Protocol:**

Leader → Follower (`/follower/command`):
| Command | Value | Meaning |
|---------|-------|---------|
| CMD_DEAD_END | 7 | Dead end detected, start backup |
| CMD_RESUME | 2 | Dead end cleared, resume following |
| CMD_I_AM_HERE | 6 | Heartbeat with pose (while lost) |

Follower → Leader (`/leader/command`):
| Command | Value | Meaning |
|---------|-------|---------|
| CMD_READY | 0 | Close enough, start exploring |
| CMD_LOST_YOU | 9 | Lost leader signal |
| CMD_FOUND_YOU | 10 | Found leader again |
| CMD_BACKED_UP | 11 | Finished backing up |

**Key Parameters:**

| Parameter | Leader | Follower |
|-----------|--------|----------|
| Follow distance OK | 1.0m | - |
| Follow distance FAR | 1.5m | 1.5m |
| Dead end range | 0.40m | - |
| Target distance | - | 0.50m |
| Approach threshold | - | 0.70m |
| Safety stop | - | 0.20m |
| Backup distance | - | 1.50m |
| Status timeout | 5.0s | 5.0s |

## Quick Start

### Prerequisites
- Ubuntu 22.04
- ROS2 Humble
- TurtleBot3 packages: `ros-humble-turtlebot3*`
- Nav2: `ros-humble-navigation2`
- SLAM Toolbox: `ros-humble-slam-toolbox`
- Gazebo Classic 11
- CycloneDDS: `ros-humble-rmw-cyclonedds-cpp`

### Build
```bash
source /opt/ros/humble/setup.bash
cd leader_follower
./scripts/build.sh
source install/setup.bash
```

### Run Simulation
```bash
./scripts/run_simulation.sh
```

### Monitor Topics
```bash
./scripts/monitor_topics.sh                 # list all topics
./scripts/monitor_topics.sh /leader/status  # watch leader state
```

### Run on Real Robots
```bash
# On each robot's Raspberry Pi first:
#   export TURTLEBOT3_MODEL=burger ROS_DOMAIN_ID=42
#   ros2 launch turtlebot3_bringup robot.launch.py namespace:=leader  (or follower)

# Then on the workstation:
./scripts/run_real_robots.sh
```

## Verification Query Results (Expected)

| # | Query | Expected |
|---|-------|----------|
| 1 | `A[] not deadlock` | SATISFIED |
| 2 | `E<> (Leader.EXPLORING and Follower.FOLLOWING)` | SATISFIED |
| 3 | `Follower.APPROACHING --> Follower.FOLLOWING` | SATISFIED |
| 4 | `Leader.DEAD_END --> Leader.EXPLORING` | SATISFIED |
| 5 | `Follower.SEARCHING --> Follower.APPROACHING` | SATISFIED |
| 6 | `E<> Leader.DEAD_END` | SATISFIED |
| 7 | `E<> Follower.LEADING_TEMPORARILY` | SATISFIED |
| 8 | No mutual timeout | SATISFIED |
| 9 | `WAITING_FOR_FOLLOWER imply t <= 60` | SATISFIED |
| 10 | `SEARCHING imply t <= 90` | SATISFIED |
| 11 | Progress from EXPLORING | SATISFIED |
| 12 | `A<> (Leader.EXPLORING and Follower.FOLLOWING)` | **NOT SATISFIED** (ERROR states) |

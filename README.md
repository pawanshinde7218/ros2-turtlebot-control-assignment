# ROS2 TurtleBot Control Assignment

## Overview

This repository contains the implementation of two ROS2 tasks focused on robot control, communication, and navigation.

The project demonstrates practical usage of:

- ROS2 Topics (Publisher/Subscriber)
- ROS2 Services
- ROS2 Actions
- Nav2 Navigation Stack
- Gazebo Simulation
- RViz Visualization
- Custom Service Interfaces

---

## Assignment Tasks

### Task 1: Topic-Based Velocity Controller

Implement a ROS2 node that:

- Subscribes to `/turtlebot/velocity`
- Receives velocity commands as `Float32MultiArray`
- Converts the received data into `geometry_msgs/Twist`
- Publishes the command to `/cmd_vel`
- Automatically stops the robot after 1 second

This demonstrates ROS2 topic communication and command forwarding.

---

### Task 2: Navigation Service

Implement a ROS2 service:

```text
/turtlebot/move_to_position
```

The service accepts:

```text
x
y
theta
```

and commands the robot to navigate to the requested target position using Nav2.

The service returns:

```text
True  -> Goal successfully reached
False -> Navigation failed
```

This demonstrates integration of:

- ROS2 Services
- ROS2 Actions
- Nav2 NavigateToPose Action Server

---

# System Architecture

## Task 1

```text
/turtlebot/velocity
        │
        ▼
velocity_forwarder_node
        │
        ▼
     /cmd_vel
        │
        ▼
      Robot
```

---

## Task 2

```text
RViz Publish Point
        │
        ▼
    goal_client
        │
        ▼
/turtlebot/move_to_position
        │
        ▼
navigation_service_server
        │
        ▼
NavigateToPose Action
        │
        ▼
       Nav2
        │
        ▼
      Robot
```

---

# Package Structure

```text
turtlebot_control/
│
├── launch/
│
├── scripts/
│   ├── velocity_forwarder.py
│   ├── goal_client.py
│   └── navigation_service_server.py
│
├── srv/
│   └── MoveToTarget.srv
│
├── package.xml
├── setup.py
└── README.md
```

---

# Custom Service Definition

```srv
float32 x
float32 y
float32 theta
---
bool success
```

---

# Implementation Details

## Velocity Forwarder Node

### Subscriber

Topic:

```text
/turtlebot/velocity
```

Message Type:

```text
std_msgs/Float32MultiArray
```

Expected Format:

```text
[data[0], data[1]]

data[0] -> Linear Velocity
data[1] -> Angular Velocity
```

Example:

```bash
ros2 topic pub --once \
/turtlebot/velocity \
std_msgs/msg/Float32MultiArray \
"{data:[0.2,0.0]}"
```

### Publisher

Topic:

```text
/cmd_vel
```

Message Type:

```text
geometry_msgs/Twist
```

Behavior:

- Receives velocity command
- Publishes to robot
- Waits 1 second
- Publishes zero velocity
- Robot stops

---

# Navigation Service

The navigation system consists of two nodes:

## Goal Client

Responsibilities:

- Subscribes to RViz clicked point
- Extracts target coordinates
- Creates service request
- Sends request to navigation service
- Displays navigation result

Subscribed Topic:

```text
/clicked_point
```

---

## Navigation Service Server

Responsibilities:

- Receives target position request
- Creates NavigateToPose goal
- Sends goal to Nav2
- Waits for navigation completion
- Returns final success status

Service:

```text
/turtlebot/move_to_position
```

Action:

```text
/navigate_to_pose
```

---

# Build Instructions

```bash
cd ~/TurtleBot_ws

colcon build --symlink-install

source install/setup.bash
```

---

# Running Task 1

### Terminal 1

Launch simulation:

```bash
ros2 launch turtlebot_control bringup.launch.py
```

### Terminal 2

Run velocity forwarding node:

```bash
ros2 run turtlebot_control velocity_forwarder.py
```

### Terminal 3

Publish velocity command:

```bash
ros2 topic pub --once \
/turtlebot/velocity \
std_msgs/msg/Float32MultiArray \
"{data:[0.2,0.0]}"
```

### Expected Result

- Robot moves forward
- Velocity command forwarded to `/cmd_vel`
- Robot automatically stops after 1 second

---

# Running Task 2

### Terminal 1

Launch robot and Nav2:

```bash
ros2 launch turtlebot_control nav2_bringup.launch.py
```

### Terminal 2

Run navigation service:

```bash
ros2 run turtlebot_control navigation_service_server.py
```

### Terminal 3

Run goal client:

```bash
ros2 run turtlebot_control goal_client.py
```

### RViz

Select:

```text
Publish Point
```

Click any valid location on the map.

### Expected Result

Client Output:

```text
Goal Client Started
Received Goal: x=4.17, y=4.83
Robot successfully reached target position
```

Server Output:

```text
Received Goal
Sending goal to Nav2
Goal accepted by Nav2
Navigation Succeeded
```

Nav2 Output:

```text
Reached the goal!
Goal succeeded
```

---

# Design Decisions

### Why Nav2 Action?

Navigation is a long-running task.

Using Nav2's `NavigateToPose` action allows:

- Goal management
- Feedback handling
- Result monitoring
- Reliable navigation execution

---

### Why MultiThreadedExecutor?

The service waits for the navigation result before responding.

A `MultiThreadedExecutor` is used to allow:

- Service callbacks
- Action callbacks

to execute concurrently without deadlocks.

---

### Why ReentrantCallbackGroup?

The navigation service internally communicates with an Action Server.

A `ReentrantCallbackGroup` allows nested callbacks to execute safely within the same node.

---

# Simulation Environment

For this assignment, a custom differential-drive robot model was used instead of TurtleBot3.

Reason:

- Existing Gazebo installation had version conflicts with TurtleBot3 simulation packages.
- The implemented ROS2 architecture remains identical to the assignment requirements.
- The solution is fully compatible with TurtleBot3 by remapping the same interfaces.

---

# Results

✅ Task 1 Completed

- Topic Subscription
- Topic Publishing
- Velocity Forwarding
- Timed Robot Stop

✅ Task 2 Completed

- Custom ROS2 Service
- Nav2 Action Integration
- Goal Navigation
- Success/Failure Response

---

# Future Improvements

### Goal Orientation Support

The current implementation accepts:

```text
x
y
theta
```

but only uses x and y for navigation.

Future work includes:

- Converting theta into quaternion orientation
- Passing orientation to Nav2
- Reaching target position with desired heading

---

### Navigation Feedback

Add continuous feedback such as:

- Remaining distance
- Estimated arrival time
- Current navigation state

---

### Goal Queue Management

Support multiple navigation requests and automatic goal scheduling.

---

# Demo

![Task 1](src/turtlebot_control/images/task1.png)

---

## Author

**Pawan Shinde**

Robotics Engineer | ROS2 Developer

GitHub: https://github.com/pawanshinde7218

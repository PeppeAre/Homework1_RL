# 🤖 Armando Robot Simulation - Robotics Lab 2025 Homework 1

This repository contains the **ROS 2 packages** required to simulate the 4-DOF *"Armando"* robotic arm, as part of the **Robotics Lab 2025 Homework 1**.

---

## 👥 Authors

- **Nicholas Ruggiero**  
- **Giuseppe Arena**

---

## 🧭 Overview

The project consists of **three main ROS 2 packages**:

### 1. `armando_description`
Contains:
- URDF (XACRO) models  
- Meshes  
- Rviz configurations  
- Launch file for visualization

### 2. `armando_gazebo`
Contains:
- Launch files and configurations to spawn the robot in the Gazebo simulator  
- Loads the `ros2_control` controllers

### 3. `armando_controller`
A **C++ node** that:
- Subscribes to `/joint_states`
- Sends sequential commands to the robot's joints

---

## ⚙️ Prerequisites

Make sure you have the following installed:

- **ROS 2 Humble** (or compatible)
- **ros2_control** framework
- **ros_gz_sim** (Gazebo simulator)
- **ros_gz_bridge** (ROS–Gazebo bridge)
- **xacro**

---

## 🏗️ How to Build

### 1. Clone the Repository
Clone this repository into your ROS 2 workspace's directory:

```bash
# Assuming your workspace is in ~/ros2_ws
cd ~/ros2_ws/src
git clone https://github.com/PeppeAre/Homework1_RL.git
```

---

### 2. Install Dependencies

Use `rosdep` to install missing dependencies:

```bash
cd ~/ros2_ws
rosdep install --from-paths src -y --ignore-src
```

---

### 3. Build the Workspace

Compile everything with `colcon`:

```bash
cd ~/ros2_ws
colcon build
```

---

## 🚀 How to Run (Usage)

Before running any launch file, **source the workspace** in every new terminal:

```bash
cd ~/ros2_ws
source install/setup.bash
```

---

### 🧩 Task 1: Visualization in Rviz

This launch file starts **Rviz** and the **joint_state_publisher_gui** to test the URDF model.

- **Launch file:** `armando_display.launch.py`

#### Command:
```bash
ros2 launch armando_description armando_display.launch.py
```

---

### ⚙️ Task 2, 3 & 4: Gazebo Simulation with Controllers

This is the **main launch file**.  
It starts **Gazebo**, spawns the robot, loads:
- The **camera plugin**
- The **ros2_control** drivers
- The **C++ controller node** (`arm_controller_node`)

- **Launch file:** `armando_world.launch.py`

This launch file also accepts a `controller_type` argument to select which controller to test, as required by **Task 4.d**.

#### ▶️ Run with Position Controller (Task 4.c)
```bash
ros2 launch armando_gazebo armando_world.launch.py controller_type:=position
```

#### ▶️ Run with Joint Trajectory Controller (Task 4.d)
```bash
ros2 launch armando_gazebo armando_world.launch.py controller_type:=trajectory
```
---

## 🧠 Notes
- Remember to always source your workspace before launching nodes.
- The controllers and motion sequences can be customized inside the `armando_controller` package.

---

**© Robotics Lab 2025 — Armando Project**

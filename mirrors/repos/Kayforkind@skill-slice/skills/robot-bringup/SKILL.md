---
name: robot-bringup
description: "Configures production ROS2 boot on Linux: systemd units, layered launch, udev stable device names, CycloneDDS/FastDDS discovery, watchdogs, and graceful actuator shutdown. Use when bringing up a robot stack, writing service units, or debugging boot-time races. Not for Nav2/SLAM algorithms, Gazebo simulation, or Windows-native ROS."
version: 1.0.1
risk: safe
source: modernized
date_modernized: "2026-05-31"
tags:
  - robotics
  - ros2
  - systemd
  - dds
  - deployment
  - linux
tools:
  - bash
  - ssh
---

## When to Use

Use this skill when the user needs to:

- Configure a robot to automatically start its full ROS2 stack on boot via systemd
- Write systemd unit files that correctly source ROS2 workspaces and set DDS environment
- Compose layered launch files (hardware, drivers, perception, application) into a single bringup
- Set up ordered startup with health checks to avoid race conditions between dependent nodes
- Write udev rules for deterministic device naming of cameras, LiDARs, and serial devices
- Configure CycloneDDS or FastDDS for multi-machine ROS2 discovery across robot and base station
- Implement watchdog and heartbeat monitoring for production robot systems
- Set up log rotation and structured logging for long-running robot deployments
- Write graceful shutdown handlers that bring actuators to a safe state before exit
- Debug boot-time failures, service ordering issues, or device enumeration races

Trigger keywords: `systemd`, `ros2 launch`, `bringup`, `udev`, `cyclonedds`, `fastdds`, `robot boot`, `service unit`, `watchdog`, `ROS_DOMAIN_ID`, `rmw`

## Prerequisites

- A Linux robot computer running systemd (Ubuntu 22.04+ or equivalent)
- ROS2 installed at `/opt/ros/${ROS_DISTRO}/` (tested with Humble and Jazzy)
- A colcon workspace at `/home/robot/ros2_ws/` with the robot's packages built
- Root or sudo access for installing systemd units and udev rules
- A dedicated `robot` system user (not root) for running the stack
- Network connectivity between robot and base station if multi-machine DDS is needed

### Create the robot user

```bash
sudo useradd -r -m -s /bin/bash robot
sudo usermod -aG dialout,video,plugdev robot
```

### Where the recipes live

This skill does not ship a companion pack. Use the Procedure sections in this file:

- udev rules for USB serial, cameras, LiDARs — Procedure 2
- CycloneDDS / FastDDS XML and multi-machine discovery — Procedure 4
- systemd hardening (`ProtectSystem`, `PrivateTmp`, capability bounding) — Procedure 6f
- `ExecStartPre` device verification — Procedure 5 (install as `/usr/local/bin/robot-device-check.sh`)
- deploy from a dev machine to the robot — Procedure 10

## Procedure

### 1. The Robot Bringup Stack

A production robot bringup follows a layered startup sequence from hardware initialization through application-level nodes. Each layer depends on the one below it.

```
                        APPLICATION LAYER
  Navigation, manipulation, mission planning, HRI

                        PERCEPTION LAYER
  Object detection, SLAM, point cloud filtering, sensor fusion

                         DRIVER LAYER
  Camera drivers, LiDAR drivers, motor controllers, IMU

                        HARDWARE LAYER
  udev rules, device enumeration, USB reset, firmware check

                      ROS2 ENVIRONMENT
  Source workspace, set RMW, ROS_DOMAIN_ID, DDS config

                    SYSTEMD TARGETS & SERVICES
  network-online.target  robot-hw.target  robot-bringup.target

                      LINUX BOOT (systemd)
  BIOS/UEFI  GRUB  kernel  systemd init

                         HARDWARE BOOT
  Power supply, onboard computer, peripherals
```

### 2. Write udev rules for deterministic device naming

Hardcoded paths like `/dev/ttyUSB0` are unreliable because USB enumeration order changes between reboots. Create stable symlinks under `/dev/robot/`.

```bash
# /etc/udev/rules.d/99-robot-devices.rules

# LiDAR (SLAMTEC RPLIDAR) — match by serial number
SUBSYSTEM=="tty", ATTRS{idVendor}=="10c4", ATTRS{idProduct}=="ea60", ATTRS{serial}=="0001", SYMLINK+="robot/lidar", MODE="0666", GROUP="dialout"

# IMU — match by serial number
SUBSYSTEM=="tty", ATTRS{idVendor}=="10c4", ATTRS{idProduct}=="ea60", ATTRS{serial}=="0002", SYMLINK+="robot/imu", MODE="0666", GROUP="dialout"

# Motor controller — match by serial number
SUBSYSTEM=="tty", ATTRS{idVendor}=="0403", ATTRS{idProduct}=="6001", ATTRS{serial}=="ABCD1234", SYMLINK+="robot/motors", MODE="0666", GROUP="dialout"

# USB camera — match by serial
SUBSYSTEM=="video4linux", ATTRS{idVendor}=="046d", ATTRS{idProduct}=="0825", ATTRS{serial}=="A1B2C3D4", SYMLINK+="robot/camera_front", MODE="0666", GROUP="video"
```

Apply and test:

```bash
sudo udevadm control --reload-rules
sudo udevadm trigger
ls -la /dev/robot/
```

### 3. Create the ROS2 environment file

systemd does not load `~/.bashrc` or `~/.profile`. Store environment variables in a dedicated file.

```bash
# /etc/robot/ros2.env
# ROS2 distribution
ROS_DISTRO=humble

# DDS middleware selection
RMW_IMPLEMENTATION=rmw_cyclonedds_cpp

# Domain isolation: unique per robot to avoid cross-talk
ROS_DOMAIN_ID=42

# CycloneDDS configuration file path
CYCLONEDDS_URI=file:///etc/robot/cyclonedds.xml

# Disable localhost-only mode for multi-machine setups
ROS_LOCALHOST_ONLY=0

# Logging configuration
ROS_LOG_DIR=/var/log/ros2
RCUTILS_LOGGING_USE_STDOUT=0
RCUTILS_COLORIZED_OUTPUT=0

# Robot-specific configuration
ROBOT_NAME=my_robot_01
ROBOT_CONFIG_DIR=/etc/robot/config
```

```bash
sudo mkdir -p /etc/robot
sudo nano /etc/robot/ros2.env
sudo mkdir -p /var/log/ros2
sudo chown robot:robot /var/log/ros2
```

### 4. Configure CycloneDDS for multi-machine discovery

```xml
<!-- /etc/robot/cyclonedds.xml -->
<?xml version="1.0" encoding="UTF-8" ?>
<CycloneDDS xmlns="https://cdds.io/config" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="https://cdds.io/config https://raw.githubusercontent.com/eclipse-cyclonedds/cyclonedds/master/etc/cyclonedds.xsd">
  <Domain id="any">
    <General>
      <Interfaces>
        <NetworkInterface name="eth0" />
      </Interfaces>
    </General>
    <Discovery>
      <Peers>
        <Peer address="192.168.1.100"/>  <!-- base station -->
        <Peer address="192.168.1.101"/>  <!-- robot onboard -->
      </Peers>
      <ParticipantIndex>auto</ParticipantIndex>
    </Discovery>
  </Domain>
</CycloneDDS>
```

### 5. Write the device check script

Write this `ExecStartPre` checker and install it as `/usr/local/bin/robot-device-check.sh`:

```bash
#!/usr/bin/env bash
# /usr/local/bin/robot-device-check.sh
# Exit non-zero if any critical device is missing — prevents driver startup race

set -euo pipefail

DEVICES=(
  "/dev/robot/camera_front"
  "/dev/robot/lidar"
  "/dev/robot/imu"
  "/dev/robot/motors"
)

for dev in "${DEVICES[@]}"; do
  if [[ ! -e "$dev" ]]; then
    echo "ERROR: Missing device $dev" >&2
    exit 1
  fi
  echo "OK: $dev present"
done

echo "All critical devices ready."
exit 0
```

```bash
sudo chmod +x /usr/local/bin/robot-device-check.sh
```

### 6. Write systemd service units

Place service files in `/etc/systemd/system/`. Split the stack into multiple services with explicit ordering for independent restart and failure isolation.

#### 6a. Hardware target

```ini
# /etc/systemd/system/robot-hw.target
[Unit]
Description=Robot Hardware Ready (udev devices enumerated)
After=network-online.target
Wants=network-online.target

[Install]
WantedBy=multi-user.target
```

#### 6b. Driver service

```ini
# /etc/systemd/system/robot-drivers.service
[Unit]
Description=Robot Hardware Drivers (cameras, LiDAR, IMU, motors)
After=network-online.target robot-hw.target
Wants=network-online.target
Requires=robot-hw.target

[Service]
Type=notify
User=robot
Group=robot
EnvironmentFile=/etc/robot/ros2.env
ExecStartPre=/usr/local/bin/robot-device-check.sh
ExecStart=/bin/bash -c '\
  source /opt/ros/${ROS_DISTRO}/setup.bash && \
  source /home/robot/ros2_ws/install/setup.bash && \
  exec ros2 launch my_robot_bringup drivers.launch.py'
ExecStop=/bin/kill -INT $MAINPID
TimeoutStopSec=20
Restart=on-failure
RestartSec=5
StartLimitIntervalSec=120
StartLimitBurst=5
WatchdogSec=30
KillMode=mixed
KillSignal=SIGINT
FinalKillSignal=SIGKILL
TimeoutStartSec=60
StandardOutput=journal
StandardError=journal
SyslogIdentifier=robot-drivers
OnFailure=robot-alert@%n.service

[Install]
WantedBy=robot-bringup.target
```

#### 6c. Perception service

```ini
# /etc/systemd/system/robot-perception.service
[Unit]
Description=Robot Perception Stack (SLAM, detection, sensor fusion)
After=robot-drivers.service
Requires=robot-drivers.service
PartOf=robot-drivers.service

[Service]
Type=notify
User=robot
Group=robot
EnvironmentFile=/etc/robot/ros2.env
ExecStart=/bin/bash -c '\
  source /opt/ros/${ROS_DISTRO}/setup.bash && \
  source /home/robot/ros2_ws/install/setup.bash && \
  exec ros2 launch my_robot_bringup perception.launch.py'
ExecStop=/bin/kill -INT $MAINPID
TimeoutStopSec=20
Restart=on-failure
RestartSec=5
StartLimitIntervalSec=120
StartLimitBurst=5
WatchdogSec=30
KillMode=mixed
KillSignal=SIGINT
FinalKillSignal=SIGKILL
StandardOutput=journal
StandardError=journal
SyslogIdentifier=robot-perception
OnFailure=robot-alert@%n.service

[Install]
WantedBy=robot-bringup.target
```

#### 6d. Application service

```ini
# /etc/systemd/system/robot-application.service
[Unit]
Description=Robot Application Layer (navigation, planning, HRI)
After=robot-perception.service
Requires=robot-perception.service
PartOf=robot-perception.service

[Service]
Type=notify
User=robot
Group=robot
EnvironmentFile=/etc/robot/ros2.env
ExecStart=/bin/bash -c '\
  source /opt/ros/${ROS_DISTRO}/setup.bash && \
  source /home/robot/ros2_ws/install/setup.bash && \
  exec ros2 launch my_robot_bringup application.launch.py'
ExecStop=/bin/kill -INT $MAINPID
TimeoutStopSec=20
Restart=on-failure
RestartSec=10
StartLimitIntervalSec=120
StartLimitBurst=5
WatchdogSec=30
KillMode=mixed
KillSignal=SIGINT
FinalKillSignal=SIGKILL
StandardOutput=journal
StandardError=journal
SyslogIdentifier=robot-application
OnFailure=robot-alert@%n.service

[Install]
WantedBy=robot-bringup.target
```

#### 6e. Bringup target (composes all layers)

```ini
# /etc/systemd/system/robot-bringup.target
[Unit]
Description=Robot Full Bringup Stack
After=network-online.target
Wants=network-online.target

[Install]
WantedBy=multi-user.target
```

#### 6f. Resource limits and hardening (optional drop-in)

```ini
# /etc/systemd/system/robot-drivers.service.d/limits.conf
[Service]
MemoryMax=2G
MemoryHigh=1800M
CPUQuota=300%
Nice=-5
IOSchedulingClass=realtime
IOSchedulingPriority=0
ProtectHome=read-only
ProtectSystem=strict
ReadWritePaths=/var/log/ros2 /tmp
PrivateTmp=true
```

### 7. Write layered launch files

Organize launch files into layers that mirror the systemd service architecture. Each layer is independently testable.

```
bringup.launch.py  (top-level: composes all layers)
  hardware.launch.py     (udev checks, device readiness)
  drivers.launch.py      (camera, LiDAR, IMU, motor drivers)
    camera.launch.py
    lidar.launch.py
    motors.launch.py
  perception.launch.py   (SLAM, detection, fusion)
    slam.launch.py
    detection.launch.py
  application.launch.py  (navigation, planning, HRI)
    navigation.launch.py
    mission.launch.py
```

#### 7a. Hardware layer launch

```python
# my_robot_bringup/launch/hardware.launch.py
from launch import LaunchDescription
from launch.actions import LogInfo, ExecuteProcess, TimerAction
from launch.substitutions import LaunchConfiguration, EnvironmentVariable

def generate_launch_description():
    robot_name = LaunchConfiguration('robot_name',
        default=EnvironmentVariable('ROBOT_NAME', default_value='default_robot'))

    check_camera = ExecuteProcess(
        cmd=['test', '-e', '/dev/robot/camera_front'],
        name='check_camera_front',
        output='screen',
    )

    check_lidar = ExecuteProcess(
        cmd=['test', '-e', '/dev/robot/lidar'],
        name='check_lidar',
        output='screen',
    )

    check_imu = ExecuteProcess(
        cmd=['test', '-e', '/dev/robot/imu'],
        name='check_imu',
        output='screen',
    )

    log_ready = TimerAction(
        period=2.0,
        actions=[LogInfo(msg='Hardware checks passed, devices ready')],
    )

    return LaunchDescription([
        check_camera,
        check_lidar,
        check_imu,
        log_ready,
    ])
```

#### 7b. Driver layer launch

```python
# my_robot_bringup/launch/drivers.launch.py
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare

def generate_launch_description():
    camera_node = Node(
        package='usb_cam',
        executable='usb_cam_node_exe',
        name='camera_front',
        parameters=[PathJoinSubstitution([
            FindPackageShare('my_robot_bringup'), 'config', 'camera_front.yaml'
        ])],
        remappings=[('/image_raw', '/camera/front/image_raw')],
    )

    lidar_node = Node(
        package='sllidar_ros2',
        executable='sllidar_node',
        name='lidar',
        parameters=[{
            'serial_port': '/dev/robot/lidar',
            'serial_baudrate': 460800,
            'frame_id': 'lidar_link',
            'angle_compensate': True,
        }],
    )

    imu_node = Node(
        package='imu_driver',
        executable='imu_node',
        name='imu',
        parameters=[{
            'port': '/dev/robot/imu',
            'frame_id': 'imu_link',
            'publish_rate': 100.0,
        }],
    )

    motor_node = Node(
        package='motor_driver',
        executable='motor_controller_node',
        name='motor_controller',
        parameters=[PathJoinSubstitution([
            FindPackageShare('my_robot_bringup'), 'config', 'motors.yaml'
        ])],
    )

    return LaunchDescription([
        DeclareLaunchArgument('use_sim', default_value='false'),
        DeclareLaunchArgument('camera_config', default_value='default'),
        camera_node,
        lidar_node,
        imu_node,
        motor_node,
    ])
```

#### 7c. Perception layer launch

```python
# my_robot_bringup/launch/perception.launch.py
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.conditions import IfCondition
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node, ComposableNodeContainer
from launch_ros.descriptions import ComposableNode
from launch_ros.substitutions import FindPackageShare

def generate_launch_description():
    enable_slam = LaunchConfiguration('enable_slam', default='true')
    enable_detection = LaunchConfiguration('enable_detection', default='true')

    perception_container = ComposableNodeContainer(
        name='perception_container',
        namespace='',
        package='rclcpp_components',
        executable='component_container_mt',
        composable_node_descriptions=[
            ComposableNode(
                package='image_proc',
                plugin='image_proc::RectifyNode',
                name='rectify',
                remappings=[('image', '/camera/front/image_raw')],
            ),
            ComposableNode(
                package='my_detection',
                plugin='my_detection::DetectorNode',
                name='detector',
                parameters=[PathJoinSubstitution([
                    FindPackageShare('my_robot_bringup'), 'config', 'detector.yaml'
                ])],
            ),
        ],
        condition=IfCondition(enable_detection),
    )

    slam_node = Node(
        package='slam_toolbox',
        executable='async_slam_toolbox_node',
        name='slam',
        parameters=[PathJoinSubstitution([
            FindPackageShare('my_robot_bringup'), 'config', 'slam.yaml'
        ])],
        condition=IfCondition(enable_slam),
    )

    return LaunchDescription([
        DeclareLaunchArgument('enable_slam', default_value='true'),
        DeclareLaunchArgument('enable_detection', default_value='true'),
        perception_container,
        slam_node,
    ])
```

#### 7d. Application layer launch

```python
# my_robot_bringup/launch/application.launch.py
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare

def generate_launch_description():
    nav_params = LaunchConfiguration('nav_params', default=PathJoinSubstitution([
        FindPackageShare('my_robot_bringup'), 'config', 'nav2_params.yaml'
    ]))

    nav2_bringup = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(PathJoinSubstitution([
            FindPackageShare('nav2_bringup'), 'launch', 'bringup_launch.py'
        ])),
        launch_arguments={
            'params_file': nav_params,
            'use_sim_time': LaunchConfiguration('use_sim', default='false'),
        }.items(),
    )

    mission_node = Node(
        package='my_mission',
        executable='mission_planner',
        name='mission_planner',
        parameters=[PathJoinSubstitution([
            FindPackageShare('my_robot_bringup'), 'config', 'mission.yaml'
        ])],
    )

    return LaunchDescription([
        DeclareLaunchArgument('nav_params', default_value=''),
        DeclareLaunchArgument('use_sim', default_value='false'),
        nav2_bringup,
        mission_node,
    ])
```

#### 7e. Top-level bringup launch

```python
# my_robot_bringup/launch/bringup.launch.py
from launch import LaunchDescription
from launch.actions import (
    DeclareLaunchArgument, IncludeLaunchDescription,
    GroupAction, LogInfo, TimerAction,
)
from launch.conditions import IfCondition, UnlessCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import (
    LaunchConfiguration, PathJoinSubstitution, PythonExpression,
)
from launch_ros.actions import PushRosNamespace
from launch_ros.substitutions import FindPackageShare

def generate_launch_description():
    pkg_share = FindPackageShare('my_robot_bringup')
    use_sim = LaunchConfiguration('use_sim')

    hardware_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution([pkg_share, 'launch', 'hardware.launch.py'])
        ),
        condition=UnlessCondition(use_sim),
    )

    drivers_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution([pkg_share, 'launch', 'drivers.launch.py'])
        ),
        condition=UnlessCondition(use_sim),
    )

    perception_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution([pkg_share, 'launch', 'perception.launch.py'])
        ),
    )

    application_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution([pkg_share, 'launch', 'application.launch.py'])
        ),
    )

    return LaunchDescription([
        DeclareLaunchArgument('use_sim', default_value='false'),
        hardware_launch,
        TimerAction(period=3.0, actions=[drivers_launch]),
        TimerAction(period=8.0, actions=[perception_launch]),
        TimerAction(period=15.0, actions=[application_launch]),
    ])
```

### 8. Implement graceful shutdown handlers

All actuator nodes must command a safe state before exit. Register signal handlers or use rclpy's shutdown callback.

```python
# GOOD: Shutdown handler commands safe state
def main():
    rclpy.init()
    node = MotorControlNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.command_zero_velocity()
        node.engage_brakes()
        node.destroy_node()
        rclpy.shutdown()
```

### 9. Configure log rotation

```bash
# /etc/logrotate.d/ros2
/var/log/ros2/*.log {
    daily
    rotate 14
    compress
    delaycompress
    missingok
    notifempty
    create 0644 robot robot
}
```

```ini
# /etc/systemd/journald.conf — add or modify:
SystemMaxUse=1G
MaxFileSec=1month
```

```bash
sudo systemctl restart systemd-journald
```

### 10. Deploy from dev machine to robot

Deploy with this workflow (save it in the project if you want to reuse it):

```bash
#!/usr/bin/env bash
# deploy-robot.sh — build locally, sync to robot, build on robot, restart services
set -euo pipefail

ROBOT_HOST="robot@192.168.1.101"
WORKSPACE="/home/robot/ros2_ws"
ROS_DISTRO="humble"

echo "=== Building bringup package locally ==="
source /opt/ros/${ROS_DISTRO}/setup.bash
colcon build --cmake-args -DCMAKE_BUILD_TYPE=Release --packages-select my_robot_bringup

echo "=== Syncing to robot ==="
rsync -avz --delete \
  --exclude='build/' --exclude='log/' \
  src/ "${ROBOT_HOST}:${WORKSPACE}/src/"

echo "=== Building on robot ==="
ssh "$ROBOT_HOST" "cd ${WORKSPACE} && \
  source /opt/ros/\${ROS_DISTRO}/setup.bash && \
  colcon build --cmake-args -DCMAKE_BUILD_TYPE=Release"

echo "=== Restarting robot services ==="
ssh "$ROBOT_HOST" 'sudo systemctl restart robot-bringup.target'

echo "=== Checking service status ==="
ssh "$ROBOT_HOST" 'sleep 3 && systemctl status robot-bringup.target --no-pager'

echo "Deploy complete."
```

### 11. Enable and start services

```bash
sudo systemctl daemon-reload
sudo systemctl enable robot-hw.target robot-bringup.target
sudo systemctl enable robot-drivers.service robot-perception.service robot-application.service
sudo systemctl start robot-bringup.target
```

## Pitfalls

### 1. Sourcing setup.bash in .bashrc for systemd

systemd services do not load `~/.bashrc` or `~/.profile`. Environment variables set there are invisible to the service, causing "command not found" or missing package errors. Always use `EnvironmentFile=/etc/robot/ros2.env` in the service unit and source explicitly in `ExecStart`.

### 2. No startup ordering

Starting all ROS2 nodes simultaneously causes race conditions. A navigation node may attempt to call a service that has not yet been advertised by the driver. Always use `After=` and `Requires=` in systemd units, or use a lifecycle manager to enforce ordered transitions.

### 3. Using Restart=always without rate limiting

A service that crashes on startup (missing config, hardware disconnected) will restart in a tight loop, consuming CPU and flooding the journal. Always set `StartLimitIntervalSec=120` and `StartLimitBurst=5` alongside `Restart=on-failure`.

### 4. Relying on network.target instead of network-online.target

`network.target` is reached as soon as network configuration starts, not when connectivity is established. DDS discovery fails because the network interface has no IP yet. Always use `After=network-online.target` and `Wants=network-online.target`. Ensure `systemd-networkd-wait-online.service` or `NetworkManager-wait-online.service` is enabled.

### 5. No log rotation

ROS2 log files in `~/.ros/log/` and journal entries grow without limit, eventually filling the disk on embedded systems. Configure logrotate for `$ROS_LOG_DIR` and set `SystemMaxUse=1G` in journald.conf.

### 6. Hardcoded device paths (/dev/ttyUSB0)

`/dev/ttyUSB0` can be assigned to any USB serial device depending on enumeration order. After a reboot, the IMU might become `/dev/ttyUSB1` and the motor controller `/dev/ttyUSB0`, reversing the mapping. Always use udev rules to create stable symlinks under `/dev/robot/`.

### 7. Running the entire stack as root

Running ROS2 as root is a security risk and causes permission issues with rosbag2, log files, and parameter persistence. Create a dedicated `robot` user and grant only necessary device permissions via udev `GROUP` and `MODE` rules. Set `User=robot` and `Group=robot` in every service unit.

### 8. No graceful shutdown handler

When systemd sends `SIGTERM` or `SIGINT`, a node without a shutdown handler exits immediately without commanding zero velocity or engaging brakes. The robot may coast or continue moving with the last commanded velocity. Always register signal handlers that command a safe state in the `finally` block before `rclpy.shutdown()`.

### 9. WatchdogSec without sd_notify in the node

Setting `WatchdogSec=30` in the service unit requires the ROS2 process to call `sd_notify(WATCHDOG=1)` within that interval. If the node does not implement this, systemd will kill and restart it repeatedly. Either implement sd_notify in the node or remove `WatchdogSec` and rely on `Restart=on-failure` alone.

### 10. PartOf without Requires

`PartOf=` creates a stop/restart dependency but does not create a start dependency. If you want a service to start when its parent starts, you also need `Requires=` (or `Wants=` for optional). Using only `PartOf=` means stopping the parent stops the child, but starting the parent does not start the child.

## Verification

### Verify udev rules

```bash
# Reload and trigger udev
sudo udevadm control --reload-rules
sudo udevadm trigger

# Check symlinks exist
ls -la /dev/robot/
# Expected output:
#   lrwxrwxrwx ... /dev/robot/camera_front -> ../video0
#   lrwxrwxrwx ... /dev/robot/lidar -> ../ttyUSB0
#   lrwxrwxrwx ... /dev/robot/imu -> ../ttyUSB1
#   lrwxrwxrwx ... /dev/robot/motors -> ../ttyUSB2
```

### Verify environment file

```bash
# Check that systemd can parse the env file
systemd-analyze verify /etc/robot/ros2.env 2>&1 || true

# Verify variables are loaded in a service context
sudo systemctl show robot-drivers.service -p Environment
# Expected: Environment=ROS_DISTRO=humble RMW_IMPLEMENTATION=rmw_cyclonedds_cpp ROS_DOMAIN_ID=42 ...
```

### Verify service unit syntax

```bash
sudo systemd-analyze verify /etc/systemd/system/robot-*.service /etc/systemd/system/robot-*.target
# Expected: no output (no errors)
```

### Verify service ordering

```bash
systemctl list-dependencies robot-bringup.target
# Expected: shows robot-drivers.service, robot-perception.service, robot-application.service
```

### Verify services are running

```bash
sudo systemctl status robot-bringup.target
# Expected: active (running)

sudo systemctl status robot-drivers.service
# Expected: active (running), with "Started Robot Hardware Drivers" in log

sudo systemctl status robot-perception.service
# Expected: active (running), with "Started Robot Perception Stack" in log

sudo systemctl status robot-application.service
# Expected: active (running), with "Started Robot Application Layer" in log
```

### Verify ROS2 topics are publishing

```bash
source /opt/ros/humble/setup.bash
source /home/robot/ros2_ws/install/setup.bash
export ROS_DOMAIN_ID=42
export RMW_IMPLEMENTATION=rmw_cyclonedds_cpp

ros2 topic list
# Expected: /camera/front/image_raw, /scan, /imu/data, /cmd_vel, /tf, etc.

ros2 topic hz /scan
# Expected: non-zero Hz (e.g., "average rate: 10.001")

ros2 node list
# Expected: /camera_front, /lidar, /imu, /motor_controller, /slam, /detector, /mission_planner
```

### Verify DDS discovery across machines

```bash
# On the base station, verify it can see robot nodes
ros2 daemon start
ros2 node list
# Expected: should show robot nodes if ROS_DOMAIN_ID and DDS config match
```

### Verify graceful shutdown

```bash
# Stop the application service and verify actuators go to safe state
sudo systemctl stop robot-application.service
# Check journal for zero-velocity / brake engagement messages
journalctl -u robot-application.service -n 20 --no-pager
# Expected: logs showing "Commanding zero velocity" and "Brakes engaged" before exit
```

### Verify boot-time startup (full integration test)

```bash
# Power cycle the robot and verify the full stack comes up
sudo reboot
# After reboot, SSH in and check:
systemctl is-active robot-bringup.target
# Expected: active

systemctl is-active robot-drivers.service robot-perception.service robot-application.service
# Expected: active active active

# Check for any failed services
systemctl --failed
# Expected: no robot-* services listed
```

### Verify log rotation is working

```bash
# Check journald disk usage
journalctl --disk-usage
# Expected: should be under 1G

# Check logrotate config is valid
sudo logrotate -d /etc/logrotate.d/ros2
# Expected: "rotating pattern" and no errors
```

## Robot Bringup Checklist

1. **udev rules written and tested** for all USB devices with stable symlinks under `/dev/robot/`
2. **systemd service units created** for each layer with correct `After=`/`Requires=` ordering
3. **ROS2 environment file** (`/etc/robot/ros2.env`) configured with `ROS_DISTRO`, `RMW_IMPLEMENTATION`, `ROS_DOMAIN_ID`, and `CYCLONEDDS_URI`
4. **CycloneDDS or FastDDS XML** configured with explicit peer list for multi-machine discovery
5. **Launch files layered and composable** with conditional arguments for sim/real and robot variants
6. **Health check scripts** written for `ExecStartPre` to verify device presence before starting drivers
7. **Watchdog integration** configured: `WatchdogSec` in service units and `sd_notify(WATCHDOG=1)` in the ROS2 process
8. **Heartbeat monitor node** deployed to detect node failures and trigger safe stop
9. **Graceful shutdown handlers** registered in all actuator nodes (zero velocity, engage brakes on `SIGINT`/`SIGTERM`)
10. **Log rotation configured** via logrotate for `$ROS_LOG_DIR` and journald `SystemMaxUse` limits
11. **Restart policies rate-limited** with `StartLimitIntervalSec` and `StartLimitBurst` to prevent restart loops
12. **Resource limits set** via `MemoryMax`, `CPUQuota` to prevent runaway nodes from starving the system
13. **Network and firewall configured** with static IPs, DDS port rules, and `ROS_LOCALHOST_ONLY` set correctly
14. **Full boot test performed** from power-off to autonomous operation, verifying service ordering and recovery from simulated failures

## Related Skills

- `ros2-launch` — Writing and debugging ROS2 launch files
- `dds-config` — CycloneDDS and FastDDS configuration for multi-robot fleets
- `systemd-services` — General systemd service unit authoring and hardening
- `robot-safety` — Safety interlocks, e-stops, and watchdog patterns for production robots

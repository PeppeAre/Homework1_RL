import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, RegisterEventHandler, DeclareLaunchArgument
from launch.event_handlers import OnProcessExit
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
import xacro

from launch.substitutions import LaunchConfiguration
from launch.actions import OpaqueFunction
from launch.conditions import IfCondition, UnlessCondition
from launch.substitutions import LaunchConfiguration, PythonExpression


def generate_launch_description():

    declare_controller_type_arg = DeclareLaunchArgument(
        'controller_type',
        default_value='position',
        description="Tipo di controller da usare: 'position' o 'trajectory'"
    )
    controller_type = LaunchConfiguration('controller_type')

    pkg_armando_description = get_package_share_directory('armando_description')
    urdf_file_path = os.path.join(pkg_armando_description, 'urdf', 'arm.urdf.xacro')
    robot_description_config = xacro.process_file(urdf_file_path)
    robot_desc = robot_description_config.toxml()

    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(get_package_share_directory('ros_gz_sim'), 'launch', 'gz_sim.launch.py')
        ),
        launch_arguments={'gz_args': '-r empty.sdf'}.items()
    )

    node_robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        output='screen',
        parameters=[{'robot_description': robot_desc, 'use_sim_time': True}]
    )

    spawn_entity = Node(
        package='ros_gz_sim',
        executable='create',
        arguments=['-topic', 'robot_description',
                   '-entity', 'armando', 
                   '-x', '0',
                   '-y', '0',
                   '-z', '0.1'],
        output='screen'
    )

    # --- BLOCCO CONTROLLER (PUNTO 4e) ---
    
    # Spawner per il JointStateBroadcaster
    spawn_joint_state_broadcaster = Node(
        package='controller_manager',
        executable='spawner',
        arguments=['joint_state_broadcaster', '--controller-manager', '/armando_controller_manager'],
        output='screen'
    )

    # Spawner per il SimplePositionController (Punto 4c)
    # Caricato solo se controller_type == 'position'
    spawn_simple_position_controller = Node(
        package='controller_manager',
        executable='spawner',
        arguments=['simple_position_controller', '--controller-manager', '/armando_controller_manager'],
        output='screen',
        condition=IfCondition(PythonExpression(["'", controller_type, "' == 'position'"]))
    )

    # Spawner per il JointTrajectoryController (Punto 4d)
    # Caricato solo se controller_type == 'trajectory'
    spawn_joint_trajectory_controller = Node(
        package='controller_manager',
        executable='spawner',
        arguments=['joint_trajectory_controller', '--controller-manager', '/armando_controller_manager'],
        output='screen',
        condition=IfCondition(PythonExpression(["'", controller_type, "' == 'trajectory'"]))
    )

    # Gestori di eventi per caricare i controller dopo lo spawn del robot
    load_joint_state_broadcaster = RegisterEventHandler(
        event_handler=OnProcessExit(
            target_action=spawn_entity,
            on_exit=[spawn_joint_state_broadcaster],
        )
    )

    # Carica il controller di posizione
    load_simple_position_controller = RegisterEventHandler(
        event_handler=OnProcessExit(
            target_action=spawn_joint_state_broadcaster,
            on_exit=[spawn_simple_position_controller],
        )
    )
    
    # Carica il controller di traiettoria
    load_joint_trajectory_controller = RegisterEventHandler(
        event_handler=OnProcessExit(
            target_action=spawn_joint_state_broadcaster,
            on_exit=[spawn_joint_trajectory_controller],
        )
    )


    # --- Bridge per la telecamera ---
    gz_ros_bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=[
            '/camera@sensor_msgs/msg/Image@gz.msgs.Image'
        ],
        remappings=[
            ('/camera', '/camera/image_raw') 
        ],
        output='screen'
    )
    
    # --- Nodo Controller C++ ---
    arm_controller_node = Node(
        package='armando_controller',
        executable='arm_controller_node',
        name='arm_controller_node',
        output='screen',
        parameters=[{'controller_type': controller_type}]
    )


    return LaunchDescription([
        declare_controller_type_arg,
        
        gazebo,
        node_robot_state_publisher,
        spawn_entity,
        
        load_joint_state_broadcaster,
        load_simple_position_controller,
        load_joint_trajectory_controller,
        
        gz_ros_bridge,
        arm_controller_node
    ])

import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node
import xacro

def generate_launch_description():

    # Percorso alla cartella del pacchetto
    pkg_share = get_package_share_directory('armando_description')
    
    # Percorso al file XACRO
    urdf_file_path = os.path.join(pkg_share, 'urdf', 'arm.urdf.xacro')
    
    # Processa XACRO e carica la descrizione del robot
    robot_description_config = xacro.process_file(urdf_file_path)
    robot_desc = robot_description_config.toxml()

    # Percorso al file di configurazione di Rviz
    rviz_config_file = os.path.join(pkg_share, 'config', 'armando_display.rviz')

    # Nodo Robot State Publisher
    node_robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        output='screen',
        parameters=[{'robot_description': robot_desc, 'use_sim_time': False}]
    )

    # Nodo Joint State Publisher (con GUI per gli slider)
    node_joint_state_publisher_gui = Node(
        package='joint_state_publisher_gui',
        executable='joint_state_publisher_gui',
        name='joint_state_publisher_gui',
        output='screen'
    )

    # Nodo Rviz2 (con configurazione)
    node_rviz2 = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        output='screen',
        arguments=['-d', rviz_config_file] # Argomento per caricare il file .rviz
    )

    # Ritorna la descrizione del launch
    return LaunchDescription([
        node_robot_state_publisher,
        node_joint_state_publisher_gui,
        node_rviz2
    ])

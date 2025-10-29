cmake_minimum_required(VERSION 3.8)
project(armando_controller)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

# find dependencies
find_package(ament_cmake REQUIRED)
find_package(rclcpp REQUIRED)
find_package(rclcpp_action REQUIRED)
find_package(sensor_msgs REQUIRED)
find_package(std_msgs REQUIRED)
find_package(control_msgs REQUIRED)

# (Punto 4a) Aggiungere l'eseguibile
add_executable(arm_controller_node src/arm_controller_node.cpp)

# (Punto 4a) Specificare le dipendenze
ament_target_dependencies(arm_controller_node
  rclcpp
  rclcpp_action
  sensor_msgs
  std_msgs
  control_msgs)

# Installare l'eseguibile
install(TARGETS
  arm_controller_node
  DESTINATION lib/${PROJECT_NAME}
)

ament_package()

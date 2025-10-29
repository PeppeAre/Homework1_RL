cmake_minimum_required(VERSION 3.8)
project(armando_description)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

# find dependencies
find_package(ament_cmake REQUIRED)

if(BUILD_TESTING)
  find_package(ament_lint_auto REQUIRED)
  set(ament_cmake_copyright_FOUND TRUE)
  set(ament_cmake_cpplint_FOUND TRUE)
  ament_lint_auto_find_test_dependencies()
endif()

# Installa il package.xml
install(
  FILES package.xml
  DESTINATION share/${PROJECT_NAME}
)

# Installa i file URDF
install(
  DIRECTORY urdf
  DESTINATION share/${PROJECT_NAME}
)

# Installa i file di Launch
install(
  DIRECTORY launch
  DESTINATION share/${PROJECT_NAME}
)

# Installa i file di Config
install(
  DIRECTORY config
  DESTINATION share/${PROJECT_NAME}
)

# Installa le Mesh
install(
  DIRECTORY meshes
  DESTINATION share/${PROJECT_NAME}
)

ament_package()

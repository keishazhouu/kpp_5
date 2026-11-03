cmake_minimum_required(VERSION 3.0.2)

project(locate_it_ros)

find_package(catkin REQUIRED COMPONENTS
  rospy
  std_msgs
  sensor_msgs
  cv_bridge
)

catkin_package()

catkin_install_python(PROGRAMS
  scripts/video_publisher.py
  scripts/locate_it_node.py
  DESTINATION ${CATKIN_PACKAGE_BIN_DESTINATION}
)

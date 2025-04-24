import sys
if sys.prefix == '/usr':
    sys.real_prefix = sys.prefix
    sys.prefix = sys.exec_prefix = '/home/jd/BluROV2_ROS2_ws/install/lumen_lights_ros2'

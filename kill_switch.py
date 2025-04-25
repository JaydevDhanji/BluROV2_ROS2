#/usr/bin/env  python3

import rclpy
from rclpy.node import Node
from mavros_msgs.srv import CommandLong
from std_msgs.msg import Int32
from sensor_msgs.msg import BatteryState
import time

class Battery(Node):
    def __init__(self):
        super().__init__('battery')
        self.battery_sub = self.create_subscription(
            BatteryState,
            '/mavros/battery',
            self.battery_callback,
            10)
        
    def battery_callback(self, msg):
        self.battery = msg.percentage
        self.get_logger().info('Battery percentage: {self.battery}')
        if self.battery < 0.2:
            self.get_logger().warn('Battery low, sending command long')

def main(args=None):
    rclpy.init(args=args)
    battery_node = Battery()
    battery_node.get_logger().info('Battery node started')
    
try:
    rclpy.spin(battery_node)
except KeyboardInterrupt:
    pass
finally:
    battery_node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()

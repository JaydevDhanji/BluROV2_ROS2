#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from mavros_msgs.srv import CommandLong
from std_msgs.msg import Int32
import time

MAV_CMD_SET_SERVO = 183
LIGHTS_OFF = 1000.0
LIGHTS_FULL_ON = 2000.0
LIGHTS_MID = 1500.0

class Lights(Node):
    def __init__(self):
        super().__init__('lights_node')
        
        # Create subscriber
        self.subscription = self.create_subscription(
            Int32,
            '/lights/set_brightness',
            self.lights_callback,
            10  # QoS profile depth
        )
        
        # Create service client
        self.cmd_client = self.create_client(CommandLong, '/mavros/cmd/command')
        
        # Wait for service to be available
        while not self.cmd_client.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('Service not available, waiting...')
        
        # Initialize lights sequence
        self.get_logger().info("Initializing lights sequence")
        self.handle_lights(LIGHTS_FULL_ON)
        time.sleep(1)
        self.handle_lights(LIGHTS_OFF)
        time.sleep(1)
        self.handle_lights(LIGHTS_OFF)
        
        self.get_logger().info("Lights node running!")

    def handle_lights(self, lights_brightness=LIGHTS_OFF):
        request = CommandLong.Request()
        request.broadcast = False
        request.command = MAV_CMD_SET_SERVO
        request.confirmation = 1
        request.param1 = 7  # Servo number
        request.param2 = float(lights_brightness)
        request.param3 = 0.0
        request.param4 = 0.0
        request.param5 = 0.0
        request.param6 = 0.0
        request.param7 = 0.0
        
        future = self.cmd_client.call_async(request)
        future.add_done_callback(self.handle_lights_response)

    def handle_lights_response(self, future):
        try:
            response = future.result()
            self.get_logger().info(f"Lights Service Request: {response.success}")
        except Exception as e:
            self.get_logger().error(f'Service call failed: {e}')

    def lights_callback(self, msg):
        self.get_logger().info(f"TURNING LIGHTS BRIGHTNESS TO: {msg.data}")
        self.handle_lights(msg.data)

def main(args=None):
    rclpy.init(args=args)
    lights_node = Lights()
    
    try:
        rclpy.spin(lights_node)
    except KeyboardInterrupt:
        pass
    finally:
        lights_node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
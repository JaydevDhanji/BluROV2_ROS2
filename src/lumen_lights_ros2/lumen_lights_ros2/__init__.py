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
        self.get_logger().info("Lights node running!")

        # Subscriber
        self.subscriber_ = self.create_subscription(
            Int32,
            "/lights/set_brightness",
            self.lights_callback,
            10  # QoS history depth
        )

        # Service client
        self.cli = self.create_client(CommandLong, '/mavros/cmd/command')
        while not self.cli.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('service not available, waiting again...')
        self.req = CommandLong.Request()

        self.handle_lights(LIGHTS_FULL_ON)
        time.sleep(1)
        self.handle_lights(LIGHTS_OFF)
        time.sleep(1)
        self.handle_lights(LIGHTS_OFF)

    def handle_lights(self, lights_brightness=LIGHTS_OFF):
        self.req.param7 = float(lights_brightness)  # Servo PWM value is param7
        self.req.command = MAV_CMD_SET_SERVO
        self.req.param1 = 0  # Component ID of system sending the command
        self.req.param2 = 0  # Frame (not really used here)
        self.req.param3 = 1  # Confirmation
        self.req.param4 = 7  # Servo channel to control (check your BlueROV2 setup)
        self.req.param5 = 0.0
        self.req.param6 = 0.0
        self.req.target_system = 1  # Target system ID (typically the autopilot)
        self.req.target_component = 1 # Target component ID (typically the autopilot)

        future = self.cli.call_async(self.req)
        rclpy.spin_until_future_complete(self, future)
        response = future.result()
        self.get_logger().info("Lights Service Request: " + str(response.success))

    def lights_callback(self, msg):
        self.get_logger().info("TURNING LIGHTS BRIGHTNESS TO: " + str(msg.data))
        self.handle_lights(float(msg.data))

def main(args=None):
    rclpy.init(args=args)
    lights_node = Lights()
    rclpy.spin(lights_node)
    lights_node.destroy_node()
    rclpy.shutdown()

if __name__ == "__main__":
    main()
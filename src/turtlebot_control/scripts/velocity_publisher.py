#!/usr/bin/env python3

import time

import rclpy
from rclpy.node import Node

from std_msgs.msg import Float32MultiArray
from geometry_msgs.msg import Twist


class VelocityBridge(Node):

    def __init__(self):
        super().__init__('velocity_publisher')

        self.cmd_vel_pub = self.create_publisher(
            Twist,
            '/cmd_vel',
            10)

        self.velocity_sub = self.create_subscription(
            Float32MultiArray,
            '/turtlebot/velocity',
            self.velocity_callback,
            10)

        self.get_logger().info(
            'Waiting for velocity commands on /turtlebot/velocity')

    def velocity_callback(self, msg):

        if len(msg.data) < 2:
            self.get_logger().error(
                'Expected [linear_x, angular_z]')
            return

        linear_x = float(msg.data[0])
        angular_z = float(msg.data[1])

        self.get_logger().info(
            f'Received command: '
            f'linear={linear_x:.2f}, '
            f'angular={angular_z:.2f}')

        cmd = Twist()
        cmd.linear.x = linear_x
        cmd.angular.z = angular_z

        # Move robot
        self.cmd_vel_pub.publish(cmd)

        self.get_logger().info(
            'Publishing command for 1 second')

        time.sleep(1.0)

        # Stop robot
        stop_cmd = Twist()
        self.cmd_vel_pub.publish(stop_cmd)

        self.get_logger().info(
            'Robot stopped')


def main(args=None):

    rclpy.init(args=args)

    node = VelocityBridge()

    try:
        rclpy.spin(node)

    except KeyboardInterrupt:
        pass

    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
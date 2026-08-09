#!/usr/bin/env python3

import rclpy
from rclpy.node import Node

from geometry_msgs.msg import PointStamped
from turtlebot_control.srv import MoveToTarget


class GoalClient(Node):

    def __init__(self):

        super().__init__('goal_client')

        self.client = self.create_client(
            MoveToTarget,
            '/turtlebot/move_to_position'
        )

        while not self.client.wait_for_service(timeout_sec=1.0):
            self.get_logger().info(
                'Waiting for /turtlebot/move_to_position service...'
            )

        self.subscription = self.create_subscription(
            PointStamped,
            '/clicked_point',
            self.point_callback,
            10
        )

        self.get_logger().info(
            'Goal Client Started. Click a point in RViz.'
        )

    def point_callback(self, msg):

        request = MoveToTarget.Request()

        request.x = msg.point.x
        request.y = msg.point.y
        request.theta = 0.0

        self.get_logger().info(
            f'Received Goal: x={request.x:.2f}, y={request.y:.2f}'
        )

        future = self.client.call_async(request)

        future.add_done_callback(
            self.service_response_callback
        )

    def service_response_callback(self, future):

        try:

            response = future.result()

            if response.success:

                self.get_logger().info(
                    'Robot successfully reached target position'
                )

            else:

                self.get_logger().warn(
                    'Robot failed to reach target position'
                )

        except Exception as e:

            self.get_logger().error(
                f'Service call failed: {e}'
            )


def main(args=None):

    rclpy.init(args=args)

    node = GoalClient()

    rclpy.spin(node)

    node.destroy_node()

    rclpy.shutdown()


if __name__ == '__main__':
    main()
#!/usr/bin/env python3

import threading

import rclpy

from rclpy.node import Node
from rclpy.action import ActionClient
from rclpy.executors import MultiThreadedExecutor
from rclpy.callback_groups import ReentrantCallbackGroup

from action_msgs.msg import GoalStatus

from nav2_msgs.action import NavigateToPose
from turtlebot_control.srv import MoveToTarget


class NavigationServiceServer(Node):

    def __init__(self):

        super().__init__('navigation_service_server')

        self.callback_group = ReentrantCallbackGroup()

        self.service = self.create_service(
            MoveToTarget,
            '/turtlebot/move_to_position',
            self.move_to_position_callback,
            callback_group=self.callback_group
        )

        self.nav_client = ActionClient(
            self,
            NavigateToPose,
            '/navigate_to_pose',
            callback_group=self.callback_group
        )

        self.navigation_done = threading.Event()
        self.navigation_success = False

        self.get_logger().info(
            'Navigation Service Ready'
        )

    def move_to_position_callback(self, request, response):

        self.get_logger().info(
            f'Received Goal: x={request.x:.2f}, y={request.y:.2f}'
        )

        if not self.nav_client.wait_for_server(timeout_sec=5.0):

            self.get_logger().error(
                'NavigateToPose action server not available'
            )

            response.success = False
            return response

        goal_msg = NavigateToPose.Goal()

        goal_msg.pose.header.frame_id = 'map'
        goal_msg.pose.header.stamp = self.get_clock().now().to_msg()

        goal_msg.pose.pose.position.x = request.x
        goal_msg.pose.pose.position.y = request.y
        goal_msg.pose.pose.position.z = 0.0

        goal_msg.pose.pose.orientation.x = 0.0
        goal_msg.pose.pose.orientation.y = 0.0
        goal_msg.pose.pose.orientation.z = 0.0
        goal_msg.pose.pose.orientation.w = 1.0

        self.navigation_done.clear()
        self.navigation_success = False

        self.get_logger().info(
            'Sending goal to Nav2...'
        )

        future = self.nav_client.send_goal_async(goal_msg)

        future.add_done_callback(
            self.goal_response_callback
        )

        self.get_logger().info(
            'Waiting for navigation result...'
        )

        self.navigation_done.wait()

        response.success = self.navigation_success

        return response

    def goal_response_callback(self, future):

        self.get_logger().info(
            'Goal response callback triggered'
        )

        goal_handle = future.result()

        if not goal_handle.accepted:

            self.get_logger().error(
                'Goal rejected by Nav2'
            )

            self.navigation_success = False
            self.navigation_done.set()

            return

        self.get_logger().info(
            'Goal accepted by Nav2'
        )

        result_future = goal_handle.get_result_async()

        result_future.add_done_callback(
            self.navigation_result_callback
        )

    def navigation_result_callback(self, future):

        self.get_logger().info(
            'Navigation result callback triggered'
        )

        result = future.result()

        if result.status == GoalStatus.STATUS_SUCCEEDED:

            self.get_logger().info(
                'Navigation Succeeded'
            )

            self.navigation_success = True

        else:

            self.get_logger().warn(
                f'Navigation Failed. Status={result.status}'
            )

            self.navigation_success = False

        self.navigation_done.set()


def main(args=None):

    rclpy.init(args=args)

    node = NavigationServiceServer()

    executor = MultiThreadedExecutor()

    executor.add_node(node)

    try:
        executor.spin()

    finally:
        executor.shutdown()
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
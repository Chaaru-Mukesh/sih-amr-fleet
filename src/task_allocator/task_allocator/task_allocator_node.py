import math

import rclpy
from rclpy.node import Node

from task_msgs.msg import Task, RobotState, TaskAssignment


class TaskAllocator(Node):

    def __init__(self):
        super().__init__('task_allocator')

        self.robots = {}
        self.task = None

        self.task_subscription = self.create_subscription(
            Task,
            '/task',
            self.task_callback,
            10
        )

        self.robot_subscription = self.create_subscription(
            RobotState,
            '/robot_states',
            self.robot_state_callback,
            10
        )

        self.assignment_publisher = self.create_publisher(
            TaskAssignment,
            '/task_assignment',
            10
        )

        self.get_logger().info(
            'Task Allocator started. Waiting for robots and tasks...'
        )

    def robot_state_callback(self, msg):
        self.robots[msg.robot_id] = {
            'x': msg.x,
            'y': msg.y,
            'battery': msg.battery,
            'workload': msg.workload
        }

    def task_callback(self, msg):
        self.task = {
            'x': msg.x,
            'y': msg.y,
            'priority': msg.priority
        }

        self.get_logger().info(
            f'Received task: '
            f'x={msg.x:.2f}, '
            f'y={msg.y:.2f}, '
            f'priority={msg.priority}'
        )

        self.allocate_task()

    def calculate_bid(self, robot):
        distance = math.sqrt(
            (robot['x'] - self.task['x']) ** 2 +
            (robot['y'] - self.task['y']) ** 2
        )

        workload_penalty = robot['workload'] * 2.0

        battery_penalty = (
            (100.0 - robot['battery']) * 0.05
        )

        priority_bonus = self.task['priority'] * 1.5

        bid = (
            distance
            + workload_penalty
            + battery_penalty
            - priority_bonus
        )

        return bid

    def allocate_task(self):

        if self.task is None:
            return

        if not self.robots:
            self.get_logger().warn(
                'No robot states available.'
            )
            return

        self.get_logger().info(
            'Calculating bids...'
        )

        bids = {}

        for name, robot in self.robots.items():

            if robot['battery'] < 15.0:
                self.get_logger().warn(
                    f'{name} skipped: battery too low.'
                )
                continue

            bid = self.calculate_bid(robot)

            bids[name] = bid

            self.get_logger().info(
                f'{name}: bid = {bid:.2f} '
                f'(workload={robot["workload"]}, '
                f'battery={robot["battery"]:.1f}%)'
            )

        if not bids:
            self.get_logger().warn(
                'No suitable robots available.'
            )
            return

        winner = min(bids, key=bids.get)

        self.get_logger().info(
            f'🏆 Task assigned to {winner}!'
        )

        assignment = TaskAssignment()

        assignment.robot_id = winner
        assignment.x = self.task['x']
        assignment.y = self.task['y']

        self.assignment_publisher.publish(assignment)

        # Increase workload because this robot received a new task
        self.robots[winner]['workload'] += 1

        self.get_logger().info(
            f'{winner} workload increased to '
            f'{self.robots[winner]["workload"]}'
        )


def main(args=None):
    rclpy.init(args=args)

    node = TaskAllocator()

    rclpy.spin(node)

    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()

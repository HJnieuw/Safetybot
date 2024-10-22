import numpy as np
import matplotlib.pyplot as plt
import cv2
import random
import math

class Node:
    def __init__(self, point):
        self.point = point
        self.parent = None
        self.cost = 0

class RRTStar:
    def __init__(self, image_path, start, goal, max_iter=10000, step_size=10, goal_radius=30, search_radius=30):
        self.max_iter = max_iter
        self.step_size = step_size
        self.goal_radius = goal_radius
        self.search_radius = search_radius
        
        # Read and preprocess the image
        self.binary_map = self.preprocess_image(image_path)
        
        self.start = Node(start)
        self.goal = Node(goal)
        self.tree = [self.start]

    @staticmethod
    def preprocess_image(image_path):
        floor_plan = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
        _, binary_map = cv2.threshold(floor_plan, 200, 255, cv2.THRESH_BINARY_INV)
        return binary_map // 255  # Convert to binary (1 for obstacles, 0 for free space)

    @staticmethod
    def distance(p1, p2):
        return math.hypot(p1[0] - p2[0], p1[1] - p2[1])

    @staticmethod
    def random_point(image_shape):
        return (random.randint(0, image_shape[1] - 1), random.randint(0, image_shape[0] - 1))

    def nearest(self, point):
        return min(self.tree, key=lambda node: self.distance(node.point, point))

    def is_collision_free(self, p1, p2):
        num_points = int(self.distance(p1, p2) / 1.5)
        for i in range(num_points):
            u = i / num_points
            x = int(p1[0] * (1 - u) + p2[0] * u)
            y = int(p1[1] * (1 - u) + p2[1] * u)
            if self.binary_map[y, x] == 1:  # 1 indicates an obstacle
                return False
        return True

    def nearby_nodes(self, point):
        return [node for node in self.tree if self.distance(node.point, point) < self.search_radius]

    def rewire(self, new_node, nearby_nodes):
        for node in nearby_nodes:
            if node is not new_node.parent:
                new_cost = new_node.cost + self.distance(new_node.point, node.point)
                if new_cost < node.cost and self.is_collision_free(new_node.point, node.point):
                    node.parent = new_node
                    node.cost = new_cost

    def rrt_star(self):
        for i in range(self.max_iter):
            rand_point = self.random_point(self.binary_map.shape)
            if random.random() < 0.05:
                rand_point = self.goal.point

            nearest_node = self.nearest(rand_point)
            direction = np.array(rand_point) - np.array(nearest_node.point)
            direction = direction / np.linalg.norm(direction)
            new_point = tuple(np.round(nearest_node.point + direction * self.step_size).astype(int))

            if (0 <= new_point[0] < self.binary_map.shape[1] and
                0 <= new_point[1] < self.binary_map.shape[0] and
                self.is_collision_free(nearest_node.point, new_point)):

                new_node = Node(new_point)
                new_node.parent = nearest_node
                new_node.cost = nearest_node.cost + self.distance(nearest_node.point, new_point)
                self.tree.append(new_node)

                # Rewire the tree
                near_nodes = self.nearby_nodes(new_point)
                self.rewire(new_node, near_nodes)

                # Check if goal is within reach
                if self.distance(new_point, self.goal.point) < self.goal_radius:
                    self.goal.parent = new_node
                    self.goal.cost = new_node.cost + self.distance(new_point, self.goal.point)
                    self.tree.append(self.goal)
                    print(f"Goal reached at iteration {i}")
                    break

        return self.tree, self.goal

    def extract_path(self):
        path = []
        node = self.goal
        while node:
            path.append(node.point)
            node = node.parent
        return path[::-1]

    def smooth_path(self, path):
        smoothed_path = [path[0]]
        i = 0
        while i < len(path) - 1:
            for j in range(len(path) - 1, i, -1):
                if self.is_collision_free(path[i], path[j]):
                    smoothed_path.append(path[j])
                    i = j
                    break
        return smoothed_path

    def rrt_star_with_smoothing(self, smooth=True):
        self.tree, self.goal = self.rrt_star()
        path = self.extract_path()

        if smooth:
            path = self.smooth_path(path)

        return self.tree, path

    def calculate_path_length(self, path):
        length = 0.0
        for i in range(1, len(path)):
            length += np.linalg.norm(np.array(path[i]) - np.array(path[i - 1]))
        return length

    def plot_results(self, path):
        plt.figure(figsize=(10, 10))
        plt.imshow(self.binary_map, cmap='gray_r')
        for node in self.tree:
            if node.parent:
                plt.plot([node.point[0], node.parent.point[0]], 
                         [node.point[1], node.parent.point[1]], 'b-', linewidth=0.5)

        plt.plot([p[0] for p in path], [p[1] for p in path], 'g-', linewidth=2, label="Smoothed Path")
        plt.scatter(self.start.point[0], self.start.point[1], color='green', label="Start", s=50)
        plt.scatter(self.goal.point[0], self.goal.point[1], color='red', label="Goal", s=50)
        plt.legend()
        plt.title("RRT* Path Planning with Smoothed Path (Inverted Colors)")
        plt.show()

import numpy as np
import matplotlib.pyplot as plt
import cv2
import random
import math
import BIM_mockup as BIM

class Node:
    def __init__(self, point):
        self.point = point
        self.parent = None
        self.cost = 0

class RRTStar:
    def __init__(self, image_path, start, goal, max_iter=20000, goal_radius=20, step_size=10, search_radius=10):
        self.max_iter = max_iter
        self.goal_radius = goal_radius
        self.step_size = step_size
        self.search_radius = search_radius

        # Read and preprocess the image
        self.binary_map = self.load_and_process_map(image_path)
        
        # Initialize start and goal nodes
        self.start_node = Node(start)
        self.goal_node = Node(goal)
        self.tree = [self.start_node]

    @staticmethod
    def load_and_process_map(image_path):
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
        num_points = int(self.distance(p1, p2) / 2) #increase for less detail
        for i in range(num_points):
            u = i / num_points
            x = int(p1[0] * (1 - u) + p2[0] * u)
            y = int(p1[1] * (1 - u) + p2[1] * u)
            if self.binary_map[y, x] == 1:  # 1 indicates an obstacle
                return False
        return True

    def nearby_nodes(self, point, radius):
        return [node for node in self.tree if self.distance(node.point, point) < radius]

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
            if random.random() < 0.15: ### Exploring bias
                rand_point = self.goal_node.point

            nearest_node = self.nearest(rand_point)
            
            # Move towards the random point
            direction = np.array(rand_point) - np.array(nearest_node.point)
            
            norm = np.linalg.norm(direction)
            if norm < 1e-6:
                continue

            direction = direction / norm # Normalize direction
            new_point = tuple(np.round(nearest_node.point + direction * self.step_size).astype(int))

            # Check bounds and collisions
            if (0 <= new_point[0] < self.binary_map.shape[1] and
                0 <= new_point[1] < self.binary_map.shape[0] and
                self.is_collision_free(nearest_node.point, new_point)):
                
                new_node = Node(new_point)
                new_node.parent = nearest_node
                new_node.cost = nearest_node.cost + self.distance(nearest_node.point, new_point)
                self.tree.append(new_node)

                # Rewire the tree
                near_nodes = self.nearby_nodes(new_point, self.search_radius)
                self.rewire(new_node, near_nodes)

                # Check if the goal is reached
                if self.distance(new_point, self.goal_node.point) < self.goal_radius:
                    self.goal_node.parent = new_node
                    self.goal_node.cost = new_node.cost + self.distance(new_point, self.goal_node.point)
                    self.tree.append(self.goal_node)
                    print(f"Goal reached at iteration {i}")
                    break

        return self.tree, self.goal_node

    def extract_path(self):
        path = []
        node = self.goal_node
        while node:
            path.append(node.point)
            node = node.parent
        return path[::-1]  # Reverse the path

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
        # Run the RRT* algorithm
        self.tree, self.goal_node = self.rrt_star()
        
        # Extract the path from start to goal
        path = self.extract_path()
        
        # Apply smoothing if requested
        if smooth:
            path = self.smooth_path(path)
        
        return path

    def calculate_path_length(self, path):
        length = 0.0
        for i in range(1, len(path)):
            length += np.linalg.norm(np.array(path[i]) - np.array(path[i - 1]))
        return length

    def plot_result(self, smoothed_path):
        plt.figure(figsize=(10, 10))
        plt.imshow(self.binary_map, cmap='gray_r')

        # Plot the smoothed path
        plt.plot([p[0] for p in smoothed_path], [p[-1] for p in smoothed_path], 
                 'g-', linewidth=2, label="Smoothed Path")
        
        start_point = smoothed_path[0]
        end_point = smoothed_path[-1]
        
        plt.scatter(start_point[0], start_point[1], color='green', label="Start", s=50)
        plt.scatter(end_point[0], end_point[1], color='red', label="Goal", s=50)
        plt.legend()
        plt.title("RRT* Path Planning with Smoothed Path (Inverted Colors)")
        plt.show()


# Example usage
if __name__ == "__main__":
    # Define start and goal points
    start = BIM.nodes[2]  # Replace with your start coordinates
    goal = BIM.nodes[3]  # Replace with your goal coordinates
    image_path = "construction_site_bk.jpg"

    rrt_star_planner = RRTStar(image_path, start, goal)
    smoothed_path = rrt_star_planner.rrt_star_with_smoothing(smooth=True)
    
    # Calculate the length of the smoothed path
    length_of_smooth_path = rrt_star_planner.calculate_path_length(smoothed_path)
    print("Length of the smoothed path:", length_of_smooth_path)

    # Plot the result
    rrt_star_planner.plot_result(smoothed_path)
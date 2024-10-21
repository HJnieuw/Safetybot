import numpy as np
import matplotlib.pyplot as plt
import cv2
import random
import math
import BIM_mockup as BIM_mockup

# Parameters for RRT*
MAX_ITER = 10000
GOAL_RADIUS = 20
STEP_SIZE = 5  # Small step size for improved accuracy
SEARCH_RADIUS = 20

# Read and preprocess the image
image_path = "construction_site_bk.jpg"
floor_plan = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)

# Invert the image to treat walls as obstacles
_, binary_map = cv2.threshold(floor_plan, 200, 255, cv2.THRESH_BINARY_INV)
binary_map = binary_map // 255  # Convert to binary (1 for obstacles, 0 for free space)

# Define the start (A) and goal (B) points
start = BIM_mockup.nodes[20]  # approximate coordinates for point A
goal = BIM_mockup.nodes[13]  # approximate coordinates for point B

# RRT* Node class
class Node:
    def __init__(self, point):
        self.point = point
        self.parent = None
        self.cost = 0

# Calculate the Euclidean distance between two points
def distance(p1, p2):
    return math.hypot(p1[0] - p2[0], p1[1] - p2[1])

# Generate a random point in the map
def random_point(image_shape):
    return (random.randint(0, image_shape[1] - 1), random.randint(0, image_shape[0] - 1))

# Find the nearest node in the tree to a given point
def nearest(tree, point):
    return min(tree, key=lambda node: distance(node.point, point))

# Check if a path between two points is collision-free
def is_collision_free(p1, p2, binary_map):
    num_points = int(distance(p1, p2) / 1.5)  # Check for collisions at intervals, reduce division for more checks
    for i in range(num_points):
        u = i / num_points
        x = int(p1[0] * (1 - u) + p2[0] * u)
        y = int(p1[1] * (1 - u) + p2[1] * u)
        if binary_map[y, x] == 1:  # 1 indicates an obstacle
            return False
    return True

# Find nodes within a radius of a point
def nearby_nodes(tree, point, radius):
    return [node for node in tree if distance(node.point, point) < radius]

# Rewire the tree by connecting the new node with nearby nodes if it offers a cheaper path
def rewire(tree, new_node, nearby_nodes):
    for node in nearby_nodes:
        if node is not new_node.parent:
            new_cost = new_node.cost + distance(new_node.point, node.point)
            if new_cost < node.cost and is_collision_free(new_node.point, node.point, binary_map):
                node.parent = new_node
                node.cost = new_cost

# RRT* Algorithm
def rrt_star(start, goal, binary_map, max_iter=MAX_ITER):
    start_node = Node(start)
    goal_node = Node(goal)
    tree = [start_node]

    for i in range(max_iter):
        # Generate a random point or goal point with some probability
        rand_point = random_point(binary_map.shape)
        if random.random() < 0.05:
            rand_point = goal

        # Find the nearest node in the tree
        nearest_node = nearest(tree, rand_point)

        # Move towards the random point
        direction = np.array(rand_point) - np.array(nearest_node.point)
        direction = direction / np.linalg.norm(direction)  # Normalize direction
        new_point = tuple(np.round(nearest_node.point + direction * STEP_SIZE).astype(int))

        # Skip if new point is out of bounds or collides with obstacles
        if (0 <= new_point[0] < binary_map.shape[1] and
            0 <= new_point[1] < binary_map.shape[0] and
            is_collision_free(nearest_node.point, new_point, binary_map)):

            new_node = Node(new_point)
            new_node.parent = nearest_node
            new_node.cost = nearest_node.cost + distance(nearest_node.point, new_point)
            tree.append(new_node)

            # Rewire the tree to find optimal paths
            near_nodes = nearby_nodes(tree, new_point, SEARCH_RADIUS)
            rewire(tree, new_node, near_nodes)

            # Check if goal is within reach
            if distance(new_point, goal) < GOAL_RADIUS:
                goal_node.parent = new_node
                goal_node.cost = new_node.cost + distance(new_point, goal)
                tree.append(goal_node)
                print(f"Goal reached at iteration {i}")
                break

    return tree, goal_node

# Extract the final path from start to goal
def extract_path(goal_node):
    path = []
    node = goal_node
    while node:
        path.append(node.point)
        node = node.parent
    return path[::-1]  # Reverse the path

# Function to smooth the path by removing unnecessary nodes
def smooth_path(path, binary_map):
    smoothed_path = [path[0]]
    i = 0
    while i < len(path) - 1:
        for j in range(len(path) - 1, i, -1):
            if is_collision_free(path[i], path[j], binary_map):
                smoothed_path.append(path[j])
                i = j
                break
    return smoothed_path

# Combined RRT* function with smoothing option
def rrt_star_with_smoothing(start, goal, binary_map, max_iter=MAX_ITER, smooth=True):
    # Run the RRT* algorithm
    tree, goal_node = rrt_star(start, goal, binary_map, max_iter)
    
    # Extract the path from start to goal
    path = extract_path(goal_node)
    
    # Apply smoothing if requested
    if smooth:
        path = smooth_path(path, binary_map)
    
    return tree, path

# Run the combined RRT* with smoothing enabled
tree, smoothed_path = rrt_star_with_smoothing(start, goal, binary_map, smooth=True)

# Calculate the length of the smoothed path
def calculate_path_length(path):
    length = 0.0
    for i in range(1, len(path)):
        length += np.linalg.norm(np.array(path[i]) - np.array(path[i-1]))
    return length

# Calculate the length of the sample path
length_of_smooth_path = calculate_path_length(smoothed_path)
print(length_of_smooth_path)

# Plot the result with both original and smoothed paths
plt.figure(figsize=(10, 10))  # Increase figure size for larger output
plt.imshow(binary_map, cmap='gray_r')  # Invert the output colors by using 'gray_r'
for node in tree:
    if node.parent:
        plt.plot([node.point[0], node.parent.point[0]], [node.point[1], node.parent.point[1]], 'b-', linewidth=0.5)

# Plot the smoothed path
plt.plot([p[0] for p in smoothed_path], [p[1] for p in smoothed_path], 'g-', linewidth=2, label="Smoothed Path")
plt.scatter(start[0], start[1], color='green', label="Start", s=50)
plt.scatter(goal[0], goal[1], color='red', label="Goal", s=50)
plt.legend()
plt.title("RRT* Path Planning with Smoothed Path (Inverted Colors)")
plt.show()
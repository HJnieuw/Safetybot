import cv2
import numpy as np
import matplotlib.pyplot as plt
import networkx as nx
import itertools

# Load the image
image_path = "Foto1-1.png"
img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)

if img is None:
    print("Error loading the image!")
    exit()

print(f"Image shape: {img.shape}")  # Debugging step

thresholded = cv2.adaptiveThreshold(img, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 2)

kernel = np.ones((2, 2), np.uint8)  # Adjust kernel size depending on what you want to remove
eroded = cv2.erode(thresholded, kernel, iterations=1)

# Apply dilation to restore thicker walls after erosion
dilated = cv2.dilate(eroded, kernel, iterations=2)

# Display the cleaned-up image
plt.imshow(dilated, cmap='gray', vmin=0, vmax=255)
plt.title('Cleaned-up Image (Thick walls only)')

print("Click multiple points, double-click to finish")

clicks = plt.ginput(0)  
plt.close()

print(f"Clicked points: {clicks}")

# Convert clicked points to (row, col) format
points = [(int(click[1]), int(click[0])) for click in clicks]  

print(f"Selected points: {points}")

# Convert the cleaned-up image into a binary matrix (0 = walkable, 1 = wall)
floorplan = (dilated == 255).astype(int)

plt.imshow(floorplan, cmap='gray', vmin=0, vmax=1)
for i, point in enumerate(points):
    plt.scatter(point[1], point[0], label=f"Point {i+1}")
plt.title('Floorplan with Multiple Points')
plt.legend()
plt.show()

# Create the graph and add diagonal movement with cost
G = nx.Graph()

rows, cols = floorplan.shape
for row in range(rows):
    for col in range(cols):
        if floorplan[row, col] == 0:  # Walkable space
            node = (row, col)
            G.add_node(node)
            for r_offset, c_offset, weight in [(-1, 0, 1), (1, 0, 1), (0, -1, 1), (0, 1, 1), 
                                               (-1, -1, np.sqrt(2)), (-1, 1, np.sqrt(2)), 
                                               (1, -1, np.sqrt(2)), (1, 1, np.sqrt(2))]:
                r, c = row + r_offset, col + c_offset
                if 0 <= r < rows and 0 <= c < cols and floorplan[r, c] == 0:
                    G.add_edge((row, col), (r, c), weight=weight)

# Function to track visited nodes during A* search
def astar_with_partial_path(graph, start, goal):
    try:
        path = nx.astar_path(graph, start, goal, weight='weight')
        return path, list(nx.shortest_path(graph, source=start, target=goal))  # Track visited nodes
    except nx.NetworkXNoPath:
        return None, []
# Greedy approach to finding the shortest path between multiple points
def greedy_path(graph, points):
    total_path = []
    total_visited = []
    remaining_points = points.copy()
    current_point = remaining_points.pop(0)
    total_path.append(current_point)

    while remaining_points:
        next_point, best_path, best_visited = None, None, None
        shortest_distance = float('inf')

        # Find the closest point
        for point in remaining_points:
            path, visited = astar_with_partial_path(graph, current_point, point)
            if path and len(path) < shortest_distance:
                shortest_distance = len(path)
                next_point = point
                best_path = path
                best_visited = visited

        # Update current point and paths
        if next_point:
            remaining_points.remove(next_point)
            total_path.extend(best_path[:-1])  # Avoid duplicating points
            total_visited.extend(best_visited)
            current_point = next_point
        else:
            break  # No path found for the next point

    return total_path, total_visited

# Find the best greedy path
best_path, best_visited = greedy_path(G, points)

# Visualize the optimal path or the best visited nodes
fig, ax = plt.subplots()
ax.imshow(floorplan, cmap=plt.cm.binary)

# Plot the optimal path if found
if best_path:
    path_x, path_y = zip(*best_path)
    ax.plot(path_y, path_x, marker="o", color="r", label="Greedy Path")

# Mark all points on the image
for i, point in enumerate(points):
    ax.plot(point[1], point[0], marker="o", markersize=10, label=f"Point {i+1}")

plt.legend()
plt.show()


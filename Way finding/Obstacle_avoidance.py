import cv2
import numpy as np
import matplotlib.pyplot as plt
import networkx as nx

image_path = r"C:\Users\Barte van der Zijden\Downloads\Foto1-1.png"
img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)

if img is None:
    print("Error loading the image!")
    exit()

print(f"Image shape: {img.shape}")  # Debugging step

thresholded = cv2.adaptiveThreshold(img, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 2)

kernel = np.ones((3, 3), np.uint8)  # Adjust kernel size depending on what you want to remove
eroded = cv2.erode(thresholded, kernel, iterations=1)

# Apply dilation to restore thicker walls after erosion
dilated = cv2.dilate(eroded, kernel, iterations=2)

# Display the cleaned-up image
plt.imshow(dilated, cmap='gray', vmin=0, vmax=255)
plt.title('Cleaned-up Image (Thick walls only)')

print("Click the start and end point")

clicks = plt.ginput(2)  
plt.close()

print(f"Clicked points: {clicks}")

start = (int(clicks[0][1]), int(clicks[0][0]))  
goal = (int(clicks[1][1]), int(clicks[1][0]))  

print(f"start: {start}, goals: {goal}")

floorplan = (dilated == 255).astype(int)

plt.imshow(floorplan, cmap='gray', vmin=0, vmax=1)
plt.scatter(start[1], start[0], color="green", label="Start")
plt.scatter(goal[1], goal[0], color="blue", label="Goal")
plt.title('Floorplan with Start and Goal')
plt.legend()
plt.show()

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
def astar_with_partial_path(graph, start, goal):
    visited = []
    try:
        path = nx.astar_path(graph, start, goal, weight='weight')
        return path, visited
    except nx.NetworkXNoPath:
        return None, visited

# Ensure the goal is a walkable node
if floorplan[goal] == 1:
    print("Goal is on a wall, choose another point.")
    exit()

    exit()

# Find the shortest path using A* algorithm with diagonal movement
path, visited = astar_with_partial_path(G, start, goal)

# Check if a path was found
if path:
    print(f"Shortest path: {path}")
else:
    print("No path found! Showing partial path...")

# Visualize the grid and the path or partial path
fig, ax = plt.subplots()
ax.imshow(floorplan, cmap=plt.cm.Dark2)

# Plot the visited nodes (partial path) if no full path found
if not path:
    if visited:
        visited_x, visited_y = zip(*visited)
        ax.plot(visited_y, visited_x, marker="o", color="orange", label="Visited Nodes")
    else:
        print("No nodes were visited during the search.")

# Plot the full path if found
if path:
    path_x, path_y = zip(*path)
    ax.plot(path_y, path_x, marker="o", color="r", label="Shortest Path")

# Mark the start and goal on the image
ax.plot(start[1], start[0], marker="o", color="green", markersize=10, label="Start")
ax.plot(goal[1], goal[0], marker="o", color="blue", markersize=10, label="Goal")

plt.legend()
plt.show()

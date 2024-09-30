import cv2
import numpy as np
import matplotlib.pyplot as plt
import networkx as nx
import random

# Load the image
image_path = r"C:\Users\Barte van der Zijden\Downloads\Foto1-1.png"
img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)

if img is None:
    print("Error loading the image!")
    exit()

# Step 1: Increase contrast by applying a threshold
_, binary_img = cv2.threshold(img, 180, 255, cv2.THRESH_BINARY_INV)  # Increase threshold for sharper contrast

# Step 2: Apply Gaussian Blur to reduce noise
blurred = cv2.GaussianBlur(binary_img, (3, 3), 0)

# Step 3: Use Canny edge detection with lower thresholds to detect more boundaries
edges = cv2.Canny(blurred, 20, 80)  # Lower thresholds to capture more edges

# Step 4: Apply morphological operations to close gaps and better define room boundaries
kernel = np.ones((3, 3), np.uint8)

# First, dilate to close small gaps between walls
dilated = cv2.dilate(edges, kernel, iterations=2)

# Then, erode to refine the edges after dilation
closed = cv2.erode(dilated, kernel, iterations=1)

# Step 5: Invert the image so that rooms are white and walls are black
inverted = cv2.bitwise_not(closed)

# Step 6: Find contours (rooms) in the processed image
contours, _ = cv2.findContours(inverted, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

# Filter out small contours based on area (to remove noise)
min_contour_area = 500  # Increase this value if necessary to remove noise
filtered_contours = [cnt for cnt in contours if cv2.contourArea(cnt) > min_contour_area]

# Create an empty image (with 3 channels for colors) to fill with different colors
color_zones = np.zeros((*img.shape, 3), dtype=np.uint8)

# Function to generate random colors
def random_color():
    return [random.randint(0, 255) for _ in range(3)]

# Draw each room with a different color and some transparency
for i, contour in enumerate(filtered_contours):
    color = random_color()
    cv2.drawContours(color_zones, [contour], -1, color, thickness=cv2.FILLED)

# Convert the colored image to float so we can apply transparency
color_zones = color_zones.astype(np.float32) / 255.0

# Overlay the colored zones with transparency over the original image
fig, ax = plt.subplots()
ax.imshow(img, cmap='gray', vmin=0, vmax=255)  # Show the floorplan in the background
ax.imshow(color_zones, alpha=0.5)  # Show the colored zones with 50% transparency

# Find the centroid or another representative point inside each room
def find_centroids(contours):
    points = []
    for contour in contours:
        M = cv2.moments(contour)
        if M["m00"] != 0:
            cx = int(M["m10"] / M["m00"])  # X-coordinate of centroid
            cy = int(M["m01"] / M["m00"])  # Y-coordinate of centroid
            points.append((cy, cx))  # Store points in (row, col) format
    return points

# Get a point (centroid) inside each room
room_points = find_centroids(filtered_contours)

# Mark centroids of rooms
for i, point in enumerate(room_points):
    plt.scatter(point[1], point[0], label=f"Room {i+1}", color="black", zorder=3)

plt.title('Rooms with Opaque Colors and Centroids')
plt.legend()
plt.show()

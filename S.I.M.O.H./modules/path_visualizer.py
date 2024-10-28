import json
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
from matplotlib.lines import Line2D
import numpy as np

# Import from other scripts
from robot_path import simulate_robot_path
from hazard_detection import load_json

def get_boundary_points(zone):
    """Extract boundary points from the zone data"""
    
    # Retrieve the boundary points directly as a list of tuples
    boundary = zone.get('boundary', [])

    # Ensure the boundary is a list of points, otherwise empty list
    return boundary if isinstance(boundary, list) else []


#ORIGNIAL!!!!!
    # boundary = zone.get('boundary', {})
    # if not boundary:
    #     return []

    # # Check if boundary is defined by min/max or as a list of points
    # if all(k in boundary for k in ('x_min', 'x_max', 'y_min', 'y_max')):
    #     x_min = boundary['x_min']
    #     x_max = boundary['x_max']
    #     y_min = boundary['y_min']
    #     y_max = boundary['y_max']
        

    #     # Define rectangle corners with the transformed y-coordinates
    #     points = [
    #         (x_min, y_min),
    #         (x_min, y_max),
    #         (x_max, y_max),
    #         (x_max, y_min)
    #     ]
    # elif 'points' in boundary:
    #     # Assume boundary is a list of (x, y) tuples, and transform each y-coordinate
    #     points = [boundary['points']]
    # else:
    #     points = []
    
    # return points

def plot_zones(ax, zones, image_height):
    """Plot all zones with transformed coordinates"""
    for zone_name, zone_info in zones.items():
        boundary_points = get_boundary_points(zone_info)
        if not boundary_points:
            print(f"Warning: No boundary points found for {zone_name}. Skipping.")
            continue
        
        # Create a polygon for the zone
        polygon = Polygon(boundary_points, color='red', closed=True, fill=True, edgecolor='black', alpha=0.3)
        ax.add_patch(polygon)
        
        # Calculate the centre for placing the text
        xs, ys = zip(*boundary_points)
        centroid_x = sum(xs) / len(xs)
        centroid_y = sum(ys) / len(ys)
        
        # Prepare the label with zone name and required PPE
        required_PPE = zone_info.get('required_PPE', 'None')
        label = f"{zone_name}\nPPE: {required_PPE}"
        
        # Add the label to the plot
        ax.text(centroid_x, centroid_y, label, horizontalalignment='center', verticalalignment='center', fontsize=4, bbox=dict(facecolor='white', alpha=0.6, edgecolor='none'))
        
def plot_robot_path(ax, path, image_height, color='green', linewidth=3, label='Robot Path'):
    """Plot the robot path on the given and transform the y axis."""
    x_coords = []
    y_coords = []
    
    for position in path:
        x, y, z = position
        x_coords.append(x)
        y_coords.append(image_height - y)  
    
    ax.plot(x_coords, y_coords, color=color, linewidth=linewidth, label=label)
    ax.scatter(x_coords, y_coords, c=color, s=10)


def main():
    """Main function to visualize zones and robot path."""
    # Path to the JSON file containing zone information
    ZONE_ID_FILE = 'S.I.M.O.H./assets/BIM.json'  # Update this path if necessary

    # Load zone data
    zones = load_json(ZONE_ID_FILE)

    # Height of the site plan in pixels
    image_height = 2339  

    # Initialize the plot
    fig, ax = plt.subplots(figsize=(10, 8))
    ax.set_title('Building Site Visualization')
    ax.set_xlabel('x coordinate')
    ax.set_ylabel('y coordinate')
    
    # Plot zones
    plot_zones(ax, zones, image_height)
    
    # Simulate and plot robot path live
    robot_path = simulate_robot_path()
    plot_robot_path(ax, robot_path, image_height)
    
    # Customize the plot
    ax.set_aspect('equal', 'box')
    
    # Add legend
    ax.legend()

    # Show the plot
    plt.show()

if __name__ == "__main__":
    main()

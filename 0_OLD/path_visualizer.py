import json
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
from matplotlib.lines import Line2D

# Import from other scripts
from robot_path import simulate_robot_path
from hazard_detection_sim import load_json

def get_boundary_points(zone):
    """Extract boundary points from the zone data.
    For rectangular zones defined by x_min, x_max, y_min, y_max,
    returns the four corner points"""

    boundary = zone.get('boundary', {})
    if not boundary:
        return []

    # Check if boundary is defined by min/max or as a list of points
    if all(k in boundary for k in ('x_min', 'x_max', 'y_min', 'y_max')):
        x_min = boundary['x_min']
        x_max = boundary['x_max']
        y_min = boundary['y_min']
        y_max = boundary['y_max']
        # Define rectangle corners
        points = [
            (x_min, y_min),
            (x_min, y_max),
            (x_max, y_max),
            (x_max, y_min)
        ]
    elif 'points' in boundary:
        # Assume boundary is a list of (x, y) tuples
        points = boundary['points']
    else:
        points = []
    
    return points

def plot_zones(ax, zones):
    """Plot all zones"""
    for zone_name, zone_info in zones.items():
        boundary_points = get_boundary_points(zone_info)
        if not boundary_points:
            print(f"Warning: No boundary points found for {zone_name}. Skipping.")
            continue
        
        # Create a polygon for the zone
        polygon = Polygon(boundary_points, closed=True, fill=True, edgecolor='black', alpha=0.3)
        ax.add_patch(polygon)
        
        # Calculate the centroid for placing the text
        xs, ys = zip(*boundary_points)
        centroid_x = sum(xs) / len(xs)
        centroid_y = sum(ys) / len(ys)
        
        # Prepare the label with zone name and required PPE
        required_PPE = zone_info.get('required_PPE', 'None')
        label = f"{zone_name}\nPPE: {required_PPE}"
        
        # Add the label to the plot
        ax.text(centroid_x, centroid_y, label, horizontalalignment='center', verticalalignment='center', fontsize=9, bbox=dict(facecolor='white', alpha=0.6, edgecolor='none'))
        
def plot_robot_path(ax, path, color='green', linewidth=3, label='Robot Path'):
    """Plot the robot path on the given Axes."""
    x_coords = []
    y_coords = []
    
    for position in path:
        x, y, z = position
        x_coords.append(x)
        y_coords.append(y)
    
    ax.plot(x_coords, y_coords, color=color, linewidth=linewidth, label=label)
    ax.scatter(x_coords, y_coords, c=color, s=10)  # Optional: Mark each position

def main():
    """Main function to visualize zones and robot path."""
    # Path to the JSON file containing zone information
    ZONE_ID_FILE = 'zone_ID_sim.json'  # Update this path if necessary

    # Load zone data
    zones = load_json(ZONE_ID_FILE)

    # Initialize the plot
    fig, ax = plt.subplots(figsize=(10, 8))
    ax.set_title('Robot Path and Zone Visualization')
    ax.set_xlabel('X Coordinate')
    ax.set_ylabel('Y Coordinate')
    
    # Plot zones
    plot_zones(ax, zones)
    
    # Simulate robot path
    robot_path = list(simulate_robot_path())
    plot_robot_path(ax, robot_path)
    
    # Customize the plot
    ax.set_aspect('equal', 'box')
    
    # Determine plot limits based on zones and robot path
    all_x = []
    all_y = []
    for zone in zones.values():
        boundary_points = get_boundary_points(zone)
        if boundary_points:
            xs, ys = zip(*boundary_points)
            all_x.extend(xs)
            all_y.extend(ys)
    robot_x, robot_y, _ = zip(*robot_path)
    all_x.extend(robot_x)
    all_y.extend(robot_y)
    
    padding = 10  # Add some padding to the plot
    ax.set_xlim(min(all_x) - padding, max(all_x) + padding)
    ax.set_ylim(min(all_y) - padding, max(all_y) + padding)
    
    # Add legend
    ax.legend()

    # Show the plot
    plt.show()

if __name__ == "__main__":
    main()

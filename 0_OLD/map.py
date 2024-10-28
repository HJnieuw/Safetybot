import json
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
from matplotlib.animation import FuncAnimation
import matplotlib.lines as mlines
import matplotlib.patches as mpatches

def simulate_robot_path():
    """Simulate the robot moving through zones."""
    # For simplicity, let's simulate the robot moving through zones.
    # Starting from x=0 and increasing x over time
    # Speed and range can be adjusted 

    for x in range(0, 200):
        y = 50               # Keep y constant for simplicity, can modify for path
        z = 0               # Assuming 2D plane
        yield (x, y, z)

def load_json(path):
    """Load JSON data from the given file path."""
    with open(path, 'r') as f:
        return json.load(f)

def get_boundary_points(zone):
    """
    Extract boundary points from the zone data.
    For rectangular zones defined by x_min, x_max, y_min, y_max,
    returns the four corner points.
    
    For future arbitrary shapes, modify this function to extract
    boundary points accordingly.
    """
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
    """Plot all zones on the given Axes."""
    zone_patches = {}
    zone_labels = {}
    for zone_name, zone_info in zones.items():
        boundary_points = get_boundary_points(zone_info)
        if not boundary_points:
            print(f"Warning: No boundary points found for {zone_name}. Skipping.")
            continue
        
        # Create a polygon for the zone
        polygon = Polygon(boundary_points, closed=True, fill=True, edgecolor='black', alpha=0.3)
        ax.add_patch(polygon)
        zone_patches[zone_name] = polygon
        
        # Calculate the centroid for placing the text
        xs, ys = zip(*boundary_points)
        centroid_x = sum(xs) / len(xs)
        centroid_y = sum(ys) / len(ys)
        
        # Prepare the label with zone name and required PPE
        required_PPE = zone_info.get('required_PPE', 'None')
        label = f"{zone_name}\nPPE: {required_PPE}"
        
        # Add the label to the plot
        ax.text(centroid_x, centroid_y, label, horizontalalignment='center', verticalalignment='center', fontsize=9, bbox=dict(facecolor='white', alpha=0.6, edgecolor='none'))
        
        # Optionally, add more information like zone activity
        zone_activity = zone_info.get('zone_activity', '')
        if zone_activity:
            ax.text(centroid_x, centroid_y - 5, f"Activity: {zone_activity}", horizontalalignment='center', verticalalignment='center', fontsize=8, color='blue', bbox=dict(facecolor='white', alpha=0.5, edgecolor='none'))
    
    return zone_patches

def initialize_plot(zones):
    """Initialize the Matplotlib plot with zones."""
    fig, ax = plt.subplots(figsize=(12, 8))
    ax.set_title('Real-Time Robot Path and Zone Visualization')
    ax.set_xlabel('X Coordinate')
    ax.set_ylabel('Y Coordinate')
    
    # Plot zones
    plot_zones(ax, zones)
    
    # Initialize robot path line and current position marker
    path_line, = ax.plot([], [], color='blue', linewidth=2, label='Robot Path')
    current_pos, = ax.plot([], [], marker='o', color='red', markersize=8, label='Robot Current Position')
    
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
    # Assuming robot path x ranges from 0 to 200 and y=50
    all_x.extend([0, 200])
    all_y.extend([50, 50])
    
    padding = 10  # Add some padding to the plot
    ax.set_xlim(min(all_x) - padding, max(all_x) + padding)
    ax.set_ylim(min(all_y) - padding, max(all_y) + padding)
    
    # Add grid
    ax.grid(True, which='both', linestyle='--', linewidth=0.5)
    
    # Add legend
    ax.legend(loc='upper left')
    
    return fig, ax, path_line, current_pos

def animate(i, robot_generator, path_line, current_pos, ax):
    """Update function for animation."""
    try:
        position = next(robot_generator)
        x, y, z = position
    except StopIteration:
        # If the generator is exhausted, stop the animation
        ani.event_source.stop()
        return path_line, current_pos

    # Get current data of the path line
    xdata, ydata = path_line.get_data()
    xdata = list(xdata)
    ydata = list(ydata)
    
    # Append new position
    xdata.append(x)
    ydata.append(y)
    
    # Update the path line
    path_line.set_data(xdata, ydata)
    
    # Update the current position marker
    current_pos.set_data([x], [y])  # Wrap in lists to make them sequences
    
    # Optionally, highlight the zone the robot is currently in
    # This requires determining which zone contains (x, y)
    # For now, we skip this part
    
    return path_line, current_pos

def main():
    """Main function to visualize zones and robot path in real-time."""
    # Path to the JSON file containing zone information
    ZONE_ID_FILE = 'zone_ID_sim.json'  # Update this path if necessary

    # Load zone data
    zones = load_json(ZONE_ID_FILE)

    # Initialize the plot
    fig, ax, path_line, current_pos = initialize_plot(zones)

    # Create a generator for the robot path
    robot_gen = simulate_robot_path()

    # Create the animation
    global ani  # Declare as global to allow stopping inside animate
    ani = FuncAnimation(
        fig, 
        animate, 
        fargs=(robot_gen, path_line, current_pos, ax), 
        frames=200,  # Specify the number of frames
        interval=0,  # Update every 100 milliseconds
        blit=True,
        save_count=200  # Prevent unbounded caching
    )

    # Display the plot
    plt.show()

if __name__ == "__main__":
    main()

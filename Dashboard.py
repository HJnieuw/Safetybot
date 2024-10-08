import json
import cv2
import matplotlib.pyplot as plt
import numpy as np
import matplotlib as mpl
from matplotlib.ticker import MaxNLocator  # Import MaxNLocator for integer Y-axis ticks

# Define the variables for the JSON file
json_file = "zone_ID.json"
#output_image = "annotated_construction_site_bk.jpg"

# Function to generate shades of color from light coral to dark red based on hazard count
def get_red_color(hazard_count, max_hazards):
    normalized_value = hazard_count / max_hazards if max_hazards > 0 else 0
    r = 1 - (normalized_value * 0.5)  # Red value decreases slightly
    g = 0.5 - (normalized_value * 0.5)
    b = 0.5 - (normalized_value * 0.5)
    return (r, g, b, 0.6)  # Adding transparency with alpha = 0.6

# Function to handle no hazards
def display_no_hazards_message(zone_name):
    ax2.cla()
    ax2.text(0.5, 0.5, f'No hazards in {zone_name}', color='black', fontsize=16, ha='center', va='center')
    ax2.set_xticks([])  
    ax2.set_yticks([])  
    ax2.set_title(f'')
    plt.draw()

# Function to create the bar chart for a specific zone
def create_bar_chart_for_zone(zone_name):
    zone = zone_data.get(zone_name)
    helmet_hazard_count, hammer_hazard_count = 0, 0
    for hazard in zone['hazard type']:
        if 'Head detected without helmet' in hazard: #HIER DE BEWOORDING NIET GOED
            helmet_hazard_count += 1
        if 'loose hammer' in hazard:
            hammer_hazard_count += 1

    ax2.cla()

    if helmet_hazard_count == 0 and hammer_hazard_count == 0:
        ax2.text(0.5, 0.5, f'No hazards in {zone_name}', color='black', fontsize=16, ha='center', va='center')
        ax2.axis('off')
    else:
        labels = ['Helmet Hazards', 'Loose Hammer Hazards']
        sizes = [helmet_hazard_count, hammer_hazard_count]
        ax2.bar(labels, sizes, color=['darkred', 'lightcoral'])
        ax2.set_ylabel('Amount of Hazards')
        ax2.set_title(f'Hazard Distribution in {zone_name}')
        ax2.yaxis.set_major_locator(MaxNLocator(integer=True))
        ax2.axis('on')

    plt.draw()

# Event handler for clicking on a zone in the heatmap
def on_click(event):
    if event.inaxes == ax1:
        x_click, y_click = event.xdata, event.ydata
        for zone_name, info in zone_data.items():
            x_zone, y_zone = info['location']
            if np.hypot(x_click - x_zone, y_click - y_zone) < 50:  # Threshold for detecting the click
                create_bar_chart_for_zone(zone_name)

# Load the zone data from the JSON file
with open(json_file, 'r') as f:
    zone_data = json.load(f)

# Use the floorplan from the first zone to load the image
first_zone = list(zone_data.values())[0]  # Get the first zone's data
construction_site = first_zone["floorplan"]  # Extract the floorplan path from the JSON

# Load the image using the floorplan path from the JSON
img = cv2.imread(construction_site)
img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

# Get the maximum number of hazards to scale the colors
max_hazards = max(round(info['amount of hazards']) for info in zone_data.values())

# Set up the figure with two subplots
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 9), gridspec_kw={'width_ratios': [2, 1]})

# Subplot 1: Heatmap on construction site plan
ax1.imshow(img_rgb)

# Plot the heatmap markers
for zone, info in zone_data.items():
    x, y = info['location']
    hazards = round(info['amount of hazards'])  

    if hazards > 0:  # Only plot zones with 1 or more hazards
        color = get_red_color(hazards, max_hazards)
        size = 100 + hazards * 300
        ax1.scatter(x, y, s=size, c=[color])
    
    # Plot the black dot and add text labels
    ax1.scatter(x , y , s=30, c='black') 
    ax1.text(x + 40, y + 25, f'{zone}', color='black', fontsize=10, ha='center')

# Create the color legend for the heatmap
cmap = mpl.colors.LinearSegmentedColormap.from_list("", ["lightcoral", "darkred"])
norm = mpl.colors.Normalize(vmin=1, vmax=max_hazards)
cbar = plt.colorbar(mpl.cm.ScalarMappable(norm=norm, cmap=cmap), ax=ax1, shrink=0.5)

# Modify the color bar to show whole numbers only
cbar.set_ticks([i for i in range(1, max_hazards + 1)])
cbar.set_ticklabels([str(i) for i in range(1, max_hazards + 1)])

cbar.set_label('Amount of Hazards', fontsize=10, rotation=90, labelpad=1)
cbar.ax.yaxis.set_label_position('left')

ax1.set_title('Amount of Hazards per Zone')
ax1.axis('off')

# Adjust the bar chart subplot to have a fixed height
ax2.set_ylim(0, max_hazards) 
ax2.set_aspect(aspect='auto')  
ax2.set_title("Click on a zone to view hazard details")
ax2.axis("off")

# Connect the click event to the heatmap
cid = fig.canvas.mpl_connect('button_press_event', on_click)

# Adjust layout to avoid overlapping and ensure equal sizing
plt.subplots_adjust(left=0.05, right=0.95, wspace=0.3)
plt.show()

# Save the annotated image to a file
#plt.savefig(output_image, bbox_inches='tight', pad_inches=0.1)

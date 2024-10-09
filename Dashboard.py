import json
import cv2
import matplotlib.pyplot as plt
import numpy as np
import matplotlib as mpl
from matplotlib.ticker import MaxNLocator  # Import MaxNLocator for integer Y-axis ticks

class ConstructionHazardVisualizer:
    def __init__(self):
        self.json_file = "zone_ID.json"  # Hardcoded path to the JSON file
        self.zone_data = self.load_zone_data()
        self.max_hazards = self.get_max_hazards()
        # Adjusted figsize to reduce the height (width remains the same)
        self.fig, (self.ax1, self.ax2) = plt.subplots(1, 2, figsize=(12, 6), gridspec_kw={'width_ratios': [6, 5]})
        self.construction_site = self.load_image()
        self.cid = None

    # Function to load the zone data from the JSON file
    def load_zone_data(self):
        with open(self.json_file, 'r') as f:
            return json.load(f)

    # Function to get the maximum number of hazards to scale the colors
    def get_max_hazards(self):
        return max(round(info['amount_of_hazards']) for info in self.zone_data.values())

    # Function to load the image using the floorplan path from the JSON
    def load_image(self):
        first_zone = list(self.zone_data.values())[0]  # Get the first zone's data
        construction_site = first_zone["floorplan"]  # Extract the floorplan path from the JSON
        img = cv2.imread(construction_site)
        return cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    # Function to generate shades of color from light coral to dark red based on hazard count
    def get_red_color(self, hazard_count):
        normalized_value = hazard_count / self.max_hazards if self.max_hazards > 0 else 0
        r = 1 - (normalized_value * 0.5)  # Red value decreases slightly
        g = 0.5 - (normalized_value * 0.5)
        b = 0.5 - (normalized_value * 0.5)
        return (r, g, b, 0.6)  # Adding transparency with alpha = 0.6

    # Function to display no hazards message
    def display_no_hazards_message(self, zone_name):
        self.ax2.cla()
        self.ax2.text(0.5, 0.5, f'No hazards in {zone_name}', color='black', fontsize=16, ha='center', va='center')
        self.ax2.set_xticks([])  
        self.ax2.set_yticks([])  
        self.ax2.set_title(f'')
        plt.draw()

    # Function to create the bar chart for a specific zone
    def create_bar_chart_for_zone(self, zone_name):
        zone = self.zone_data.get(zone_name)
        helmet_hazard_count, hammer_hazard_count = 0, 0
        
        # Adjust the string matching for both helmet and hammer hazards
        for hazard in zone['hazard_type']:
            if 'person is not wearing their helmet' in hazard:  # Adjusted for the correct phrase
                helmet_hazard_count += 1
            if 'loose hammer detected' in hazard:  # Adjusted for the correct phrase
                hammer_hazard_count += 1

        self.ax2.cla()

        if helmet_hazard_count == 0 and hammer_hazard_count == 0:
            self.ax2.text(0.5, 0.5, f'No hazards in {zone_name}', color='black', fontsize=16, ha='center', va='center')
            self.ax2.axis('off')
        else:
            labels = ['Helmet Hazards', 'Loose Hammer Hazards']
            sizes = [helmet_hazard_count, hammer_hazard_count]
            self.ax2.bar(labels, sizes, color=['darkred', 'lightcoral'])
            self.ax2.set_ylabel('Amount of Hazards')
            self.ax2.set_title(f'Hazard Distribution in {zone_name}')
            self.ax2.yaxis.set_major_locator(MaxNLocator(integer=True))
            self.ax2.axis('on')

        plt.draw()

    # Event handler for clicking on a zone in the heatmap
    def on_click(self, event):
        if event.inaxes == self.ax1:
            x_click, y_click = event.xdata, event.ydata
            for zone_name, info in self.zone_data.items():
                x_zone, y_zone = info['location']
                if np.hypot(x_click - x_zone, y_click - y_zone) < 50:  # Threshold for detecting the click
                    self.create_bar_chart_for_zone(zone_name)

    # Function to draw the initial visualizations
    def draw(self):
        # Subplot 1: Heatmap on construction site plan
        self.ax1.imshow(self.construction_site)

        # Plot the heatmap markers
        for zone, info in self.zone_data.items():
            x, y = info['location']
            hazards = round(info['amount_of_hazards'])

            if hazards > 0:  # Only plot zones with 1 or more hazards
                color = self.get_red_color(hazards)
                size = 100 + hazards * 300
                self.ax1.scatter(x, y, s=size, c=[color])

            # Plot the black dot and add text labels
            self.ax1.scatter(x, y, s=30, c='black')
            self.ax1.text(x + 40, y + 40, f'{zone}', color='black', fontsize=10, ha='center')

        # Create the color legend for the heatmap
        cmap = mpl.colors.LinearSegmentedColormap.from_list("", ["lightcoral", "darkred"])
        norm = mpl.colors.Normalize(vmin=1, vmax=self.max_hazards)
        cbar = plt.colorbar(mpl.cm.ScalarMappable(norm=norm, cmap=cmap), ax=self.ax1, shrink=0.5)

        # Calculate evenly spaced ticks
        num_ticks = 5  # Set the desired number of ticks (you can adjust this)
        ticks = np.linspace(1, self.max_hazards, num_ticks).astype(int)  # Evenly spaced ticks

        # Set ticks and labels
        cbar.set_ticks(ticks)
        cbar.set_ticklabels([str(i) for i in ticks])

        cbar.set_label('Amount of Hazards', fontsize=10, rotation=90, labelpad=1)
        cbar.ax.yaxis.set_label_position('left')

        cbar.set_label('Amount of Hazards', fontsize=10, rotation=90, labelpad=1)
        cbar.ax.yaxis.set_label_position('left')

        self.ax1.set_title('Amount of Hazards per Zone')
        self.ax1.axis('off')

        # Adjust the bar chart subplot to have a fixed height
        self.ax2.set_ylim(0, self.max_hazards)
        self.ax2.set_aspect(aspect='auto')
        self.ax2.set_title("Click on a zone to view hazard details")
        self.ax2.axis("off")

        # Connect the click event to the heatmap
        self.cid = self.fig.canvas.mpl_connect('button_press_event', self.on_click)

        # Adjust layout to avoid overlapping and ensure equal sizing
        plt.subplots_adjust(left=0.05, right=0.95, wspace=0.3)
        plt.show()

    # Function to disconnect the click event if needed
    def disconnect_click_event(self):
        if self.cid is not None:
            self.fig.canvas.mpl_disconnect(self.cid)
            self.cid = None


if __name__ == "__main__":
    visualizer = ConstructionHazardVisualizer()
    visualizer.draw()

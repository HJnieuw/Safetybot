import matplotlib.pyplot as plt
from PIL import Image

# Initialize a dictionary to store zone data
zone_id = {}

# Load and display the image
image_path = "C:/Users/HJnie/Documents/TU student/BT 2024-2025/CORE/Schemas/Overview.png"
img = Image.open(image_path)
fig, ax = plt.subplots()
ax.imshow(img)
plt.axis('off')

# Event handler for mouse click
def onclick(event):
    # Check if the click is within the image boundaries
    if event.xdata is not None and event.ydata is not None:
        plt.close(fig)
        x, y = int(event.xdata), int(event.ydata)
        print(f'Coordinates: ({x}, {y})')

        # Get user input for zone details
        zone_name = input("Enter zone name: ")
        zone_activity = input("Enter activity: ")
        ppe_necessity = input("Enter PPE: ")
        risk_factor = input("Enter risk factor: ")

        # Store the data
        zone_id[zone_name] = {
            'location': [x, y],
            'activity': zone_activity,
            'PPE': ppe_necessity,
            'risk': risk_factor
        }

        # Save the data to a file
        with open('zones.txt', 'w') as file:
            for name, data in zone_id.items():
                file.write(f"{name}: {data}\n")

    else:
        print("Click inside the image area!")

# Connect click event to handler
fig.canvas.mpl_connect('button_press_event', onclick)

# Display the image
plt.show()
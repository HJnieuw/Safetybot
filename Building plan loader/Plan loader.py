import matplotlib.pyplot as plt
from matplotlib.backend_bases import MouseButton
from PIL import Image

# Initialize an empty dictionary to hold the targets
zone_id = {}

# Load the image
image_path = "C:/Users/HJnie/Documents/TU student/BT 2024-2025/CORE/Schemas/Overview.png"
img = Image.open(image_path)

# Create a figure and axis to display the image
fig, ax = plt.subplots()
ax.imshow(img)
plt.axis('off')

# Define the event handling function
def onclick(event):
    # Check if the left mouse button was clicked
    if event.button is MouseButton.LEFT:
        x, y = int(event.xdata), int(event.ydata)
        print(f'Coordinates: ({x}, {y})')

        # Prompt user for details about the zone
        zone_name = input("Enter name for this zone: ")
        zone_activity = input("Enter the activity for this zone: ")
        ppe_necessity = input("What PPE is necessary: ")
        risk_factor = input("Give the risk factor for this zone: ")

        # Store the data in the dictionary
        zone_id[zone_name] = {
            'location': [x, y],
            'zone_activity': zone_activity,
            'ppe_necessity': ppe_necessity,
            'risk_factor': risk_factor
        }

        # Save the data to a file
        with open('targets.txt', 'w') as file:
            for name, data in zone_id.items():
                file.write(f"{name} = {{'location': {data['location']}, 'zone_activity': '{data['zone_activity']}', "
                           f"'ppe_necessity': '{data['ppe_necessity']}', 'risk_factor': '{data['risk_factor']}'}}\n")

# Connect the click event to the figure's canvas
cid = fig.canvas.mpl_connect('button_press_event', onclick)

# Display the image
plt.show()

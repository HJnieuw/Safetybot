import matplotlib.pyplot as plt
from PIL import Image

# Initialize an empty dictionary to hold the targets
zone_id = {}

# Function to be called when the mouse is clicked
def onclick(event):
    # Check if the click is within the image axes
    if event.inaxes is not None:
        # Get coordinates
        x, y = int(event.xdata), int(event.ydata)
        
        print(f'coordinates: ({x: .2f}, {y: .2f})')

        # Ask user for a name and additional variables
        zone_name = input("Enter name for this zone: ")
        zone_activity = input("Enter the activity for this zone: ")
        ppe_necessity = input("What PPE is necessery: ")
        risk_factor = input("Give the risk factor for this zone: ")

        
        # Store the coordinates and additional info in the dictionary
        zone_id[zone_name] = {'location': [x, y], 'zone_activity': zone_activity, "ppe_necessity": ppe_necessity, "risk_factor": risk_factor}

# Load the image
image_path = "C:/Users/HJnie/Documents/TU student/BT 2024-2025/CORE/Schemas/Overview.png"  # Change to your image path
img = Image.open(image_path)
plt.imshow(img)
plt.axis('off')  # Turn off axis numbers and ticks

# Connect the click event
cid = plt.gcf().canvas.mpl_connect('button_press_event', onclick)

# Show the image
plt.show()

# Save the targets to a text file
with open('targets.txt', 'w') as file:
    for name, data in zone_id.items():
        file.write(f"{name} = {{'location': {data['location']}, 'zone_activity': '{data['zone_activity']}', 'ppe_necessity': {data['ppe_necessity']}, 'risk_factor': {data['risk_factor']}}}\n")


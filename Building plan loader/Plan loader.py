import matplotlib.pyplot as plt
from PIL import Image

# Initialize an empty dictionary to hold the targets
zone_id = {}

# Function to be called when the mouse is clicked
def onclick(event):
    if event.inaxes is not None:
        x, y = int(event.xdata), int(event.ydata)
        print(f'Coordinates: ({x}, {y})')
        zone_name = input("Enter name for this zone: ")
        zone_activity = input("Enter the activity for this zone: ")
        ppe_necessity = input("What PPE is necessary: ")
        risk_factor = input("Give the risk factor for this zone: ")
        
        zone_id[zone_name] = {
            'location': [x, y], 
            'zone_activity': zone_activity, 
            'ppe_necessity': ppe_necessity, 
            'risk_factor': risk_factor
        }

# Load the image
image_path = "C:/Users/HJnie/Documents/TU student/BT 2024-2025/CORE/Schemas/Overview.png"
img = Image.open(image_path)

# Create a figure and axis to display the image
fig, ax = plt.subplots()
ax.imshow(img)
plt.axis('off')

# Connect the click event to the figure's canvas
cid = fig.canvas.mpl_connect('button_press_event', onclick)

# Use non-blocking plt.show() to avoid the event loop issue
plt.show(block=False)

# After collecting input, save the data to a file
with open('targets.txt', 'w') as file:
    for name, data in zone_id.items():
        file.write(f"{name} = {{'location': {data['location']}, 'zone_activity': '{data['zone_activity']}', "
                   f"'ppe_necessity': '{data['ppe_necessity']}', 'risk_factor': '{data['risk_factor']}'}}\n")

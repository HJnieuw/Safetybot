import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
from PIL import Image, ImageTk
import os
import json

# Set the specific path for the zone_id.txt file
ZONE_ID_FILE_PATH = "Safetybot\zone_id.txt"  # Change this path to your desired location

# Initialize the main application window
class ZoneApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Zone Coordinate Picker")
        
        self.zone_id = self.load_existing_data()

        # Load image button
        self.load_button = tk.Button(root, text="Load Image", command=self.load_image)
        self.load_button.pack()

        # Canvas to display image
        self.canvas = tk.Canvas(root)
        self.canvas.pack()

        # Labels to display coordinates
        self.coord_label = tk.Label(root, text="Coordinates: (x, y)")
        self.coord_label.pack()

        # Zone details entry with labels
        tk.Label(root, text="Zone Name:").pack()
        self.zone_name_entry = tk.Entry(root, width=30)
        self.zone_name_entry.pack()

        tk.Label(root, text="Activity:").pack()
        self.zone_activity_entry = tk.Entry(root, width=30)
        self.zone_activity_entry.pack()

        tk.Label(root, text="PPE Necessary:").pack()
        self.ppe_entry = tk.Entry(root, width=30)
        self.ppe_entry.pack()

        tk.Label(root, text="Risk Factor:").pack()
        self.risk_factor_entry = tk.Entry(root, width=30)
        self.risk_factor_entry.pack()

        # Submit button
        self.submit_button = tk.Button(root, text="Submit Zone Details", command=self.submit_details)
        self.submit_button.pack()

    def load_existing_data(self):
        # Load existing data from the specified file
        if os.path.exists(ZONE_ID_FILE_PATH):
            with open(ZONE_ID_FILE_PATH, 'r') as file:
                try:
                    return json.load(file)  # Load existing data as a dictionary
                except json.JSONDecodeError:
                    return {}  # Return empty if there is a decode error
        return {}  # Return empty if file doesn't exist

    def load_image(self):
        # Load an image file
        file_path = filedialog.askopenfilename()
        if file_path:
            self.image = Image.open(file_path)
            self.tk_image = ImageTk.PhotoImage(self.image)

            # Adjust the canvas size to the image size
            self.canvas.config(width=self.image.width, height=self.image.height)
            self.canvas.create_image(0, 0, anchor=tk.NW, image=self.tk_image)

            # Bind the click event to get coordinates
            self.canvas.bind("<Button-1>", self.get_coordinates)

    def get_coordinates(self, event):
        # Get coordinates when the canvas is clicked
        x, y = event.x, event.y
        self.x, self.y = x, y  # Store coordinates for later use
        self.coord_label.config(text=f"Coordinates: ({self.x}, {self.y})")  # Update the label

    def submit_details(self):
        # Get details from entries and store them
        zone_name = self.zone_name_entry.get().strip()
        zone_activity = self.zone_activity_entry.get().strip()
        ppe_necessity = self.ppe_entry.get().strip()
        risk_factor = self.risk_factor_entry.get().strip()

        # Check if zone name is already present
        if zone_name in self.zone_id:
            messagebox.showwarning("Warning", "Zone name already exists! Please choose a different name.")
            return

        # Prepare the data to be saved in a structured format
        zone_data = {
            "location": [self.x, self.y],
            "zone_activity": zone_activity,  # Changed to a single value instead of a list
            "PPE_necessity": ppe_necessity,  # Changed to a single value instead of a list
            "risk_factor": float(risk_factor),  # Convert to float for storage
            "credits": len(self.zone_id) + 1  # Increment credits based on existing zones
        }

        # Add the new zone data to the dictionary
        self.zone_id[zone_name] = zone_data

        # Write all zone data back to the specified file
        with open(ZONE_ID_FILE_PATH, 'w') as file:
            json.dump(self.zone_id, file, indent=4)  # Write in JSON format

        # Print the stored data
        print("Zone details stored successfully:")
        print(self.zone_id)

# Create the main window
root = tk.Tk()
app = ZoneApp(root)
root.mainloop()

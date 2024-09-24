import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
from PIL import Image, ImageTk
import os

# Initialize the main application window
class ZoneApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Zone Coordinate Picker")
        
        self.zone_id = {}

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

        # Load button
        self.load_data_button = tk.Button(root, text="Load Data", command=self.load_data)
        self.load_data_button.pack()

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
        zone_name = self.zone_name_entry.get()
        zone_activity = self.zone_activity_entry.get()
        ppe_necessity = self.ppe_entry.get()
        risk_factor = self.risk_factor_entry.get()

        # Prepare the data to be saved
        zone_data = {zone_name: {"location": [self.x, self.y],"zone_activity": zone_activity,"PPE_necessity": ppe_necessity,"risk_factor": float(risk_factor),"credits": 1}}

        # Append the data to zone_id.txt
        with open('Safetybot\zone_id.txt', 'a') as file:
            file.write(f"{zone_data}\n")

        # Print the stored data
        print("Zone details stored successfully:")
        print(zone_data)

    def load_data(self):
        # Load the zone_id data from zone_id.txt
        if os.path.exists('zone_id.txt'):
            with open('zone_id.txt', 'r') as file:
                data = file.readlines()
            messagebox.showinfo("Success", "Zone data loaded successfully!")
            print("Loaded Zone Data:")
            for line in data:
                print(line.strip())  # Print each line without the newline character
        else:
            messagebox.showwarning("Warning", "No saved data found!")

# Create the main window
root = tk.Tk()
app = ZoneApp(root)
root.mainloop()

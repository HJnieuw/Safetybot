import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
from PIL import Image, ImageTk
import os
import json

# Initialize the main application window
class ZoneApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Zone Coordinate Picker")

        self.zone_id = {}
        self.x, self.y = None, None  # Initialize coordinates
        self.zone_dot = None  # To store the current zone dot ID on canvas
        self.zone_text = None  # To store the current zone name text ID on canvas

        # Create frames for better layout
        self.frame_top = tk.Frame(root)
        self.frame_top.pack(pady=10)

        self.frame_bottom = tk.Frame(root)
        self.frame_bottom.pack(pady=10)

        # Load image button
        self.load_button = tk.Button(self.frame_top, text="Load Image", command=self.load_image)
        self.load_button.grid(row=0, column=0, padx=5)

        # Canvas to display image
        self.canvas = tk.Canvas(self.frame_top)
        self.canvas.grid(row=1, column=0, columnspan=2)

        # Labels to display coordinates
        self.coord_label = tk.Label(self.frame_bottom, text="Coordinates: (x, y)")
        self.coord_label.pack()

        # Zone details entry with labels
        tk.Label(self.frame_bottom, text="Zone Name:").pack()
        self.zone_name_entry = tk.Entry(self.frame_bottom, width=30)
        self.zone_name_entry.pack()

        tk.Label(self.frame_bottom, text="Activity:").pack()
        self.zone_activity_entry = tk.Entry(self.frame_bottom, width=30)
        self.zone_activity_entry.pack()

        tk.Label(self.frame_bottom, text="PPE Necessary:").pack()
        self.ppe_entry = tk.Entry(self.frame_bottom, width=30)
        self.ppe_entry.pack()

        tk.Label(self.frame_bottom, text="Risk Factor:").pack()
        self.risk_factor_entry = tk.Entry(self.frame_bottom, width=30)
        self.risk_factor_entry.pack()

        # Submit button
        self.submit_button = tk.Button(self.frame_bottom, text="Submit Zone Details", command=self.submit_details)
        self.submit_button.pack(pady=5)

        # Listbox for displaying zones
        self.zone_listbox = tk.Listbox(self.frame_bottom, width=50, height=10)
        self.zone_listbox.pack(pady=5)
        self.zone_listbox.bind('<<ListboxSelect>>', self.load_selected_zone)

        # Edit and Delete buttons
        self.edit_button = tk.Button(self.frame_bottom, text="Edit Zone", command=self.edit_zone)
        self.edit_button.pack(pady=5)

        self.delete_button = tk.Button(self.frame_bottom, text="Delete Zone", command=self.delete_zone)
        self.delete_button.pack(pady=5)

        # Initialize empty zone data
        self.load_data()

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
        self.x, self.y = event.x, event.y  # Store coordinates for later use
        self.coord_label.config(text=f"Coordinates: ({self.x}, {self.y})")  # Update the label
        
        # Draw a dot at the clicked location
        self.draw_zone_dot()

    def draw_zone_dot(self):
        # Remove previous dot and text if they exist
        if self.zone_dot:
            self.canvas.delete(self.zone_dot)
        if self.zone_text:
            self.canvas.delete(self.zone_text)

        # Draw a new dot at the current coordinates
        radius = 5
        self.zone_dot = self.canvas.create_oval(
            self.x - radius, self.y - radius, self.x + radius, self.y + radius,
            fill="red", outline="black"
        )

        # Draw the zone name text slightly below the dot
        zone_name = self.zone_name_entry.get().strip()
        if zone_name:
            self.zone_text = self.canvas.create_text(
                self.x, self.y + 10, text=zone_name, fill="black", anchor=tk.N
            )

    def submit_details(self):
        # Get details from entries and validate
        zone_name = self.zone_name_entry.get().strip()
        zone_activity = self.zone_activity_entry.get().strip()
        ppe_necessity = self.ppe_entry.get().strip()
        risk_factor = self.risk_factor_entry.get().strip()

        if self.x is None or self.y is None:
            messagebox.showwarning("Warning", "Please click on the image to select coordinates.")
            return

        if not zone_name:
            messagebox.showerror("Error", "Zone name cannot be empty.")
            return

        try:
            risk_factor_float = float(risk_factor)
        except ValueError:
            messagebox.showerror("Error", "Risk factor must be a number.")
            return

        if zone_name not in self.zone_id: # New zone
            credits = len(self.zone_id) + 1
        else:
            credits = self.zone_id[zone_name].get("credits", 1) # Keep current credits if zone exists


        # Prepare the data to be saved
        zone_data = {
            "location": [self.x, self.y],
            "zone_activity": zone_activity,
            "PPE_necessity": ppe_necessity,
            "risk_factor": risk_factor_float,
            "credits": credits
        }

        self.zone_id[zone_name] = zone_data
        self.update_zone_listbox()

        # Save all zones to file
        self.save_data()

        # Clear the input fields
        self.clear_fields()

    def load_data(self):
        # Load the zone_id data from zone_id.json
        file_path = os.path.join('Safetybot', 'zone_id.json')
        if os.path.exists(file_path):
            with open(file_path, 'r') as file:
                self.zone_id = json.load(file)
            self.update_zone_listbox()
            messagebox.showinfo("Success", "Zone data loaded successfully!")
        else:
            messagebox.showwarning("Warning", "No saved data found!")

    def save_data(self):
        # Save the zone_id data to zone_id.json
        file_path = os.path.join('Safetybot', 'zone_id.json')
        with open(file_path, 'w') as file:
            json.dump(self.zone_id, file, indent=4)

    def update_zone_listbox(self):
        # Update the listbox with current zone names
        self.zone_listbox.delete(0, tk.END)
        for zone_name in self.zone_id.keys():
            self.zone_listbox.insert(tk.END, zone_name)

    def load_selected_zone(self, event):
        # Load details of the selected zone into the entry fields
        selected_index = self.zone_listbox.curselection()
        if selected_index:
            zone_name = self.zone_listbox.get(selected_index)
            zone_details = self.zone_id[zone_name]

            self.zone_name_entry.delete(0, tk.END)
            self.zone_name_entry.insert(0, zone_name)
            self.zone_activity_entry.delete(0, tk.END)
            self.zone_activity_entry.insert(0, zone_details["zone_activity"])
            self.ppe_entry.delete(0, tk.END)
            self.ppe_entry.insert(0, zone_details["PPE_necessity"])
            self.risk_factor_entry.delete(0, tk.END)
            self.risk_factor_entry.insert(0, zone_details["risk_factor"])
            self.x, self.y = zone_details["location"]
            self.coord_label.config(text=f"Coordinates: ({self.x}, {self.y})")
            
            # Draw the dot on the loaded coordinates and show the zone name
            self.draw_zone_dot()

    def edit_zone(self):
        # Edit the selected zone
        selected_index = self.zone_listbox.curselection()
        if selected_index:
            zone_name = self.zone_listbox.get(selected_index)
            self.submit_details()  # Save edited details with the same zone name

    def delete_zone(self):
        # Delete the selected zone
        selected_index = self.zone_listbox.curselection()
        if selected_index:
            zone_name = self.zone_listbox.get(selected_index)
            confirm = messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete '{zone_name}'?")
            if confirm:
                del self.zone_id[zone_name]
                self.update_zone_listbox()
                self.save_data()  # Update the file after deletion
                self.clear_fields()  # Clear fields after deletion

    def clear_fields(self):
        self.zone_name_entry.delete(0, tk.END)
        self.zone_activity_entry.delete(0, tk.END)
        self.ppe_entry.delete(0, tk.END)
        self.risk_factor_entry.delete(0, tk.END)
        self.coord_label.config(text="Coordinates: (x, y)")
        self.x, self.y = None, None  # Reset coordinates
        
        # Clear the dot and text from canvas
        if self.zone_dot:
            self.canvas.delete(self.zone_dot)
        if self.zone_text:
            self.canvas.delete(self.zone_text)

# Create the main window
root = tk.Tk()
app = ZoneApp(root)
root.mainloop()

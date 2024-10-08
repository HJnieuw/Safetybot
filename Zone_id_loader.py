import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog, ttk
from PIL import Image, ImageTk
import os
import json

class ZoneApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Zone Coordinate Picker")

        self.zone_id = {}
        self.x, self.y = None, None
        self.zone_dot = None
        self.zone_text = None
        self.image_path = None  # Store the image path
        self.max_width = 400  # Set a maximum width for the image
        self.max_height = 400  # Set a maximum height for the image

        # Create frames for layout
        self.frame_top = tk.Frame(root)
        self.frame_top.pack(pady=10)
        self.frame_bottom = tk.Frame(root)
        self.frame_bottom.pack(pady=10)

        # Load image button
        self.load_button = tk.Button(self.frame_top, text="Load Image", command=self.load_image)
        self.load_button.grid(row=0, column=0, padx=5)

        # Canvas for displaying the image
        self.canvas = tk.Canvas(self.frame_top)
        self.canvas.grid(row=1, column=0, columnspan=2)

        # Coordinate label
        self.coord_label = tk.Label(self.frame_bottom, text="Coordinates: (x, y)")
        self.coord_label.pack()

        # Zone details entry with dropdown for activities
        tk.Label(self.frame_bottom, text="Zone Name:").pack()
        self.zone_name_entry = tk.Entry(self.frame_bottom, width=30)
        self.zone_name_entry.pack()

        tk.Label(self.frame_bottom, text="Activity:").pack()
        self.activity_combobox = ttk.Combobox(self.frame_bottom, width=27)
        self.activity_combobox['values'] = ['Welding', 'Brick laying', 'Carpentry']  # Example activities
        self.activity_combobox.pack()

        tk.Label(self.frame_bottom, text="PPE Necessary:").pack()
        self.ppe_button = tk.Button(self.frame_bottom, text="Select PPE", command=self.select_ppe)
        self.ppe_button.pack()

        self.ppe_display_label = tk.Label(self.frame_bottom, text="Selected PPE: None")
        self.ppe_display_label.pack()

        tk.Label(self.frame_bottom, text="Risk Factor:").pack()
        self.risk_factor_entry = tk.Entry(self.frame_bottom, width=30)
        self.risk_factor_entry.pack()

        # Submit button
        self.submit_button = tk.Button(self.frame_bottom, text="Submit Zone Details", command=self.submit_details)
        self.submit_button.pack(pady=5)

        # Delete button
        self.delete_button = tk.Button(self.frame_bottom, text="Delete Selected Zone", command=self.delete_zone)
        self.delete_button.pack(pady=5)

        # Listbox to display zones
        self.zone_listbox = tk.Listbox(self.frame_bottom, width=50, height=10)
        self.zone_listbox.pack(pady=5)
        self.zone_listbox.bind('<<ListboxSelect>>', self.load_selected_zone)

        # Initialize empty zone data
        self.load_data()

        # To hold selected PPE items
        self.selected_ppe = []

    def load_image(self, image_path=None):
        # Load an image file
        if image_path is None:  # If no path is provided, ask for a file
            self.image_path = filedialog.askopenfilename()
        else:  # Use the provided image path
            self.image_path = image_path
        
        if self.image_path:
            print(f"Image path loaded: {self.image_path}")
            self.image = Image.open(self.image_path)

            # Resize image if it's too large
            self.image = self.resize_image(self.image)

            self.tk_image = ImageTk.PhotoImage(self.image)

            # Adjust the canvas size to the image size
            self.canvas.config(width=self.image.width, height=self.image.height)
            self.canvas.create_image(0, 0, anchor=tk.NW, image=self.tk_image)

            # Bind the click event to get coordinates
            self.canvas.bind("<Button-1>", self.get_coordinates)
      
    def resize_image(self, image):
        original_width, original_height = image.size
        aspect_ratio = original_width / original_height

        if original_width > self.max_width or original_height > self.max_height:
            if aspect_ratio > 1:
                self.new_width = self.max_width
                self.new_height = int(self.max_width / aspect_ratio)
            else:
                self.new_height = self.max_height
                self.new_width = int(self.max_height * aspect_ratio)

            # Calculate the scaling factor for future use
            self.scale_factor_x = original_width / self.new_width
            self.scale_factor_y = original_height / self.new_height

            return image.resize((self.new_width, self.new_height), Image.Resampling.LANCZOS)
        else:
            self.new_width, self.new_height = original_width, original_height
            self.scale_factor_x = 1
            self.scale_factor_y = 1  # No scaling if the image fits within max dimensions
            return image

    def get_coordinates(self, event):
        # Get coordinates relative to the resized image
        self.x, self.y = event.x, event.y

        # Convert the coordinates back to the original image size using the scaling factor
        self.x_full = int(self.x * self.scale_factor_x)
        self.y_full = int(self.y * self.scale_factor_y)

        # Display coordinates (in original image size) in the label
        self.coord_label.config(text=f"Coordinates: ({self.x_full}, {self.y_full})")

        # Draw the dot on the resized image for visual feedback
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

    def select_ppe(self):
        # Open a new window to select multiple PPE items
        ppe_window = tk.Toplevel(self.root)
        ppe_window.title("Select PPE")

        # Sample PPE items
        ppe_items = ['Gloves', 'Helmet', 'Goggles', 'Mask', 'Safety Shoes', 'Respirator']
        self.ppe_var = tk.Variable(value=self.selected_ppe)

        # Create a listbox for PPE selection
        self.ppe_listbox = tk.Listbox(ppe_window, selectmode=tk.MULTIPLE)
        for item in ppe_items:
            self.ppe_listbox.insert(tk.END, item)
        self.ppe_listbox.pack(padx=10, pady=10)

        # Select previously chosen items
        for ppe in self.selected_ppe:
            if ppe in ppe_items:
                index = ppe_items.index(ppe)
                self.ppe_listbox.select_set(index)

        # Button to confirm selection
        confirm_button = tk.Button(ppe_window, text="Confirm", command=lambda: self.confirm_ppe_selection(ppe_window))
        confirm_button.pack(pady=5)

    def confirm_ppe_selection(self, window):
        # Get selected PPE items and update the label
        selected_indices = self.ppe_listbox.curselection()
        self.selected_ppe = [self.ppe_listbox.get(i) for i in selected_indices]
        self.ppe_display_label.config(text=f"Selected PPE: {', '.join(self.selected_ppe) if self.selected_ppe else 'None'}")
        window.destroy()  # Close the PPE selection window

    def submit_details(self):
        # Get details from entries
        zone_name = self.zone_name_entry.get().strip()
        zone_activity = self.activity_combobox.get().strip()
        ppe_necessity = ', '.join(self.selected_ppe)  # Join selected PPE for saving
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

        if zone_name not in self.zone_id:  # New zone
            credits = sum(1 for key in self.zone_id)
        else:
            credits = self.zone_id[zone_name].get("credits", 1)  # Keep current credits if zone exists

        # Prepare the data to be saved
        zone_data = {
            "location": [self.x_full, self.y_full],
            "zone_activity": zone_activity,
            "PPE_necessity": ppe_necessity,
            "risk_factor": risk_factor_float,
            "credits": credits,
            "floorplan": self.image_path,
            "amount of hazards": 0,
            "hazard type": []
        }

        # Save the zone data
        self.zone_id[zone_name] = zone_data

        self.update_zone_listbox()
        self.save_data()
        self.clear_fields()

    def delete_zone(self):
        # Delete the selected zone
        selected_zone = self.zone_listbox.get(tk.ACTIVE)
        if selected_zone in self.zone_id:
            del self.zone_id[selected_zone]  # Remove the zone from the dictionary
            self.update_zone_listbox()  # Update the Listbox display
            self.save_data()  # Save the updated data
            self.clear_fields()  # Clear the input fields
            messagebox.showinfo("Info", f"Zone '{selected_zone}' has been deleted.")

    def load_selected_zone(self, event):
        selected_zone = self.zone_listbox.get(self.zone_listbox.curselection())

        if selected_zone in self.zone_id:
            zone_data = self.zone_id[selected_zone]

            self.zone_name_entry.delete(0, tk.END)
            self.zone_name_entry.insert(0, selected_zone)

            self.activity_combobox.set(zone_data.get("zone_activity", ""))

            self.selected_ppe = zone_data.get("PPE_necessity", "").split(", ")
            self.ppe_display_label.config(text=f"Selected PPE: {', '.join(self.selected_ppe) if self.selected_ppe else 'None'}")

            self.risk_factor_entry.delete(0, tk.END)
            self.risk_factor_entry.insert(0, zone_data.get("risk_factor", ""))

            self.image_path = zone_data.get("floorplan", "")
            self.load_image(self.image_path)

            # Retrieve full-size coordinates
            self.x_full, self.y_full = zone_data["location"]

            # Convert full-size coordinates to resized image coordinates using the scaling factor
            self.x = int(self.x_full / self.scale_factor_x)
            self.y = int(self.y_full / self.scale_factor_y)

            # Update the label to show the original coordinates
            self.coord_label.config(text=f"Coordinates: ({self.x_full}, {self.y_full})")

            # Draw the dot on the resized image
            self.draw_zone_dot()

    def update_zone_listbox(self):
        # Update Listbox with zone names
        self.zone_listbox.delete(0, tk.END)
        for zone in self.zone_id:
            self.zone_listbox.insert(tk.END, zone)

    def save_data(self):
        # Save the zone data to a JSON file
        with open("Zone_id.json", "w") as json_file:
            json.dump(self.zone_id, json_file, indent=4)

    def load_data(self):
        # Load the zone data from a JSON file
        json_file_path = "Zone_id.json"
        if os.path.exists(json_file_path):
            with open(json_file_path, "r") as json_file:
                self.zone_id = json.load(json_file)
            self.update_zone_listbox()

    def clear_fields(self):
        # Clear all input fields and reset state
        self.zone_name_entry.delete(0, tk.END)
        self.activity_combobox.set('')
        self.ppe_display_label.config(text="Selected PPE: None")
        self.selected_ppe = []
        self.risk_factor_entry.delete(0, tk.END)
        self.coord_label.config(text="Coordinates: (x, y)")
        self.x, self.y = None, None

        if self.zone_dot:
            self.canvas.delete(self.zone_dot)
        if self.zone_text:
            self.canvas.delete(self.zone_text)
        self.zone_dot = None
        self.zone_text = None

class ZoneOverview:
    def __init__(self, root):
        self.root = root
        self.root.title("Zone Coordinate Picker")

        self.zone_id = {}
        self.image_path = None  # Store the image path
        self.max_width = 400  # Set a maximum width for the image
        self.max_height = 400  # Set a maximum height for the image
        self.scale_factor_x, self.scale_factor_y = 1, 1  # Initialize scale factors

        # Create frames for layout
        self.frame_top = tk.Frame(root)
        self.frame_top.pack(pady=10)

        # Canvas for displaying the image
        self.canvas = tk.Canvas(self.frame_top)
        self.canvas.grid(row=0, column=0)

        # Frame for displaying zone information
        self.info_frame = tk.Frame(self.frame_top, padx=10)
        self.info_frame.grid(row=0, column=1, sticky="n")

        # Create labels for zone information
        self.zone_name_label = tk.Label(self.info_frame, text="Zone Name: N/A")
        self.zone_name_label.pack(anchor=tk.W)

        self.risk_factor_label = tk.Label(self.info_frame, text="Risk Factor: N/A")
        self.risk_factor_label.pack(anchor=tk.W)

        self.ppe_label = tk.Label(self.info_frame, text="PPE Necessity: N/A")
        self.ppe_label.pack(anchor=tk.W)

        self.location_label = tk.Label(self.info_frame, text="Location: N/A")
        self.location_label.pack(anchor=tk.W)

        self.activity_label = tk.Label(self.info_frame, text="Activity: N/A")
        self.activity_label.pack(anchor=tk.W)

        # Load zone data on startup
        self.load_data()

    def load_image(self, image_path=None):
        # Load an image file
        if image_path is None:  # If no path is provided, ask for a file
            self.image_path = filedialog.askopenfilename()
        else:  # Use the provided image path
            self.image_path = image_path

        if self.image_path:
            try:
                self.image = Image.open(self.image_path)

                # Resize image if it's too large
                self.image = self.resize_image(self.image)

                self.tk_image = ImageTk.PhotoImage(self.image)

                # Adjust the canvas size to the image size
                self.canvas.config(width=self.image.width, height=self.image.height)
                self.canvas.create_image(0, 0, anchor=tk.NW, image=self.tk_image)

                # Draw all zones on the canvas
                self.draw_all_zones()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load image: {e}")

    def draw_all_zones(self):
        for zone_name, zone_data in self.zone_id.items():
            # Retrieve coordinates and draw dot for each zone
            x_full, y_full = zone_data["location"]

            # Convert full-size coordinates to resized image coordinates using the scaling factor
            x_resized = int(x_full / self.scale_factor_x)
            y_resized = int(y_full / self.scale_factor_y)

            # Draw the zone dot and bind click event
            self.draw_zone_dot(x_resized, y_resized, zone_name, zone_data)

    def draw_zone_dot(self, x, y, zone_name, zone_data):
        # Draw a dot at the given coordinates
        radius = 5
        zone_dot = self.canvas.create_oval(
            x - radius, y - radius, x + radius, y + radius,
            fill="red", outline="black"
        )

        # Draw an invisible clickable area around the dot
        clickable_radius = 15  # This will define the clickable area radius
        clickable_area = self.canvas.create_oval(
            x - clickable_radius, y - clickable_radius, 
            x + clickable_radius, y + clickable_radius,
            fill="", outline=""  # Transparent fill and outline
        )

        # Draw the zone name text slightly below the dot
        self.canvas.create_text(
            x, y + 10, text=zone_name, fill="black", anchor=tk.N
        )

        # Bind the larger clickable area to show zone information on click
        self.canvas.tag_bind(clickable_area, "<Button-1>", lambda event: self.show_zone_info(zone_data, zone_name))

    def show_zone_info(self, zone_data, zone_name):
        """ Display zone information in the dedicated info area. """
        self.zone_name_label.config(text=f"Zone Name: {zone_name}")  # Use zone_name directly
        self.risk_factor_label.config(text=f"Risk Factor: {zone_data.get('risk_factor', 'N/A')}")
        self.ppe_label.config(text=f"PPE Necessity: {zone_data.get('PPE_necessity', 'N/A')}")
        self.location_label.config(text=f"Location: {zone_data.get('location', 'N/A')}")
        self.activity_label.config(text=f"Activity: {zone_data.get('zone_activity', 'N/A')}")

    def resize_image(self, image):
        original_width, original_height = image.size
        aspect_ratio = original_width / original_height

        if original_width > self.max_width or original_height > self.max_height:
            if aspect_ratio > 1:
                new_width = self.max_width
                new_height = int(self.max_width / aspect_ratio)
            else:
                new_height = self.max_height
                new_width = int(self.max_height * aspect_ratio)

            # Calculate the scaling factor for future use
            self.scale_factor_x = original_width / new_width
            self.scale_factor_y = original_height / new_height

            return image.resize((new_width, new_height), Image.Resampling.LANCZOS)
        else:
            self.scale_factor_x = 1
            self.scale_factor_y = 1  # No scaling if the image fits within max dimensions
            return image

    def load_data(self):
        # Load the zone data from a JSON file
        json_file_path = "Zone_id.json"
        if os.path.exists(json_file_path):
            with open(json_file_path, "r") as json_file:
                self.zone_id = json.load(json_file)

            # Load the image path from the first zone for demonstration purposes
            if self.zone_id:
                first_zone_data = list(self.zone_id.values())[0]
                self.load_image(first_zone_data.get("floorplan", ""))


# To prevent auto-launching the app when imported as a module
if __name__ == "__main__":
    root = tk.Tk()
    app = ZoneApp(root)
    root.mainloop()

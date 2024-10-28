import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk
import os
import json

# Display for adjusting zone information (plan, coordinates, activity, required PPE)
class ZoneApp:

    # Create display
    def __init__(self, root):
        self.root = root
        self.root.title("Zone Coordinate Picker")
        self.zone_id = {}
        self.x, self.y = None, None
        self.zone_dot = None
        self.zone_text = None
        self.image_path = None
        self.max_width = 400  
        self.max_height = 400  

        # Create main frames
        self.frame_main = tk.Frame(root)
        self.frame_main.pack(pady=10, padx=10, expand=True, fill=tk.BOTH)

        # Frame for the left side (image)
        self.frame_left = tk.Frame(self.frame_main)
        self.frame_left.grid(row=0, column=0, padx=10, pady=10)

        # Frame for the right side (coordinates and listbox)
        self.frame_right = tk.Frame(self.frame_main)
        self.frame_right.grid(row=0, column=1, padx=10, pady=10)

        # Load image button
        self.load_button = tk.Button(self.frame_left, text="Load Construction Site Plan", command=self.load_image, bg="white", bd=0.5, highlightbackground="gray", width=30)
        self.load_button.pack(pady=0)

        # Canvas for displaying the image
        self.canvas = tk.Canvas(self.frame_left)
        self.canvas.pack(pady=10)

        # Coordinates label
        self.coord_label = tk.Label(self.frame_right, text="Coordinates: (x, y)")
        self.coord_label.grid(row=0, column=0, sticky='w')  # Align left at the top

        # Listbox 
        self.zone_listbox = tk.Listbox(self.frame_right, width=40, height=10)
        self.zone_listbox.grid(row=1, column=0, padx=0, pady=10)
        self.zone_listbox.bind('<<ListboxSelect>>', self.load_selected_zone)

        # Zone name entry
        tk.Label(self.frame_right, text="Zone Name:").grid(row=2, column=0, sticky='w')
        self.zone_name_entry = tk.Entry(self.frame_right, width=25, bd=1)
        self.zone_name_entry.grid(row=2, column=0, pady=5, padx=5, sticky= "e")

        # Activity combobox
        tk.Label(self.frame_right, text="Activity:").grid(row=4, column=0, sticky='w')
        self.activity_combobox = ttk.Combobox(self.frame_right, width=22)
        self.activity_combobox['values'] = ['Welding', 'Brick laying', 'Carpentry']
        self.activity_combobox.grid(row=4, column=0, pady=5, padx=5, sticky="e")

        # PPE button and display
        tk.Label(self.frame_right, text="Required PPE:").grid(row=5, column=0, sticky='w')
        self.ppe_button = tk.Button(self.frame_right, text="Select", command=self.select_ppe, bg="white", bd=0.5, highlightbackground="gray", width=21) 
        self.ppe_button.grid(row=5, column=0, pady=5, padx=5, sticky="e")      
        self.ppe_display_label = tk.Label(self.frame_right, text="", anchor='w')  # Text will show selected PPE items
        self.ppe_display_label.grid(row=6, column=0, pady=5, padx=5, sticky='w')

        # Frame for submit and delete buttons
        self.submit_delete_frame = tk.Frame(self.frame_right)
        self.submit_delete_frame.grid(row=8, column=0, pady=10)

        # Submit button
        self.submit_button = tk.Button(self.submit_delete_frame, text="Submit Zone Details", command=self.submit_details, bg="white", bd=0.5, highlightbackground="gray")
        self.submit_button.grid(row=0, column=1, padx=6, sticky= "e")

        # Delete button
        self.delete_button = tk.Button(self.submit_delete_frame, text="Delete Zone Details", command=self.delete_zone, bg="white", bd=0.5, highlightbackground="gray")
        self.delete_button.grid(row=0, column=0, padx=5, sticky="w")

        # Load data from JSON 
        self.load_data()

        # List for selected PPE
        self.selected_ppe = []

    # Load image of construction site plan
    def load_image(self, image_path=None):
       
        if image_path is None:  
            self.image_path = filedialog.askopenfilename()
        else:  
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

    # Resize image
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

            self.scale_factor_x = original_width / self.new_width
            self.scale_factor_y = original_height / self.new_height
            return image.resize((self.new_width, self.new_height), Image.Resampling.LANCZOS)
        else:
            self.new_width, self.new_height = original_width, original_height
            self.scale_factor_x = 1
            self.scale_factor_y = 1
            return image

    # Determine zone coordinates by clicking on image
    def get_coordinates(self, event):
        self.x, self.y = event.x, event.y
        self.x_full = int(self.x * self.scale_factor_x)
        self.y_full = int(self.y * self.scale_factor_y)
        self.coord_label.config(text=f"Coordinates: ({self.x_full}, {self.y_full})")
        self.draw_zone_dot()

    # Create dot on image
    def draw_zone_dot(self):
        if self.zone_dot:
            self.canvas.delete(self.zone_dot)
        if self.zone_text:
            self.canvas.delete(self.zone_text)

        radius = 5
        self.zone_dot = self.canvas.create_oval(
            self.x - radius, self.y - radius, self.x + radius, self.y + radius,
            fill="darkred", outline="black")
        
        zone_name = self.zone_name_entry.get().strip()
        if zone_name:
            self.zone_text = self.canvas.create_text(
                self.x, self.y + 10, text=zone_name, fill="black", anchor=tk.N
            )

    # Select required PPE
    def select_ppe(self):
        ppe_window = tk.Toplevel(self.root)
        ppe_window.title("Select required PPE")

        ppe_items = ['Gloves', 'Helmet', 'Goggles', 'Mask', 'Safety Shoes', 'Respirator']
        self.ppe_var = tk.Variable(value=self.selected_ppe)

        self.ppe_listbox = tk.Listbox(ppe_window, selectmode=tk.MULTIPLE)
        for item in ppe_items:
            self.ppe_listbox.insert(tk.END, item)
        self.ppe_listbox.pack(padx=10, pady=10)

        for ppe in self.selected_ppe:
            if ppe in ppe_items:
                index = ppe_items.index(ppe)
                self.ppe_listbox.select_set(index)

        confirm_button = tk.Button(ppe_window, text="Confirm", command=lambda: self.confirm_ppe_selection(ppe_window))
        confirm_button.pack(pady=5)

    # Confirm PPE selection
    def confirm_ppe_selection(self, window):
        selected_indices = self.ppe_listbox.curselection()
        self.selected_ppe = [self.ppe_listbox.get(i) for i in selected_indices]
        self.ppe_display_label.config(text=f"{', '.join(self.selected_ppe) if self.selected_ppe else ''}")
        window.destroy()

    # Submit details (per zone)
    def submit_details(self):
        zone_name = self.zone_name_entry.get().strip()
        zone_activity = self.activity_combobox.get().strip()
        required_PPE = ', '.join(self.selected_ppe)

        if self.x is None or self.y is None:
            messagebox.showwarning("Warning", "Please click on the image to select coordinates.")
            return

        if not zone_name:
            messagebox.showerror("Error", "Zone name cannot be empty.")
            return
        
        # Create parameters for the JSON file 
        zone_data = {
            "location": [self.x_full, self.y_full],
            "floorplan": self.image_path,
            "zone_activity": zone_activity,
            "required_PPE": required_PPE,
            "amount_of_hazards": 0,
            "hazard_type": []
        }

        self.zone_id[zone_name] = zone_data
        self.update_zone_listbox()
        self.save_data()
        self.clear_fields()

    # Delete zone 
    def delete_zone(self):
        selected_zone = self.zone_listbox.get(tk.ACTIVE)
        if selected_zone in self.zone_id:
            del self.zone_id[selected_zone]
            self.update_zone_listbox()
            self.save_data()
            self.clear_fields()
            messagebox.showinfo("Info", f"Zone '{selected_zone}' has been deleted.")

    # Load selected zone with details
    def load_selected_zone(self, event):
        selected_zone = self.zone_listbox.get(self.zone_listbox.curselection())

        if selected_zone in self.zone_id:
            zone_data = self.zone_id[selected_zone]

            self.zone_name_entry.delete(0, tk.END)
            self.zone_name_entry.insert(0, selected_zone)

            self.activity_combobox.set(zone_data.get("zone_activity", ""))

            self.selected_ppe = zone_data.get("required_PPE", "").split(", ")
            self.ppe_display_label.config(text=f"{', '.join(self.selected_ppe) if self.selected_ppe else ''}")

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

    # Update zone details
    def update_zone_listbox(self):
        self.zone_listbox.delete(0, tk.END)
        for zone in self.zone_id:
            self.zone_listbox.insert(tk.END, zone)

    # save JSON file
    def save_data(self):
        with open("zone_ID.json", "w") as json_file:
            json.dump(self.zone_id, json_file, indent=4)

    # update JSON file
    def load_data(self):
        json_file_path = "zone_ID.json"
        if os.path.exists(json_file_path):
            with open(json_file_path, "r") as json_file:
                self.zone_id = json.load(json_file)
            self.update_zone_listbox()

    def clear_fields(self):
        self.zone_name_entry.delete(0, tk.END)
        self.activity_combobox.set('')
        self.ppe_display_label.config(text="")
        self.selected_ppe = []
        self.coord_label.config(text="Coordinates: (x, y)")
        self.x, self.y = None, None

        if self.zone_dot:
            self.canvas.delete(self.zone_dot)
        if self.zone_text:
            self.canvas.delete(self.zone_text)
        self.zone_dot = None
        self.zone_text = None

# Display with an overview of information per zone
class ZoneOverview:
    # Create display
    def __init__(self, root):
        self.root = root
        self.root.title("Zone Overview")
        self.zone_id = {}
        self.image_path = None  
        self.max_width = 400 
        self.max_height = 400  
        self.scale_factor_x, self.scale_factor_y = 1, 1 

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
        self.zone_name_label = tk.Label(self.info_frame, text="Zone Name: ")
        self.zone_name_label.pack(anchor=tk.W)

        self.location_label = tk.Label(self.info_frame, text="Location: ")
        self.location_label.pack(anchor=tk.W)

        self.activity_label = tk.Label(self.info_frame, text="Activity: ")
        self.activity_label.pack(anchor=tk.W)

        self.ppe_label = tk.Label(self.info_frame, text="Required PPE: ")
        self.ppe_label.pack(anchor=tk.W)

        # Load zone data on startup
        self.load_data()

    # Load the image 
    def load_image(self, image_path=None):
      
        if image_path is None: 
            self.image_path = filedialog.askopenfilename()
        else: 
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

    # Draw clickable dot for each zone
    def draw_all_zones(self):
        for zone_name, zone_data in self.zone_id.items():
            # Retrieve coordinates and draw dot for each zone
            x_full, y_full = zone_data["location"]

            # Convert full-size coordinates to resized image coordinates using the scaling factor
            x_resized = int(x_full / self.scale_factor_x)
            y_resized = int(y_full / self.scale_factor_y)

            # Draw the zone dot and bind click event
            self.draw_zone_dot(x_resized, y_resized, zone_name, zone_data)
    
    # Create clickable dot on image 
    def draw_zone_dot(self, x, y, zone_name, zone_data):
        radius = 5
        zone_dot = self.canvas.create_oval(
            x - radius, y - radius, x + radius, y + radius,
            fill="red", outline="black")
        
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

    # show zone information when clicked on a dot
    def show_zone_info(self, zone_data, zone_name):
        """ Display zone information in the dedicated info area. """
        self.zone_name_label.config(text=f"Zone Name: {zone_name}") 
        self.location_label.config(text=f"Location: {zone_data.get('location', 'N/A')}")
        self.activity_label.config(text=f"Activity: {zone_data.get('zone_activity', 'N/A')}")
        self.ppe_label.config(text=f"Required PPE: {zone_data.get('required_PPE', 'N/A')}")

    # resize image
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

    # Load zone data from a JSON file
    def load_data(self):
        json_file_path = "zone_ID.json"
        if os.path.exists(json_file_path):
            with open(json_file_path, "r") as json_file:
                self.zone_id = json.load(json_file)

            # Load the image path from the first zone for demonstration purposes
            if self.zone_id:
                first_zone_data = list(self.zone_id.values())[0]
                self.load_image(first_zone_data.get("floorplan", ""))

# Run the script correctly
if __name__ == "__main__":
    root = tk.Tk()
    app = ZoneApp(root)
    root.mainloop()

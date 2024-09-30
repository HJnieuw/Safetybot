import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog, ttk
from PIL import Image, ImageTk
import os
import json

#Hidde is een sukkel

class ZoneApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Zone Coordinate Picker")

        self.zone_id = {}
        self.x, self.y = None, None
        self.zone_dot = None
        self.zone_text = None
        self.image_path = None  # Store the image path
        self.max_width = 800  # Set a maximum width for the image
        self.max_height = 600  # Set a maximum height for the image

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

    def load_image(self):
        # Load an image file
        self.image_path = filedialog.askopenfilename()
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
        # Scale the image down if it's larger than the max width or height
        original_width, original_height = image.size
        aspect_ratio = original_width / original_height

        # Determine new width and height, keeping aspect ratio
        if original_width > self.max_width or original_height > self.max_height:
            if aspect_ratio > 1:
                # Image is wider than tall
                new_width = self.max_width
                new_height = int(self.max_width / aspect_ratio)
            else:
                # Image is taller than wide
                new_height = self.max_height
                new_width = int(self.max_height * aspect_ratio)
            return image.resize((new_width, new_height), Image.ANTIALIAS)
        else:
            return image

    def get_coordinates(self, event):
        # Get coordinates when the canvas is clicked
        self.x, self.y = event.x, event.y  # Store coordinates for later use
        self.coord_label.config(text=f"Coordinates: ({self.x}, {self.y})")  # Update the label
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
        ppe_items = ['Gloves', 'Helmet', 'Goggles', 'Mask', 'Safety Shoes']
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
            credits = len(self.zone_id) + 1
        else:
            credits = self.zone_id[zone_name].get("credits", 1)  # Keep current credits if zone exists

        # Prepare the data to be saved
        zone_data = {
            "location": [self.x, self.y],
            "zone_activity": zone_activity,
            "PPE_necessity": ppe_necessity,
            "risk_factor": risk_factor_float,
            "credits": credits
        }

        # Save the zone data and image path
        self.zone_id[zone_name] = zone_data

        if self.image_path:  # Ensure that the image path is not None
            print(f"Saving image path: {self.image_path}")  # Debugging
            self.zone_id["image_path"] = self.image_path

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
        # Load zone details when selected from the Listbox
        try:
            selected_zone = self.zone_listbox.get(self.zone_listbox.curselection())
        except tk.TclError:
            return

        if selected_zone in self.zone_id:
            zone_data = self.zone_id[selected_zone]

            self.zone_name_entry.delete(0, tk.END)
            self.zone_name_entry.insert(0, selected_zone)

            self.activity_combobox.set(zone_data.get("zone_activity", ""))

            self.selected_ppe = zone_data.get("PPE_necessity", "").split(", ")
            self.ppe_display_label.config(text=f"Selected PPE: {', '.join(self.selected_ppe) if self.selected_ppe else 'None'}")

            self.risk_factor_entry.delete(0, tk.END)
            self.risk_factor_entry.insert(0, zone_data.get("risk_factor", ""))

            self.x, self.y = zone_data["location"]
            self.coord_label.config(text=f"Coordinates: ({self.x}, {self.y})")
            self.draw_zone_dot()

    def update_zone_listbox(self):
        # Update Listbox with zone names
        self.zone_listbox.delete(0, tk.END)
        for zone in self.zone_id:
            if zone != "image_path":  # Exclude the image path key
                self.zone_listbox.insert(tk.END, zone)

    def save_data(self):
        # Save the zone data to a JSON file
        with open("Safetybot\zone_id.json", "w") as json_file:
            json.dump(self.zone_id, json_file, indent=4)

    def load_data(self):
        # Load the zone data from a JSON file
        if os.path.exists("Safetybot\zone_id.json"):
            with open("Safetybot\zone_id.json", "r") as json_file:
                self.zone_id = json.load(json_file)
                image_path = self.zone_id.get("image_path")

                if image_path and os.path.exists(image_path):
                    # Reload the image if path exists
                    self.image_path = image_path
                    self.image = Image.open(self.image_path)

                    # Resize image if it's too large
                    self.image = self.resize_image(self.image)

                    self.tk_image = ImageTk.PhotoImage(self.image)
                    self.canvas.config(width=self.image.width, height=self.image.height)
                    self.canvas.create_image(0, 0, anchor=tk.NW, image=self.tk_image)

                    self.canvas.bind("<Button-1>", self.get_coordinates)

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

if __name__ == "__main__":
    root = tk.Tk()
    app = ZoneApp(root)
    root.mainloop()

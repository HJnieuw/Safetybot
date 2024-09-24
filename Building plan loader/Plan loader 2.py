import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import os
import json

# Initialize the main application window
class ZoneApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Zone Coordinate Picker")

        self.zone_id = {}
        self.start_x, self.start_y = None, None  # Start coordinates for bounding box
        self.rect = None  # Rectangle object on the canvas

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
        self.coord_label = tk.Label(self.frame_bottom, text="Bounding Box: (x1, y1) to (x2, y2)")
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

        # Load button
        self.load_data_button = tk.Button(self.frame_bottom, text="Load Data", command=self.load_data)
        self.load_data_button.pack(pady=5)

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

            # Bind mouse events to create bounding box
            self.canvas.bind("<ButtonPress-1>", self.start_draw)
            self.canvas.bind("<B1-Motion>", self.draw_rectangle)
            self.canvas.bind("<ButtonRelease-1>", self.end_draw)

    def start_draw(self, event):
        # Record the starting coordinates for the bounding box
        self.start_x, self.start_y = event.x, event.y
        # Create a rectangle on the canvas
        self.rect = self.canvas.create_rectangle(self.start_x, self.start_y, self.start_x, self.start_y, outline="red")

    def draw_rectangle(self, event):
        # Update the rectangle coordinates while dragging
        self.canvas.coords(self.rect, self.start_x, self.start_y, event.x, event.y)
        self.coord_label.config(text=f"Bounding Box: ({self.start_x}, {self.start_y}) to ({event.x}, {event.y})")

    def end_draw(self, event):
        # Finalize the rectangle and store coordinates
        self.end_x, self.end_y = event.x, event.y
        self.coord_label.config(text=f"Bounding Box: ({self.start_x}, {self.start_y}) to ({self.end_x}, {self.end_y})")

    def submit_details(self):
        # Get details from entries and validate
        zone_name = self.zone_name_entry.get().strip()
        zone_activity = self.zone_activity_entry.get().strip()
        ppe_necessity = self.ppe_entry.get().strip()
        risk_factor = self.risk_factor_entry.get().strip()

        if self.start_x is None or self.start_y is None or self.end_x is None or self.end_y is None:
            messagebox.showwarning("Warning", "Please draw a bounding box on the image.")
            return

        try:
            risk_factor_float = float(risk_factor)
        except ValueError:
            messagebox.showerror("Error", "Risk factor must be a number.")
            return

        # Prepare the data to be saved
        zone_data = {
            "location": [self.start_x, self.start_y, self.end_x, self.end_y],
            "zone_activity": zone_activity,
            "PPE_necessity": ppe_necessity,
            "risk_factor": risk_factor_float,
            "credits": 1
        }

        self.zone_id[zone_name] = zone_data
        self.update_zone_listbox()

        # Save all zones to file
        self.save_data()

        # Clear the input fields and refresh bounding box
        self.clear_fields()

        # Refresh the bounding box on the canvas
        self.canvas.delete(self.rect)  # Remove the existing rectangle
        self.start_x, self.start_y, self.end_x, self.end_y = None, None, None, None  # Reset coordinates
        self.coord_label.config(text="Bounding Box: (x1, y1) to (x2, y2)")  # Reset label

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
        # Load selected zone data into entry fields
        selected_zone_index = self.zone_listbox.curselection()
        if selected_zone_index:
            zone_name = self.zone_listbox.get(selected_zone_index)
            zone_data = self.zone_id[zone_name]
            self.zone_name_entry.delete(0, tk.END)
            self.zone_name_entry.insert(0, zone_name)
            self.zone_activity_entry.delete(0, tk.END)
            self.zone_activity_entry.insert(0, zone_data['zone_activity'])
            self.ppe_entry.delete(0, tk.END)
            self.ppe_entry.insert(0, zone_data['PPE_necessity'])
            self.risk_factor_entry.delete(0, tk.END)
            self.risk_factor_entry.insert(0, zone_data['risk_factor'])

            # Set bounding box coordinates
            self.start_x, self.start_y, self.end_x, self.end_y = zone_data['location']
            self.coord_label.config(text=f"Bounding Box: ({self.start_x}, {self.start_y}) to ({self.end_x}, {self.end_y})")

            # Draw the bounding box on the canvas
            self.canvas.delete("all")  # Clear existing canvas
            self.canvas.create_image(0, 0, anchor=tk.NW, image=self.tk_image)  # Re-draw image
            self.rect = self.canvas.create_rectangle(self.start_x, self.start_y, self.end_x, self.end_y, outline="red")

    def edit_zone(self):
        # Functionality to edit selected zone details
        selected_zone_index = self.zone_listbox.curselection()
        if selected_zone_index:
            zone_name = self.zone_listbox.get(selected_zone_index)
            self.submit_details()  # Reuse submit_details for editing
            self.clear_fields()

    def delete_zone(self):
        # Functionality to delete selected zone
        selected_zone_index = self.zone_listbox.curselection()
        if selected_zone_index:
            zone_name = self.zone_listbox.get(selected_zone_index)
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
        self.coord_label.config(text="Bounding Box: (x1, y1) to (x2, y2)")
        self.start_x, self.start_y, self.end_x, self.end_y = None, None, None, None  # Reset coordinates

# Create the main window
root = tk.Tk()
app = ZoneApp(root)
root.mainloop()

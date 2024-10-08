# Scripts
import Zone_id_loader as Zil

# Packages
import tkinter as tk
import Zone_id_loader as Zil
import os
import json

class RobotApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Robot Control Panel")

        # Create the label
        self.label = tk.Label(root, text="=== Robot Control Panel ===", font=("Arial", 16))
        self.label.pack(pady=10)

        # Create buttons for each menu option
        self.button_status = tk.Button(root, text="Robot Status", command=self.robot_status, width=30)
        self.button_status.pack(pady=5)

        self.button_start = tk.Button(root, text="Start Robot", command=self.start_robot, width=30)
        self.button_start.pack(pady=5)

        self.button_stop = tk.Button(root, text="Stop Robot", command=self.stop_robot, width=30)
        self.button_stop.pack(pady=5)

        self.button_pause = tk.Button(root, text="Pause Robot", command=self.pause_robot, width=30)
        self.button_pause.pack(pady=5)

        self.button_change_zone = tk.Button(root, text="Change Zone_ID", command=self.change_zone, width=30)
        self.button_change_zone.pack(pady=5)

        self.button_show_info = tk.Button(root, text="Show Zone Information", command=self.show_zone_information, width=30)
        self.button_show_info.pack(pady=5)

        self.button_import_plan = tk.Button(root, text="Import New Site Plan", command=self.import_site_plan, width=30)
        self.button_import_plan.pack(pady=5)

        self.button_exit = tk.Button(root, text="Exit", command=root.quit, width=30)
        self.button_exit.pack(pady=5)

        # Text area for showing status and information
        self.info_area = tk.Text(root, height=10, width=50, state=tk.DISABLED)
        self.info_area.pack(pady=10)

    def robot_status(self):
        self.display_message("Robot Status: [Status details go here]")

    def start_robot(self):
        self.display_message("Robot started.")

    def stop_robot(self):
        self.display_message("Robot stopped.")

    def pause_robot(self):
        self.display_message("Robot paused.")

    def change_zone(self):
        self.display_message("Change Zone_ID: [Zone change details go here]")

    def show_zone_information(self):
        zone_id_file = 'Zone_id.json'
        if os.path.exists(zone_id_file) and os.path.getsize(zone_id_file) > 0:
            with open(zone_id_file, 'r') as file:
                data = json.load(file)
                zone_info = "\n=== Zone Information ===\n"
                for zone, details in data.items():
                    zone_info += f"Zone: {zone}\nDetails: {details}\n\n"
                self.display_message(zone_info)
        else:
            self.display_message("No zone data available. Please update the zone file.")

    def import_site_plan(self):
        new_window = tk.Toplevel(self.root)
        app = Zil.ZoneApp(new_window)

    def display_message(self, message):
        self.info_area.config(state=tk.NORMAL)
        self.info_area.delete(1.0, tk.END)  # Clear previous content
        self.info_area.insert(tk.END, message)
        self.info_area.config(state=tk.DISABLED)

# Create the main Tkinter window
root = tk.Tk()

# Create an instance of RobotApp
app = RobotApp(root)

# Start the Tkinter main loop
root.mainloop()
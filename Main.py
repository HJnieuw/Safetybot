# Importing packages
import tkinter as tk

# Importing modules
import Zone_id_loader as Zil
import Dashboard as db  # Assuming this contains the ConstructionHazardVisualizer


class RobotApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Robot Control Panel")

        # Create the label
        self.label = tk.Label(root, text="Robot Control Panel", font=("Arial", 16))
        self.label.pack(pady=10)

        # Create buttons for each menu option
        self.create_buttons()

        # Text area for showing status and information
        self.info_area = tk.Text(root, height=10, width=50, state=tk.DISABLED)
        self.info_area.pack(pady=10)

    def create_buttons(self):
        button_options = [
            ("Robot Status", self.robot_status),
            ("Start Robot", self.start_robot),
            ("Stop Robot", self.stop_robot),
            ("Pause Robot", self.pause_robot),
            ("Show Zone Hazards", self.show_hazards),
            ("Show Zone Information", self.show_zone_information),
            ("Import New Site Plan", self.import_site_plan),
            ("Exit", self.root.quit)
        ]

        for (text, command) in button_options:
            button = tk.Button(self.root, text=text, command=command, width=30)
            button.pack(pady=5)

    def robot_status(self):
        self.display_message("Robot Status: The robot is active and can still operate for 119 minutes.")

    def start_robot(self):
        self.display_message("Robot started.")

    def stop_robot(self):
        self.display_message("Robot stopped.")

    def pause_robot(self):
        self.display_message("Robot paused.")

    def show_hazards(self):
        # Create an instance of ConstructionHazardVisualizer and draw the visualization
        visualizer = db.ConstructionHazardVisualizer()
        visualizer.draw()  # Call draw on the instance

    def show_zone_information(self):
        new_window = tk.Toplevel(self.root)
        app = Zil.ZoneOverview(new_window)

    def import_site_plan(self):
        new_window = tk.Toplevel(self.root)
        app = Zil.ZoneApp(new_window)

    def display_message(self, message):
        self.info_area.config(state=tk.NORMAL)
        self.info_area.delete(1.0, tk.END)  # Clear previous content
        self.info_area.insert(tk.END, message)
        self.info_area.config(state=tk.DISABLED)

# Create the main Tkinter window
if __name__ == "__main__":
    root = tk.Tk()
    app = RobotApp(root)
    root.mainloop()

import tkinter as tk            # Standard Pyhton library for GUI
import zone_ID_loader as Zil    # Import our own zone_ID_loader script
import dashboard as db          # Import our own dashboard script to visualise the hazards 
import subprocess               # Used open a terminal and type commands

# Create rounded button-like shapes for the GUI
class RoundedButton(tk.Canvas):
    def __init__(self, parent, text, command=None, width=250, **kwargs):
        tk.Canvas.__init__(self, parent, width=width, height=50, **kwargs)      
        self.command = command
        self.text = text
        self.rect = self.create_rounded_rectangle(5, 5, width - 5, 45, radius=20, fill="#7296bd", outline="#252526")
        self.label = self.create_text(width / 2, 25, text=self.text, fill="#252526", font=("Arial", 12, "bold"))

        self.bind("<Button-1>", self.on_click)
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)

    # Drawing the rounded triangles for buttons
    def create_rounded_rectangle(self, x1, y1, x2, y2, radius=25, **kwargs): 
        points = [
            x1 + radius, y1,
            x1 + radius, y1,
            x2 - radius, y1,
            x2 - radius, y1,
            x2, y1,
            x2, y1 + radius,
            x2, y1 + radius,
            x2, y2 - radius,
            x2, y2 - radius,
            x2, y2,
            x2 - radius, y2,
            x2 - radius, y2,
            x1 + radius, y2,
            x1 + radius, y2,
            x1, y2,
            x1, y2 - radius,
            x1, y2 - radius,
            x1, y1 + radius,
            x1, y1 + radius,
            x1, y1
        ]
        return self.create_polygon(points, smooth=True, **kwargs)

    # Executes the command related to the button when it is clicked
    def on_click(self, event):
        if self.command:
            self.command()

    # Changes the buttons color when the mouse hoovers over it
    def on_enter(self, event):
        self.itemconfig(self.rect, fill="#86b0de")

    # Reverts the buttons color when the mouse leaves again
    def on_leave(self, event):
        self.itemconfig(self.rect, fill="#7296bd")

# Set up the main app window and its components
class RobotApp:
    def __init__(self, root):
        self.root = root
        self.root.title("") # Sets up window title

        # Set the initial size of the window
        self.root.geometry("600x300")

        # Set background color 
        self.root.config(bg="#f3f3f3")

        # Center the content by configuring columns to stretch equally
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=1)

        # Create the label with black text and a blue background
        self.label = tk.Label(root, text="Robot Control Panel", font=("Arial", 16), fg="#252526", bg="#f3f3f3")
        self.label.grid(row=0, column=0, columnspan=2, pady=20)

        # Create buttons for each menu option
        self.create_buttons()

    # Adds buttons to the main app window
    def create_buttons(self):
        # Creating buttons using the custom RoundedButton class
        button_width = 280  # Set button width to ensure they are properly aligned

        button_import_plan = RoundedButton(self.root, text="Import New Site Plan", command=self.import_site_plan, width=button_width, highlightthickness=0)
        button_import_plan.grid(row=1, column=0, padx=10, pady=10)

        button_show_info = RoundedButton(self.root, text="Show Zone Information", command=self.show_zone_information, width=button_width,  highlightthickness=0)
        button_show_info.grid(row=1, column=1, padx=10, pady=10)

        button_robot_settings = RoundedButton(self.root, text="Robot Settings", command=self.robot_settings, width=button_width,  highlightthickness=0)
        button_robot_settings.grid(row=2, column=0, padx=10, pady=10)

        button_show_hazards = RoundedButton(self.root, text="Show Zone Hazards", command=self.show_hazards, width=button_width,  highlightthickness=0)
        button_show_hazards.grid(row=2, column=1, padx=10, pady=10)

        # START button with similar style but occupying both columns and centered
        button_start = RoundedButton(self.root, text="START", command=self.start_robot, width=(button_width * 2) + 20, highlightthickness=0)
        button_start.grid(row=3, column=0, columnspan=2, padx=10, pady=20)

    # Opens new window for robot settings
    def robot_settings(self):
        new_window = tk.Toplevel(self.root)
        new_window.title("Robot Settings")
        # Additional content for the settings window can be added here

    # Opens new window for dashboard information (dashboard.py)
    def show_hazards(self):
        # Create an instance of ConstructionHazardVisualizer and draw the visualization
        visualizer = db.ConstructionHazardVisualizer() # import our own dashboard.py script
        visualizer.draw()  # Draw it

    # Opens new window for zone information (zone_ID_loader.py)
    def show_zone_information(self):
        new_window = tk.Toplevel(self.root) 
        app = Zil.ZoneOverview(new_window) # Import our own Zone_ID_loader.py script

    # Opens new window to import a site plan
    def import_site_plan(self):
        new_window = tk.Toplevel(self.root)
        app = Zil.ZoneApp(new_window)

    # Run script haxard_detection.py when pressing start
    def start_robot(self):
        """Function to start the robot by running the hazard_detection.py script."""
        try:
            # Call the hazard_detection.py script as a subprocess
            subprocess.Popen(["python", "hazard_detection.py"])
            print("Robot started successfully!")
        except Exception as e:
            print(f"Error starting the robot: {e}")

# Create the main Tkinter window
if __name__ == "__main__":
    root = tk.Tk()          # Create main window
    app = RobotApp(root)    # Calls main app window
    root.mainloop()         # Starts main loop to listen for user interactions with the app

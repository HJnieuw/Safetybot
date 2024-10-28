import tkinter as tk
from tkinter import ttk
import cv2
from PIL import Image, ImageTk
from ultralytics import YOLO
import json
from datetime import datetime
from robot_path import simulate_robot_path

# Include your existing functions here
# ... [load_json, save_json, calculate_overlap, etc.] ...

class HazardDetectionApp:
    def __init__(self, root, model_path='best_helmet.pt', zone_id_file='zone_ID_sim.json'):
        self.root = root
        self.root.title("Hazard Detection SAFETYBOT")
        
        # Load YOLO model
        self.model = YOLO(model_path)
        
        # Load zone data
        self.zone_data = load_json(zone_id_file)
        
        # Initialize video capture
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            print("Error: Cannot open camera")
            self.root.destroy()
            return
        
        # Initialize variables
        self.hazard_detection_active = False
        self.detected_hazards = None
        self.active_zone = None
        self.window_open = False
        
        # Create GUI elements
        self.video_label = ttk.Label(root)
        self.video_label.pack()
        
        self.status_label = ttk.Label(root, text="Initializing...", font=("Helvetica", 14))
        self.status_label.pack()
        
        self.quit_button = ttk.Button(root, text="Quit", command=self.quit_app)
        self.quit_button.pack()
        
        # Start simulation
        self.robot_positions = simulate_robot_path()
        self.position_index = 0
        
        # Start the update loop
        self.update_video()
    
    def quit_app(self):
        self.cap.release()
        self.root.destroy()
    
    def update_video(self):
        if self.position_index >= len(self.robot_positions):
            self.position_index = 0  # Restart simulation or handle as needed
        
        robot_pose = self.robot_positions[self.position_index]
        self.position_index += 1
        
        # Process robot position
        self.hazard_detection_active, self.active_zone, self.detected_hazards = processing_robot_position(
            robot_pose, self.zone_data, self.hazard_detection_active, self.active_zone, self.detected_hazards
        )
        
        # Update status label
        self.status_label.config(text=f"Robot Position: {robot_pose}\nActive Zone: {self.active_zone}")
        
        if self.hazard_detection_active:
            ret, frame = self.cap.read()
            if ret:
                # Perform hazard detection
                hazards, results = detect_hazards(frame, self.model, self.detected_hazards)
                
                # Update zone data if new hazards are detected
                data_updated = update_zone_data(self.zone_data, self.active_zone, hazards)
                if data_updated:
                    save_json('zone_ID_sim.json', self.zone_data)
                
                # Annotate frame
                if results:
                    annotated_image = results[0].plot()
                else:
                    annotated_image = frame
                
                # Convert the image to RGB and then to PIL format
                annotated_image = cv2.cvtColor(annotated_image, cv2.COLOR_BGR2RGB)
                img = Image.fromarray(annotated_image)
                imgtk = ImageTk.PhotoImage(image=img)
                self.video_label.imgtk = imgtk
                self.video_label.configure(image=imgtk)
                
                # Handle window state (optional)
                # You can add more logic here based on your requirements
        else:
            # Optionally, display a placeholder or a message when detection is inactive
            placeholder = Image.new('RGB', (640, 480), color=(0, 0, 0))
            img = Image.fromarray(cv2.cvtColor(np.array(placeholder), cv2.COLOR_BGR2RGB))
            imgtk = ImageTk.PhotoImage(image=img)
            self.video_label.imgtk = imgtk
            self.video_label.configure(image=imgtk)
        
        # Schedule the next update
        self.root.after(30, self.update_video)  # Adjust the delay as needed

# Include the rest of your functions here
# ... [load_json, save_json, calculate_overlap, etc.] ...

if __name__ == "__main__":
    root = tk.Tk()
    app = HazardDetectionApp(root)
    root.mainloop()

import cv2
from ultralytics import YOLO
import json
from datetime import datetime
import tkinter as tk
from tkinter import simpledialog

# Constants 
ZONE_ID_FILE = 'zone_ID.json'   # Path to the ZONE ID JSON file

# Load trained YOLO model
model = YOLO('best_helmet.pt')  # Path to the trained model

def load_json(path):
    """Load JSON data from the given file path"""
    with open(path, 'r') as f:
        return json.load(f)
    
def save_json(path, data):
    """Save JSON data to the given file path"""
    with open(path, 'w') as f:
        json.dump(data, f, indent=4)

def calculate_overlap(box1, box2):
    """Calculate overlap ratio between two bounding boxes"""
    x1_max = max(box1[0], box2[0])
    y1_max = max(box1[1], box2[1])
    x2_min = min(box1[2], box2[2])
    y2_min = min(box1[3], box2[3])
    overlap_area = max(0, x2_min - x1_max) * max(0, y2_min - y1_max)

    # Calculate the area of each bounding box
    box1_area = (box1[2] - box1[0]) * (box1[3] - box1[1])
    box2_area = (box2[2] - box2[0]) * (box2[3] - box2[1])
    
    if box1_area == 0 or box2_area == 0:
        return 0
    return overlap_area / min(box1_area, box2_area)

def initialize_detected_hazards():
    """Keep track of detected hazards in dictionary to avoid double logging"""
    return {"no_helmet": {}}

def process_detections(results, detected_hazards, helmet_boxes):
    """Process detection results and update the list of hazards"""
    hazards = []

    if results:
        for box in results[0].boxes:
            class_name = model.names[int(box.cls[0])]   # Get the class name ('helmet' or 'no_helmet')
            x1, y1, x2, y2 = map(int, box.xyxy[0])      # Extract bounding box coordinates 

            if box.id is not None:
                detection_id = str(int(box.id[0]))      # Extract unique ID
                
                if class_name == 'helmet':
                    helmet_boxes.append((x1, y1, x2, y2))   # Store helmet boxes
               
                elif class_name == 'no_helmet':
                    head_is_hazard = True   # Assume the head is a hazard untill proven otherwise
                    for helmet_box in helmet_boxes:
                        overlap_ratio = calculate_overlap((x1, y1, x2, y2), helmet_box)
                        if overlap_ratio > 0.8:
                            head_is_hazard = False 
                            break
                    
                    if head_is_hazard and detection_id not in detected_hazards["no_helmet"]:
                        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        hazard_warning = f"WARNING: Person without helmet detected, ID: {detection_id}, at {current_time}"

                        detected_hazards["no_helmet"][detection_id] = current_time
                        hazards.append(hazard_warning)
    return hazards

def update_zone_data(zone_data, zone_name, hazards):
    """Update the zone data with new hazards"""
    hazard_count = len(hazards)
    if hazard_count > 0:
        zone = zone_data.get(zone_name, {})

        zone["amount_of_hazards"] = zone.get("amount_of_hazards", 0) + hazard_count
        zone.setdefault("hazard_type", []).extend(hazards)

        zone_data[zone_name] = zone
        return True
    return False

def get_zone_name():
    """Get zone name using a Tkinter input dialog"""
    root = tk.Tk()
    root.withdraw()  # Hide the root window
    zone_name = simpledialog.askstring("Input", "Please enter Zone Name: ")
    return zone_name

# MAIN LOOP
def main():
    """Main loop to detect in every frame"""
    
    zone_name = get_zone_name()
    if not zone_name:
        print("No zone name entered, exiting.")
        return
    
    cap = cv2.VideoCapture(0)

    zone_data = load_json(ZONE_ID_FILE)
    detected_hazards = initialize_detected_hazards()   

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Error: failed to grab frame")
            break
    
        required_PPE = zone_data[zone_name].get("required_PPE", [])
        
        if "Helmet" in required_PPE:
            results = model.track(
                source=frame, 
                conf=0.6, 
                persist=True, 
                save=False,
                tracker='bytetrack_helmet.yaml',
                verbose=False
            )
        else:
            results = None
        
        helmet_boxes = []
        hazards = process_detections(results, detected_hazards, helmet_boxes)
        data_updated = update_zone_data(zone_data, zone_name, hazards)

        if data_updated:
            save_json(ZONE_ID_FILE, zone_data)

        if results:
            annotated_image = results[0].plot()
        else:
            annotated_image = frame  

        cv2.imshow('Hazard Detection SAFETYBOT', annotated_image)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()

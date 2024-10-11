import cv2
from ultralytics import YOLO
import json
from datetime import datetime

# Constants 
ZONE_ID_FILE = 'zone_ID2.json'   # Path to the ZONE ID JSON file
ZONE_NAME = "Zone 1"            # Name of the current zone, needs to be automated

# Load trained YOLO model
model1 = YOLO('best_helmet.pt')  # Path to the trained model
model2 = YOLO('best_hammer.pt')  # Path to the second model

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
    
    # Determine the overlap ratio
    if box1_area == 0 or box2_area == 0:
        return 0
    return overlap_area / min(box1_area, box2_area)

def initialize_detected_hazards():
    """Keep track of detected hazards in dictionary to avoid double logging"""

    return{
        "no_helmet": {},
        "hammer": {}
    }

def process_helmet_detections(results, detected_hazards, helmet_boxes):

    """Process helmet detection results and update the list of hazards"""

    # Make list to store hazards
    hazards = []

    # Process results from model if applicable
    if results:
        for box in results[0].boxes:
            class_name = model1.names[int(box.cls[0])]   # Get the class name ('helmet' or 'no_helmet')
            x1, y1, x2, y2 = map(int, box.xyxy[0])      # Extract bounding box coordinates 

            # Check if detection ID is valid
            if box.id is not None:
                detection_id = str(int(box.id[0]))      # Extract unique ID
                
                if class_name == 'helmet':
                    helmet_boxes.append((x1, y1, x2, y2))   # Store helmet boxes
               
                elif class_name == 'no_helmet':
                    head_is_hazard = True   # Assume the head is a hazard untill proven otherwise
                    # Check if the head overlaps with any helmet
                    for helmet_box in helmet_boxes:
                        overlap_ratio = calculate_overlap((x1, y1, x2, y2), helmet_box)
                        if overlap_ratio > 0.8: # More than 50% means person is wearing a helmet
                            head_is_hazard = False # Proven otherwise
                            break
                    
                    # If no helmet overlaps, log the hazard if it hasn't been logged yet
                    if head_is_hazard and detection_id not in detected_hazards["no_helmet"]:
                        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        hazard_warning = f"WARNING: Person without helmet detected, ID: {detection_id}, at {current_time}"

                        # Add to detected hazards dictionary to prevent re-logging in this run
                        detected_hazards["no_helmet"][detection_id] = current_time

                        # Append the hazard warning to update JSON
                        hazards.append(hazard_warning)
    return hazards

def process_hammer_detections(results, detected_hazards_hammers):
    """Process hammer detection results and update the list of hazards"""

    # Make list to store hammer hazards
    hammer_hazards = []

    if results:
        for box in results[0].boxes:
            class_name = model2.names[int(box.cls[0])]
            x1, y1, x2, y2 = map(int, box.xyxy[0])

            if box.id is not None:
                detection_id = str(int(box.id[0]))

                if class_name == 'hammer':
                    if detection_id not in detected_hazards_hammers:
                        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        hazard_warning = f"WARNING: Tool detected on the ground, ID: {detection_id}, at {current_time}"

                        detected_hazards_hammers[detection_id] = current_time
                        hammer_hazards.append(hazard_warning)
    return hammer_hazards

def update_zone_data(zone_data, zone_name, hazards):
    """Update the zone data with new hazards"""

    hazard_count = len(hazards)
    if hazard_count > 0:
        zone = zone_data.get(zone_name, {}) # Provides empy dictionary if the zone is not found

        # Update the amount of hazards
        zone["amount_of_hazards"] = zone.get("amount_of_hazards", 0) + hazard_count

        # Update the hazard types
        hazard_type_list = zone.setdefault("hazard_type", [])
        hazard_type_list.extend(hazards)

        # Save the updated zone data back into the main data
        zone_data[zone_name] = zone

        return True     # Indicates that the zone data was updated
    return False        # No updates made

def draw_detections(frame, results_list, model_names_list):
    """Draw bounding boxes and labels on the frame for all results in results_list"""

    for results, names in zip(results_list, model_names_list):
        if results:
            for box in results[0].boxes:
                class_id = int(box.cls[0])
                class_name = names[class_id]
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                conf = box.conf[0]
                label = f"{class_name} {conf:.2f}"

                # Choose a color for the class
                if class_name == 'helmet':
                    color = (0, 255, 0)      # Green for helmets
                elif class_name == 'no_helmet':
                    color = (0, 0, 255)      # Red for no helmet
                elif class_name == 'hammer':
                    color = (255, 0, 0)      # Blue for tools
                else:
                    color = (255, 255, 255)  # White for other classes

                # Draw rectangle
                cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
                # Draw label background
                (w, h), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
                cv2.rectangle(frame, (x1, y1 - h - 5), (x1 + w, y1), color, -1)
                # Draw label text
                cv2.putText(frame, label, (x1, y1 - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,255), 1)

# MAIN LOOP
def main():
    """Main loop to detect in every frame"""
    
    # Open webcam
    cap = cv2.VideoCapture(0)

    # Load data from JSON
    zone_data = load_json(ZONE_ID_FILE)

    # Initialize dictionary to keep track of hazards detected in this run
    detected_hazards = initialize_detected_hazards()   

    while True:
        # Capture frame-by-frame
        ret, frame = cap.read()
        if not ret:
            print("Error: failed to grab frame")
            break
    
        # Determine if helmet PPE is required in the current zone
        required_PPE = zone_data[ZONE_NAME].get("required_PPE", [])
        
        # YOLO detection and tracking
        if "Helmet" in required_PPE:
            results1 = model1.track(
                source=frame, 
                conf=0.6, 
                persist=True, 
                save=False,
                tracker= 'bytetrack_helmet.yaml',
                verbose= False
            )
        else:
            results1 = None

        results2 = model2.track(
            source=frame,
            conf = 0.6,
            persist=True,
            save=False,
            tracker='bytetrack_hammer.yaml',
            verbose=False
        )
        
        # Make list to store helmet bounding boxes
        helmet_boxes = []

        # Process detections and get new hazards
        hazards = process_helmet_detections(results1, detected_hazards, helmet_boxes)

        # Process hammer detection and get new hazards
        hammer_hazards = process_hammer_detections(results2, detected_hazards["hammer"])

        # Combine all hazards
        all_hazards = hazards + hammer_hazards

        # Update zone data if new hazards are detected
        data_updated = update_zone_data(zone_data, ZONE_NAME, all_hazards)

        # Save the JSON data only if there were updates
        if data_updated:
            save_json(ZONE_ID_FILE, zone_data)

        # Draw detections on the frame
        draw_detections(frame, [results1, results2], [model1.names, model2.names])
      
        # Display the annotated image
        cv2.imshow('Hazard Detection SAFETYBOT', frame)

        # Exit the loop if 'q' is pressed
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Release the webcam and close al windows
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()


import cv2
from ultralytics import YOLO
import json
from datetime import datetime

# Load trained models
model1 = YOLO('best_helmet.pt')  # Model for helmets and no-helmet
model2 = YOLO('best_hammer.pt')  # Model for hammers

# Open webcam
cap = cv2.VideoCapture(0)

# Define the zone where the BOT is currently located
zone_name = "Zone 2"

# Load JSON file
zone_ID = 'zone_ID2.json'
with open(zone_ID, 'r') as f:
    zone_data = json.load(f)

# Ensure "logged_detection_ids" exists for the zone
if "logged_detection_ids" not in zone_data[zone_name]:
    zone_data[zone_name]["logged_detection_ids"] = {
        "no_helmet": [],
        "hammer": []
    }

# Overlap function
def calculate_overlap(box1, box2):
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

# Main loop processing each frame
while True:
    # Capture frame-by-frame
    ret, frame = cap.read()

    if not ret:
        print("Error: Failed to grab frame.")
        break

    # Zone requires helmet detection?
    required_PPE = zone_data[zone_name]["required_PPE"]

    # YOLO tracking
    if "Helmet" in required_PPE:
        results1 = model1.track(source=frame, conf=0.25, persist=True, save=False)
    else:
        results1 = None

    results2 = model2.track(source=frame, conf=0.25, persist=True, save=False)

    # Make lists to store bboxes and total hazards
    helmet_boxes = []
    head_boxes = []
    hazards = []

    # Process results from model 1 (helmets, heads) if applicable
    if results1:
        for box in results1[0].boxes:
            class_name = model1.names[int(box.cls[0])]
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            
            # Check if detection ID is valid
            if box.id is not None:
                detection_id = str(int(box.id[0]))  # Convert detection ID to string to store in JSON

                if class_name == 'helmet':
                    helmet_boxes.append((x1, y1, x2, y2))
                elif class_name == 'no_helmet':
                    head_boxes.append((x1, y1, x2, y2))

                    # Check if head overlaps with a helmet
                    head_is_hazard = True
                    for helmet_box in helmet_boxes:
                        overlap_ratio = calculate_overlap((x1, y1, x2, y2), helmet_box)
                        if overlap_ratio > 0.5:  # More than 50% overlap means they are wearing a helmet
                            head_is_hazard = False
                            break

                    # If no helmet overlaps and the detection is not logged in JSON, log the hazard
                    if head_is_hazard and detection_id not in zone_data[zone_name]["logged_detection_ids"]["no_helmet"]:
                        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        hazard_entry = f"Person without helmet detected, ID: {detection_id}, at {current_time}"
                        hazards.append(hazard_entry)
                        zone_data[zone_name]["logged_detection_ids"]["no_helmet"].append(detection_id)
                        # Add to JSON data
                        zone_data[zone_name]["hazard_type"].append(hazard_entry)
                        zone_data[zone_name]["amount_of_hazards"] += 1

    # Process results from the second model (hammers)
    for box in results2[0].boxes:
        class_name = model2.names[int(box.cls[0])]

        # Check if detection ID is valid
        if box.id is not None:
            detection_id = str(int(box.id[0]))  # Convert detection ID to string to store in JSON

            if class_name == 'hammer':
                # If the detection is not logged in JSON, log the hazard
                if detection_id not in zone_data[zone_name]["logged_detection_ids"]["hammer"]:
                    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    hazard_entry = f"Hammer detected, ID: {detection_id}, at {current_time}"
                    hazards.append(hazard_entry)
                    zone_data[zone_name]["logged_detection_ids"]["hammer"].append(detection_id)
                    # Add to JSON data
                    zone_data[zone_name]["hazard_type"].append(hazard_entry)
                    zone_data[zone_name]["amount_of_hazards"] += 1

    # Save the updated JSON file only if new hazards are detected
    if hazards:
        with open(zone_ID, 'w') as f:
            json.dump(zone_data, f, indent=4)

    # Get the annotated image from the first and second model's results
    if results1:
        annotated_image1 = results1[0].plot()
    else:
        annotated_image1 = frame  # If helmet detection isn't needed, use the original frame
    annotated_image2 = results2[0].plot()

    # Combine the two annotated images into one (overlay results)
    combined_image = cv2.addWeighted(annotated_image1, 0.5, annotated_image2, 0.5, 0)

    # Display the combined image
    cv2.imshow('Hazard Detection', combined_image)

    # Exit the loop if 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the webcam and close all OpenCV windows
cap.release()
cv2.destroyAllWindows()

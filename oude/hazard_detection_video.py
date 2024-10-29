import cv2
from ultralytics import YOLO
import json
from datetime import datetime

# Load both YOLO models 
model1 = YOLO('best_helmet.pt')  # Model for helmets and no-helmet
model2 = YOLO('best_hammer.pt')  # Model for hammers

# Open the webcam (0 refers to the default webcam)
cap = cv2.VideoCapture(0)

# Function to calculate overlap between two bounding boxes
def calculate_overlap(box1, box2):
    x1_max = max(box1[0], box2[0])
    y1_max = max(box1[1], box2[1])
    x2_min = min(box1[2], box2[2])
    y2_min = min(box1[3], box2[3])
    overlap_area = max(0, x2_min - x1_max) * max(0, y2_min - y1_max)
    box1_area = (box1[2] - box1[0]) * (box1[3] - box1[1])
    box2_area = (box2[2] - box2[0]) * (box2[3] - box2[1])
    return overlap_area / min(box1_area, box2_area) if box1_area > 0 and box2_area > 0 else 0

# Load existing JSON file for zones
zone_ID = 'zone_ID.json'
with open(zone_ID, 'r') as f:
    zone_data = json.load(f)

# Define the zone (this can be dynamically updated based on your criteria)
zone_name = "Zone 3"

# Loop to process each frame from the webcam
while True:
    # Capture frame-by-frame
    ret, frame = cap.read()

    if not ret:
        print("Error: Failed to grab frame.")
        break

    # Check if the zone requires helmet detection
    required_PPE = zone_data[zone_name]["required_PPE"]

    if "Helmet" in required_PPE:
        # Use both models (helmets and hammers) to predict on the current frame
        results1 = model1.predict(source=frame, conf=0.25, save=False)
    else:
        # Use only hammer model when helmet is not required
        results1 = None

    results2 = model2.predict(source=frame, conf=0.25, save=False)

    # Detect possible hazards / labels (no helmets / only head AND/OR loose hammer)
    helmet_boxes = []
    head_boxes = []
    hammer_count = 0
    hazards = []

    # Process results from model 1 (helmets, heads) if applicable
    if results1:
        for box in results1[0].boxes:
            class_name = model1.names[int(box.cls[0])]
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            box_coords = (x1, y1, x2, y2)
            if class_name == 'helmet':
                helmet_boxes.append(box_coords)  # Save bounding box for helmet
            elif class_name == 'no_helmet':
                head_boxes.append(box_coords)  # Save bounding box for head

    # Process results from model 2 (hammers)
    for box in results2[0].boxes:
        class_name = model2.names[int(box.cls[0])]
        if class_name == 'hammer':
            hammer_count += 1

    # Get the current time for hazards detection
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Check if head-box overlaps with a helmet-box
    for head_box in head_boxes:
        head_is_hazard = True  # Initially, the head is a hazard
        for helmet_box in helmet_boxes:
            overlap_ratio = calculate_overlap(head_box, helmet_box)
            if overlap_ratio > 0.5:  # If more than 50% of the bounding box overlaps
                head_is_hazard = False  # The head is not a hazard
                break  # Stop if a helmet is found that overlaps

        # If no helmet overlaps, it's a hazard
        if head_is_hazard:
            hazards.append(f"1 person is not wearing their helmet at {current_time}")

    # Process results for hammers
    if hammer_count > 0:
        hazards.append(f"{hammer_count} {'loose hammer' if hammer_count == 1 else 'loose hammers'} detected at {current_time}")

    # Determine the total number of hazards
    hazard_count = len(head_boxes) + hammer_count

    # --- Update the existing zones.json with new hazards information ---

    # Update zone with new hazard info
    if zone_name in zone_data:
        # Update the amount of hazards
        if "amount_of_hazards" in zone_data[zone_name]:
            zone_data[zone_name]["amount_of_hazards"] += hazard_count  # Add to existing hazard count
        else:
            zone_data[zone_name]["amount_of_hazards"] = hazard_count  # Initialize if not present

        # Update hazard types
        if "hazard_type" in zone_data[zone_name]:
            zone_data[zone_name]["hazard_type"].extend(hazards)  # Append new hazards to the list
        else:
            zone_data[zone_name]["hazard_type"] = hazards  # Initialize if not present

    else:
        print(f"Zone {zone_name} not found in the JSON data.")

    # Save the updated JSON file
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
    cv2.imshow('YOLOv8 Combined Detection', combined_image)

    # Exit the loop if 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the webcam and close all OpenCV windows
cap.release()
cv2.destroyAllWindows()

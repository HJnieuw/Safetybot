import cv2
from ultralytics import YOLO
import json
import os
from datetime import datetime  

# Load both YOLO models 
model1 = YOLO('/Users/tombo/Documents/CORE/Safetybot/trained models/yolov8n_helmets_heads.pt')  # Model for helmets and heads
model2 = YOLO('/Users/tombo/Documents/CORE/Safetybot/trained models/yolov8n_hammer.pt')  # Model for hammers

# Load the image only once
image_path = "/Users/tombo/Documents/CORE/Safetybot/photo:video/IMG_7691.jpeg"
image = cv2.imread(image_path)  # Load the image

# Use both models to predict on the image
results1 = model1.predict(source=image, conf=0.25, save=False)
results2 = model2.predict(source=image, conf=0.25, save=False)

# Detect possible hazards / labels (no helmets / only head AND/OR loose hammer)
helmet_boxes = []
head_boxes = []
hammer_count = 0
hazards = []

# Function to calculate overlap between two bounding boxes
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

# Process results from model 1 (helmets, heads)
for box in results1[0].boxes:
    class_name = model1.names[int(box.cls[0])]
    x1, y1, x2, y2 = map(int, box.xyxy[0])
    box_coords = (x1, y1, x2, y2)
    
    if class_name == 'helmet':
        helmet_boxes.append(box_coords)  # Save bounding box for helmet
    elif class_name == 'head':
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

# After processing all heads, if any heads are hazards, append only one hazard entry with the count and time
if len(head_boxes) > 0:
    hazards.append(f"{len(head_boxes)} head(s) detected without helmet(s) at {current_time}")

# Process results for hammers (dynamically adding the count if multiple are detected)
if hammer_count > 0:
    hazards.append(f"{hammer_count} {'loose hammer' if hammer_count == 1 else 'loose hammers'} detected at {current_time}")

# Determine the total number of hazards (count individual hazards, not just descriptions)
hazard_count = len(head_boxes) + hammer_count

# --- Update the existing zones.json with new hazards information ---

# 1: load existing JSON file
zone_ID = '/Users/tombo/Documents/CORE/Safetybot/zone_ID.json'
with open(zone_ID, 'r') as f:
    zone_data = json.load(f)

# zone of hazards (DIT MOET AANPASBAAR WORDEN)
zone_name = "Zone 2"  

# 2: Add hazard information to zone_ID (Append new hazards instead of overwriting)
if zone_name in zone_data:
    if "amount of hazards" in zone_data[zone_name]:
        zone_data[zone_name]["amount of hazards"] += hazard_count  # Add to existing hazard count WILLEN WE DAT HET GETAL WORDT OPGETELS OF ERNAAST KOMT TE STAAN?
    else:
        zone_data[zone_name]["amount of hazards"] = hazard_count  # Initialize if not present
    
    if "hazard type" in zone_data[zone_name]:
        zone_data[zone_name]["hazard type"].extend(hazards)  # Append new hazards to existing list
    else:
        zone_data[zone_name]["hazard type"] = hazards  # Initialize if not present
else:
    print(f"Zone {zone_name} not found in the JSON data.")

# 3: Save new JSON file
with open(zone_ID, 'w') as f:
    json.dump(zone_data, f, indent=4)

# --- End of JSON update section ---

# # Save hazards information to an additional JSON file 
# hazard_data = {
#     "amount_of_hazards": hazard_count,
#     "hazard_types": hazards
# }

# with open('hazard_detection.json', 'w') as f:
#     json.dump(hazard_data, f, indent=4)  # indent=4 makes the JSON file more readable

# --- End of additional JSON update section ---

# Get the annotated image from the first and second model's results
annotated_image1 = results1[0].plot()
annotated_image2 = results2[0].plot()

# Combine the two annotated images into one (overlay results)
combined_image = cv2.addWeighted(annotated_image1, 0.5, annotated_image2, 0.5, 0)

# Display the combined image
cv2.imshow('YOLOv8 Combined Detection', combined_image)

# Dynamically detect the file extension and save the combined result
file_extension = os.path.splitext(image_path)[1]  # Get the file extension (e.g., .jpg, .png)
combined_image_path = image_path.replace(file_extension, f'_combined{file_extension}')  # Save with the same extension

# Save the combined result to a file (keeping the original file type)
cv2.imwrite(combined_image_path, combined_image)

# Wait for a key press and then close the image window
cv2.waitKey(0)
cv2.destroyAllWindows()

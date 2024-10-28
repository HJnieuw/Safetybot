# Pseudocode for integrating liDAR SLAM data into hazard_detection.py script

### Assumptions:
# - We have access to a Python SDK or API provided by GeoSLAM to retrieve real-time LidAR data
# - We are uising an open-source library for 3D data procssing compatible with python (open3d). See SLAMAlgorithm class
# - We do not use ROS because of different programming language
# - Zones are defined with specific boundaries within the zone_ID_lidar.json file
# - The robots onboard computer can handle the computational load or processing LIDAR data and running SLAM algorithms

# Existing imorts
import cv2
from ultralytics import YOLO
import json
from datetime import datetime

# New imports for SLAM and LiDAR data processing
# import geoslam_sdk  # Hypothetical SDK for GeoSLAM device (GeoSLAM ZEB Horizon RT Mobile Scanner)
import numpy as np
import open3d as o3d # For point cloud processing

# Constants 
ZONE_ID_FILE = 'zone_ID_lidar.json' 

# Load trained YOLO model
model = YOLO('best_helmet.pt')  # Path to the trained model

# Placeholder for the GeoSLAM scanner initialization, replace with the actual GeoSLAM SDK
# scanner = geoslam_sdk.Scanner()

# Placeholder SLAM algorithm class
class SLAMAlgorithm:
    """Defines the position of the robot"""
    def __init__(self):
        # Initialize variables and parameters
        self.map = o3d.geometry.PointCloud()
        self.previous_pose = np.identity(4)
    
    def process(self, point_cloud):
        # Convert raw data to Open3D point cloud
        current_pcd = o3d.geometry.PointCloud()
        current_pcd.points = o3d.utility.Vector3dVector(point_cloud)
        
        # Perform registration (e.g., ICP)
        threshold = 1.0  # Set an appropriate threshold
        trans_init = np.identity(4)
        reg = o3d.pipelines.registration.registration_icp(
            current_pcd, self.map, threshold, trans_init,
            o3d.pipelines.registration.TransformationEstimationPointToPoint()
        )
        
        # Update map and pose
        self.map += current_pcd.transform(reg.transformation)
        self.previous_pose = np.dot(self.previous_pose, reg.transformation)
        
        # Extract robot position from pose
        robot_position = self.previous_pose[:3, 3]
        return robot_position

# Functions
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
    """Initialize dictionary to keep track of detected hazards in this run"""

    return {"no_helmet": {}}

def process_detections(results, detected_hazards, helmet_boxes):
    """Process detection results and update the list of hazards"""

    # List to store hazards
    hazards = []

    # Process results from model if applicable
    if results:
        for box in results[0].boxes:
            class_name = model.names[int(box.cls[0])]   # Get the class name ('helmet' or 'no_helmet')
            x1, y1, x2, y2 = map(int, box.xyxy[0])      # Extract bounding box coordinates 

            # Check if detection ID is valid
            if box.id is not None:
                detection_id = str(int(box.id[0]))      # Extract unique ID

                if class_name == 'helmet':
                    helmet_boxes.append((x1, y1, x2, y2))   # Store helmet boxes

                elif class_name == 'no_helmet':
                    head_is_hazard = True   # Assume the head is a hazard until proven otherwise
                    # Check if the head overlaps with any helmet
                    for helmet_box in helmet_boxes:
                        overlap_ratio = calculate_overlap((x1, y1, x2, y2), helmet_box)
                        if overlap_ratio > 0.8:  # More than 80% overlap means person is wearing a helmet
                            head_is_hazard = False  # Proven otherwise
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

def update_zone_data(zone_data, zone_name, hazards):
    """Update the zone data with new hazards"""

    hazard_count = len(hazards)
    if hazard_count > 0:
        zone = zone_data.get(zone_name, {}) # Provides empy dictionary if the zone is not found

        # Update the amount of hazards
        zone["amount_of_hazards"] = zone.get("amount_of_hazards", 0) + hazard_count

        # Update the hazard types
        zone.setdefault("hazard_type", []).extend(hazards)

        # Save the updated zone data back into the main data
        zone_data[zone_name] = zone

        return True     # Indicates that the zone data was updated
    return False        # No updates made

def get_current_zone(robot_pose, zone_data):
    """Determine the current zone based on the robots position
    Returns a tuple: (zone_name, required_PPE)
    """
    
    # initialize robot position
    x, y, z = robot_pose

    for zone_name, zone_info in zone_data.items():
        # assume each zone has a boundary field defining its area
        boundary = zone_info.get('boundary') 

        if boundary:
            if (boundary['x_min'] <= x <= boundary['x_max'] and
                boundary['y_min'] <= y <= boundary['y_max']):

                # Get the required PPE as a list (split on commas and delete space)
                required_PPE = [p.strip() for p in zone_info.get('required_PPE', '').split(',')]

                return zone_name, required_PPE
        return None, None
    
def detect_hazards(frame, model, detected_hazards):
    """Perfrom hazard detection on the given frame
    Returns a list of detected hazards."""

    # Make a list to store helmet boudning boxes
    helmet_boxes = []

    # Yolo detection and tracking
    results = model.track(
        source = frame,
        conf = 0.6,
        persist = True,
        save = False,
        tracker = 'bytetrack_helmet.yaml',
        verbose = False
    )

    hazards = process_detections(results, detected_hazards, helmet_boxes)
    return hazards, results

# MAIN LOOP
def main():
    """Main loop to perform SLAM and hazard detection."""

    # Initialize SLAM algorithm
    slam = SLAMAlgorithm() # This is a placeholder for an actual SLAM implementation, now a class from an open-source SLAM library

    # Start LiDAR scanning, replace with actual scanner initialization
    # scanner.start_scan()

    # Open webcam for hazard detection
    cap = cv2.VideoCapture(0)

    # Load the zone data from JSON
    zone_data = load_json(ZONE_ID_FILE)

    # Keep track if hazard detection is active and initialize variables
    hazard_detection_active = False
    detected_hazards = False

    while True:
        # Step 1: Aquire Lidar Data
        # This needs to be replaced with actual data from the scanner
        # point_cloud = scanner.get_point_cloud() # Get latest point cloud data
        # Now, for proove of concept, we use a simulated pount_cloud as random data
        point_cloud = np.random.rand(1000, 3) # Placeholder for pointcloud data

        # Step 2: Perform Slam to estimate robots position
        robot_pose = slam.process(point_cloud)

        # Step 3: Determine current zone and required PPE
        current_zone, required_PPE = get_current_zone(robot_pose, zone_data)

        # Step 4: Check if helmet PPE is required
        helmet_required = 'Helmet' in required_PPE if required_PPE else False

        # Step 5: Start or stop hazard detection based on the zone and PPE requirement
        if current_zone and helmet_required:
            if not hazard_detection_active:
                print(f"S.I.M.O.H. entered {current_zone}. Starting hazard detection")
                hazard_detection_active = True
                # Initialize directory to keep track of hazards detected in zone run
                detected_hazards = initialize_detected_hazards()
        else:
            if hazard_detection_active:
                print("S.I.M.O.H. left designated Zone. Stopping hazard detection")
                hazard_detection_active = False
        
        # Step 6: If hazard detection is active, performe hazard tracking
        if hazard_detection_active:
            # Capture frame-by-frame
            ret, frame = cap.read()
            if not ret:
                print("Error: fialed to grab frame")
                break

            # Perform hezard detection
            hazards, results = detect_hazards(frame, model, detected_hazards)

            # Update zone data if new hazards are detected
            data_updated = update_zone_data(zone_data, current_zone, hazards)

            # Save the JSON data only if there were updates
            if data_updated:
                save_json(ZONE_ID_FILE, zone_data)

            # Get the annotated image
            if results:
                annotated_image = results[0].plot()
            else:
                annotated_image = frame     # Use original frame if no detection

            # Display the annotated image
            cv2.imshow('Hazard Detection SAFETYBOT', annotated_image)
        
        else:
            # Display the camera without annotations
            ret, frame = cap.read()
            if ret:
                cv2.imshow('Robot View', frame)

        # Exit the loop if 'q' is pressed
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Cleanup
    cap.release()
    cv2.destroyAllWindows()
    # scanner.stop_scan()

if __name__ == "__main__":
    main()

    



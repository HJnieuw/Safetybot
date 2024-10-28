import cv2

# Load the image
image = cv2.imread('/Users/tombo/Documents/CORE/Safetybot/S.I.M.O.H./assets/construction_site_bk.jpg')
clone = image.copy()
bounding_boxes = []

# Mouse callback function to draw rectangles
def draw_rectangle(event, x, y, flags, param):
    global x_start, y_start, drawing, image

    if event == cv2.EVENT_LBUTTONDOWN:
        # Start drawing
        drawing = True
        x_start, y_start = x, y

    elif event == cv2.EVENT_MOUSEMOVE:
        if drawing:
            # Draw the rectangle on the cloned image
            image = clone.copy()
            cv2.rectangle(image, (x_start, y_start), (x, y), (0, 255, 0), 2)

    elif event == cv2.EVENT_LBUTTONUP:
        # Finish drawing
        drawing = False
        cv2.rectangle(image, (x_start, y_start), (x, y), (0, 255, 0), 2)
        bounding_boxes.append((x_start, y_start, x, y))

# Initialize variables
drawing = False
x_start, y_start = -1, -1

# Create a window and bind the function to window
cv2.namedWindow('Manual Annotation')
cv2.setMouseCallback('Manual Annotation', draw_rectangle)

while True:
    cv2.imshow('Manual Annotation', image)
    key = cv2.waitKey(1) & 0xFF

    # Press 'r' to reset the image
    if key == ord('r'):
        image = clone.copy()
        bounding_boxes = []

    # Press 'q' to quit
    elif key == ord('q'):
        break

# Print and save the bounding boxes
print("Bounding Boxes:", bounding_boxes)
cv2.destroyAllWindows()

import json

with open('room_boundaries_manual.json', 'w') as f:
    json.dump(bounding_boxes, f)

from ultralytics import YOLO
import os

# Load your trained YOLO model
model = YOLO('/Users/tombo/Documents/CORE/Safetybot/best_helmet.pt')

# Path to the image
image_path = "/Users/tombo/Documents/CORE/Safetybot/terras.jpeg"

# Run the prediction
results = model.predict(
    source=image_path,  # Correct path
    conf=0.25,
    save=True
)

# Print the results
print(results)
results[0].show()

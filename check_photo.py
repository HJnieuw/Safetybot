from ultralytics import YOLO

model = YOLO('yolov8n.pt')

results = model.predict(
    source = "/Users/tombo/Documents/CORE/Safetybot/IMG_7691.jpeg",
    conf = 0.25,
    save = True
)

# # print for image
# print(results)
# results[0].show()

# # Save the result to custom directory
# results.save(save_dir="/path/to/custom/directory")


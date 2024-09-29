from ultralytics import YOLO

model = YOLO('yolov8n.pt')

model.train(
    data = "/Users/tombo/Documents/CORE/Safetybot/data.yaml",
    epochs = 100,
    imgsz = 640,
    batch = 16,
    workers = 4
)
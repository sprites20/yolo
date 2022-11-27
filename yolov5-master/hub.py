import torch

# Model
#model = torch.hub.load('ultralytics/yolov5', 'yolov5s')  # or yolov5n - yolov5x6, custom
model = torch.hub.load('ultralytics/yolov5', 'custom', path='yolo-preprocessing.pt', force_reload=True) 
# Images
img = "C:\\Users\\NakaMura\\Desktop\\Screenshot 2022-11-27 223302.jpg"  # or file, Path, PIL, OpenCV, numpy, list

# Inference
results = model(img)

# Results
results.save()  # or .show(), .save(), .crop(), .pandas(), etc.
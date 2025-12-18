import cv2
import numpy as np
from ultralytics import YOLO

# Load the YOLOv8-Pose model (it will download automatically the first time)
# 'yolov8n-pose.pt' is the "Nano" version: super fast.
model = YOLO('yolov8n-pose.pt')

def analyze_pose(image_path):
    """
    Reads an image and uses YOLOv8 to detect human skeletons.
    """
    try:
        # 1. Run Inference
        # conf=0.5 means we only trust detections with 50%+ confidence
        results = model(image_path, conf=0.5)

        # 2. Check if anything was found
        # results[0] is the result for the first image
        if len(results[0].keypoints) == 0:
            original_img = cv2.imread(image_path)
            return cv2.cvtColor(original_img, cv2.COLOR_BGR2RGB), "⚠️ No human skeleton detected."

        # 3. Draw the skeleton
        # plot() returns the image with boxes and skeletons drawn
        annotated_bgr = results[0].plot()

        # 4. Convert BGR to RGB for Streamlit
        annotated_rgb = cv2.cvtColor(annotated_bgr, cv2.COLOR_BGR2RGB)

        return annotated_rgb, "✅ Subject Tracked. Skeleton Extracted via YOLOv8."

    except Exception as e:
        return None, f"Error running YOLO Analysis: {str(e)}"
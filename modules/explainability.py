import cv2
import numpy as np
import torch
from ultralytics import YOLO
from pytorch_grad_cam import GradCAM, EigenCAM
from pytorch_grad_cam.utils.image import show_cam_on_image

# --- THE FIX ---
# This wrapper strips away the extra YOLO data so GradCAM only sees the tensor
class YOLOv8Wrapper(torch.nn.Module):
    def __init__(self, model):
        super(YOLOv8Wrapper, self).__init__()
        self.model = model

    def forward(self, x):
        # YOLOv8 returns a tuple/list. We only want the first element (the tensor).
        result = self.model(x)
        return result[0]

def generate_heatmap(image_path):
    """
    Generates a heatmap using EigenCAM to visualize AI attention.
    """
    try:
        # 1. Load the Model
        yolo_model = YOLO('yolov8n.pt')
        
        # 2. Target the specific internal layer
        # We target the last layer of the "backbone" (usually index -2 or -3)
        target_layers = [yolo_model.model.model[-2]]

        # 3. Prepare the Image
        img = cv2.imread(image_path)
        if img is None:
            return None, "Error: Could not read image."
            
        # Resize to standard YOLO size to avoid shape mismatches
        img = cv2.resize(img, (640, 640))
        
        # Convert to float 0-1 range for the visualizer
        rgb_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        rgb_img_float = np.float32(rgb_img) / 255.0
        
        # 4. Run EigenCAM WITH THE WRAPPER
        # We wrap 'yolo_model.model' so it behaves like a standard PyTorch model
        cam = EigenCAM(
            model=YOLOv8Wrapper(yolo_model.model), # <--- THIS WAS MISSING
            target_layers=target_layers, 
        )
        
        # Process the image into a tensor
        tensor = torch.from_numpy(rgb_img_float).permute(2, 0, 1).unsqueeze(0)
        
        # Generate the heatmap
        grayscale_cam = cam(input_tensor=tensor)
        grayscale_cam = grayscale_cam[0, :] # Take the first result
        
        # 5. Overlay Heatmap
        visualization = show_cam_on_image(rgb_img_float, grayscale_cam, use_rgb=True)
        
        return visualization, "✅ Heatmap Generated via Native EigenCAM."

    except Exception as e:
        return None, f"Explainability Error: {str(e)}"
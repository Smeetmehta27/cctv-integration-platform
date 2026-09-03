import os
import time
import logging
import cv2
import numpy as np
from typing import List, Dict, Any
from ultralytics import YOLO

logger = logging.getLogger(__name__)

class ModelManager:
    def __init__(self):
        self.model_name = os.getenv("AI_MODEL", "yolov8n.pt")
        self.confidence_threshold = float(os.getenv("AI_CONFIDENCE", "0.4"))
        self.device = os.getenv("AI_DEVICE", "cpu")
        self.model = None
        
        # We only care about specific COCO classes for Stage 3.2
        # ultralytics COCO: 0=person, 1=bicycle, 2=car, 3=motorcycle, 5=bus, 7=truck
        self.target_classes = {0, 1, 2, 3, 5, 7}

    def load_model(self):
        logger.info(f"Loading YOLO model {self.model_name} on device {self.device}...")
        try:
            self.model = YOLO(self.model_name)
            if self.device != "cpu":
                self.model.to(self.device)
            logger.info("Model loaded successfully.")
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            raise e

    def predict(self, image_np: np.ndarray) -> (List[Dict[str, Any]], float):
        """
        Runs inference on a numpy array image.
        Returns a tuple of (detections_list, inference_time_ms).
        """
        if self.model is None:
            raise RuntimeError("Model is not loaded.")

        start_time = time.time()
        
        # ultralytics predict
        results = self.model.predict(
            source=image_np,
            conf=self.confidence_threshold,
            device=self.device,
            classes=list(self.target_classes),
            verbose=False
        )
        
        inference_time_ms = (time.time() - start_time) * 1000.0
        
        detections = []
        if len(results) > 0:
            result = results[0]
            boxes = result.boxes
            for box in boxes:
                cls_id = int(box.cls[0].item())
                conf = float(box.conf[0].item())
                x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
                
                class_name = self.model.names[cls_id]
                
                detections.append({
                    "class_id": cls_id,
                    "class_name": class_name,
                    "confidence": conf,
                    "bbox": {
                        "x1": x1,
                        "y1": y1,
                        "x2": x2,
                        "y2": y2
                    }
                })
                
        return detections, inference_time_ms

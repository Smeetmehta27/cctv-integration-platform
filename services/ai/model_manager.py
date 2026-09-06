from __future__ import annotations

import os
import time
import logging
import cv2
import numpy as np
from typing import Any
from ultralytics import YOLO

logger = logging.getLogger(__name__)

class ModelManager:
    def __init__(self):
        # Resolve model paths relative to this file's directory
        self._ai_dir = os.path.dirname(os.path.abspath(__file__))
        self._project_root = os.path.abspath(os.path.join(self._ai_dir, "..", ".."))

        # Ordered candidate weight files — first existing file wins.
        # This avoids triggering a network download for missing weights.
        self._weight_candidates = [
            os.path.join(self._ai_dir, "best.pt"),
            os.path.join(self._ai_dir, "runs", "fgvd_finetune-2", "weights", "best.pt"),
            os.path.join(self._ai_dir, "runs", "fgvd_finetune", "weights", "best.pt"),
            os.path.join(self._ai_dir, "itd_yolov8.pt"),
            os.path.join(self._project_root, "yolov8n.pt"),
            os.path.join(self._ai_dir, "yolov8n.pt"),
        ]

        self.confidence_threshold = float(os.getenv("AI_CONFIDENCE", "0.45"))
        self.iou_threshold = float(os.getenv("AI_IOU", "0.50"))
        self.device = os.getenv("AI_DEVICE", "cpu")
        self.model = None
        self.model_name = None  # resolved in load_model()

    def _resolve_weights(self) -> str:
        """
        Return the first weight file that actually exists on disk.
        Falls back to the AI_MODEL env-var override if set.
        """
        env_override = os.getenv("AI_MODEL")
        if env_override and os.path.isfile(env_override):
            return env_override

        for path in self._weight_candidates:
            if os.path.isfile(path):
                return path

        raise FileNotFoundError(
            "No YOLO weight file found. Searched:\n"
            + "\n".join(f"  • {p}" for p in self._weight_candidates)
        )

    def load_model(self):
        self.model_name = self._resolve_weights()
        logger.info(f"Loading YOLO model {self.model_name} on device {self.device}...")
        try:
            self.model = YOLO(self.model_name)
            if self.device != "cpu":
                self.model.to(self.device)
            logger.info(f"Model loaded successfully: {os.path.basename(self.model_name)}")
        except Exception as e:
            logger.error(f"Failed to load model {self.model_name}: {e}")
            raise

    def predict(self, image_np: np.ndarray) -> tuple[list[dict[str, Any]], float]:
        """
        Runs inference on a numpy array image.
        Returns a tuple of (detections_list, inference_time_ms).
        """
        if self.model is None:
            raise RuntimeError("Model is not loaded.")

        start_time = time.time()
        
        # ultralytics predict — no class filter; allows all FGVD 215 classes
        results = self.model.predict(
            source=image_np,
            conf=self.confidence_threshold,
            iou=self.iou_threshold,
            device=self.device,
            verbose=False
        )
        
        inference_time_ms = (time.time() - start_time) * 1000.0

        # --- Live OpenCV visualiser ---
        if len(results) > 0:
            annotated_frame = results[0].plot()
            cv2.imshow("VIGILIS AI - Live Inference", annotated_frame)
            cv2.waitKey(1)  # flush UI buffer without blocking

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

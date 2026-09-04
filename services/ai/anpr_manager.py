import os
import logging
import cv2
import numpy as np
from typing import Optional, Tuple
from services.ai.plate_normalizer import IndianPlateNormalizer

logger = logging.getLogger(__name__)

class ANPRManager:
    """
    Manages the EasyOCR pipeline for reading license plates from vehicle ROIs.
    """
    def __init__(self):
        # We lazy-load EasyOCR because it's heavy
        self.reader = None
        self.min_confidence = float(os.getenv("ANPR_MIN_CONFIDENCE", "0.4"))

    def _get_reader(self):
        if self.reader is None:
            logger.info("Initializing EasyOCR (CPU Mode)...")
            import easyocr
            # For Indian plates, 'en' is usually sufficient. 
            self.reader = easyocr.Reader(['en'], gpu=False, verbose=False)
        return self.reader

    def read_plate(self, vehicle_crop: np.ndarray) -> Optional[Tuple[str, str, float]]:
        """
        Takes a full vehicle BBOX crop.
        Intelligently slices the bottom 50% (where the plate usually is),
        runs OCR, and returns the best normalized read.
        Returns: (raw_text, normalized_text, confidence)
        """
        h, w = vehicle_crop.shape[:2]
        
        # Too small to read a plate
        if h < 40 or w < 40:
            return None
            
        # ROI Waterfall: crop bottom 50% to save CPU and remove noise (brand logos etc.)
        roi = vehicle_crop[int(h*0.5):h, 0:w]
        
        # Optional: Convert to grayscale and apply basic contrast for EasyOCR
        gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        
        reader = self._get_reader()
        # detail=1 returns [(bbox, text, prob)]
        results = reader.readtext(gray, detail=1, paragraph=False)
        
        best_plate = None
        highest_conf = 0.0
        
        for bbox, raw_text, conf in results:
            if conf < self.min_confidence:
                continue
                
            normalized = IndianPlateNormalizer.normalize(raw_text)
            if IndianPlateNormalizer.is_valid_format(normalized):
                if conf > highest_conf:
                    highest_conf = conf
                    best_plate = (raw_text, normalized, conf)
                    
        return best_plate

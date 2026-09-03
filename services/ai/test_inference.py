import cv2
import urllib.request
import numpy as np
from services.ai.model_manager import ModelManager

def main():
    print("Loading ModelManager...")
    manager = ModelManager()
    manager.load_model()
    
    print("Downloading sample image...")
    # Bus image
    url = 'https://ultralytics.com/images/bus.jpg'
    resp = urllib.request.urlopen(url)
    image = np.asarray(bytearray(resp.read()), dtype="uint8")
    frame = cv2.imdecode(image, cv2.IMREAD_COLOR)
    
    print(f"Image decoded. Shape: {frame.shape}")
    print("Running inference...")
    detections, latency = manager.predict(frame)
    
    print(f"\nInference completed in {latency:.1f}ms")
    print(f"Found {len(detections)} targets.")
    for d in detections:
        print(f" - {d['class_name']} ({d['confidence']:.2f}) at {d['bbox']}")

if __name__ == "__main__":
    main()

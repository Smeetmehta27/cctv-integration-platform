import cv2
import numpy as np
from services.ai.anpr_manager import ANPRManager
from services.ai.plate_normalizer import PlateNormalizer
from services.ai.plate_stabilizer import PlateStabilizer

def create_synthetic_car():
    # Create a 400x400 blank car image
    img = np.zeros((400, 400, 3), dtype=np.uint8)
    
    # Draw a mock license plate in the bottom 50%
    cv2.rectangle(img, (100, 250), (300, 310), (255, 255, 255), -1)
    
    # Draw text "GJ 01 AB 1234" on the plate
    # We use a standard font that OCR can read easily
    cv2.putText(img, "GJ 01 AB 1234", (110, 295), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 0), 2)
    
    return img

def main():
    print("Initializing ANPR Pipeline...")
    anpr = ANPRManager()
    stabilizer = PlateStabilizer(required_hits=2)
    
    # 1. Create synthetic vehicle crop
    print("Generating synthetic vehicle crop with plate 'GJ 01 AB 1234'...")
    vehicle_crop = create_synthetic_car()
    
    camera_id = "CAM_TEST"
    track_id = 17
    
    # Simulate Frame 1
    print("\n--- Processing Frame 1 ---")
    res1 = anpr.read_plate(vehicle_crop)
    if res1:
        raw, norm, conf = res1
        print(f"EasyOCR Output: Raw='{raw}', Normalized='{norm}', Conf={conf:.2f}")
        stable = stabilizer.add_reading(camera_id, track_id, raw, norm, conf)
        if stable:
            print("=> PLATE CONFIRMED!")
        else:
            print("=> Stabilizing (Waiting for more frames)")
    
    # Simulate Frame 2 (identical to Frame 1 for this test)
    print("\n--- Processing Frame 2 ---")
    res2 = anpr.read_plate(vehicle_crop)
    if res2:
        raw, norm, conf = res2
        print(f"EasyOCR Output: Raw='{raw}', Normalized='{norm}', Conf={conf:.2f}")
        stable = stabilizer.add_reading(camera_id, track_id, raw, norm, conf)
        if stable:
            print(f"=> PLATE CONFIRMED: {stable}")
        else:
            print("=> Stabilizing (Waiting for more frames)")
            
    assert stabilizer.has_stable_plate(camera_id, track_id), "Plate did not stabilize after 2 hits!"
    final_plate = stabilizer.get_stable_plate(camera_id, track_id)
    assert final_plate["normalized_text"] == "GJ01AB1234", "Plate normalization failed!"
    
    print("\nTEST PASSED: ANPR Pipeline correctly stabilized and normalized the Indian license plate!")

if __name__ == "__main__":
    main()

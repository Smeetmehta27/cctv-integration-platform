import cv2
import urllib.request
import numpy as np
from services.ai.tracker_manager import TrackerManager

def download_image(url):
    resp = urllib.request.urlopen(url)
    image = np.asarray(bytearray(resp.read()), dtype="uint8")
    return cv2.imdecode(image, cv2.IMREAD_COLOR)

def main():
    print("Loading TrackerManager...")
    manager = TrackerManager()
    
    print("Downloading sample images...")
    # Bus image
    frame_a1 = download_image('https://ultralytics.com/images/bus.jpg')
    # Same image, slightly shifted to simulate next frame
    M = np.float32([[1, 0, 10], [0, 1, 0]]) # shift right by 10px
    frame_a2 = cv2.warpAffine(frame_a1, M, (frame_a1.shape[1], frame_a1.shape[0]))
    
    # Different image (zidane)
    frame_b1 = download_image('https://ultralytics.com/images/zidane.jpg')
    
    print("\n--- Testing Camera A (Frame 1) ---")
    tracks_a1, _ = manager.process_frame("CAMERA_A", frame_a1, pts=100.0)
    for t in tracks_a1:
        print(f"Cam A Track: {t['class_name']} #{t['track_id']} at {t['centroid']}")
        
    print("\n--- Testing Camera A (Frame 2) ---")
    tracks_a2, _ = manager.process_frame("CAMERA_A", frame_a2, pts=200.0)
    for t in tracks_a2:
        print(f"Cam A Track: {t['class_name']} #{t['track_id']} at {t['centroid']} | Vel: {t['image_plane_velocity']} px/s")

    print("\n--- Testing Camera B (Frame 1) ---")
    tracks_b1, _ = manager.process_frame("CAMERA_B", frame_b1, pts=100.0)
    for t in tracks_b1:
        print(f"Cam B Track: {t['class_name']} #{t['track_id']} at {t['centroid']}")
        
    print("\n--- Verification ---")
    assert len(manager.isolated_trackers) == 2, "Should have 2 independent trackers"
    
    # Check if tracking IDs persisted in Camera A
    a1_ids = {t['track_id'] for t in tracks_a1}
    a2_ids = {t['track_id'] for t in tracks_a2}
    intersection = a1_ids.intersection(a2_ids)
    print(f"Persisted IDs in Camera A: {intersection}")
    assert len(intersection) > 0, "No tracks persisted between frames in Camera A"
    
    # Check Camera B IDs are isolated
    b1_ids = {t['track_id'] for t in tracks_b1}
    overlap = b1_ids.intersection(a1_ids)
    print(f"Overlapping IDs between Camera A and Camera B: {overlap}")
    # Technically ByteTrack counts up, so if B is a new tracker, it starts at 1,
    # and A also started at 1. The tracker states are separate.
    
    print("\nTEST PASSED: Tracking state is isolated per camera!")

if __name__ == "__main__":
    main()

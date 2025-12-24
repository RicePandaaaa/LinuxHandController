#!/usr/bin/env python3

import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import time

# Download the hand landmark model if not present
MODEL_PATH = 'hand_landmarker.task'

# Create hand landmarker
base_options = python.BaseOptions(model_asset_path=MODEL_PATH)
options = vision.HandLandmarkerOptions(
    base_options=base_options,
    running_mode=vision.RunningMode.VIDEO,
    num_hands=2,
    min_hand_detection_confidence=0.5,
    min_hand_presence_confidence=0.5,
    min_tracking_confidence=0.5
)

landmarker = vision.HandLandmarker.create_from_options(options)

# Initialize webcam
cap = cv2.VideoCapture(2)
prev_time = 0
frame_count = 0

while True:
    success, frame = cap.read()
    if not success:
        print("Failed to grab frame")
        break
    
    frame = cv2.flip(frame, 1)
    
    # Convert to MediaPipe Image
    mp_frame = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame)
    
    # Process frame with timestamp
    timestamp_ms = int(time.time() * 1000)
    results = landmarker.detect_for_video(mp_frame, timestamp_ms)
    
    # Draw landmarks
    if results.hand_landmarks:
        for idx, hand_landmarks in enumerate(results.hand_landmarks):            
            # Get handedness
            if results.handedness:
                hand_label = results.handedness[idx][0].category_name
                hand_label_color = (0, 255, 0) if hand_label == 'Left' else (0, 0, 255)

                # Draw each landmark
                for landmark in hand_landmarks:
                    x = int(landmark.x * frame.shape[1])
                    y = int(landmark.y * frame.shape[0])
                    cv2.circle(img=frame, center=(x, y), radius=5, color=hand_label_color, thickness=-1)
                
                # Display hand label
                wrist = hand_landmarks[0]
                cv2.putText(
                    img=frame,
                    text=f"{hand_label} Hand",
                    org=(int(wrist.x * frame.shape[1]), int(wrist.y * frame.shape[0]) - 20),
                    fontFace=cv2.FONT_HERSHEY_SIMPLEX,
                    fontScale=0.7,
                    color=hand_label_color,
                    thickness=2
                )
    
    # Calculate FPS
    current_time = time.time()
    fps = 1 / (current_time - prev_time) if prev_time != 0 else 0
    prev_time = current_time
    
    cv2.putText(img=frame, text=f"FPS: {int(fps)}", org=(10, 30), fontFace=cv2.FONT_HERSHEY_SIMPLEX, fontScale=1, color=(0, 255, 0), thickness=2)
    
    num_hands = len(results.hand_landmarks) if results.hand_landmarks else 0
    cv2.putText(img=frame, text=f"Hands: {num_hands}", org=(10, 70), fontFace=cv2.FONT_HERSHEY_SIMPLEX, fontScale=1, color=(0, 255, 0), thickness=2)
    
    cv2.imshow(winname='HandTracker', mat=frame)
    
    if cv2.waitKey(delay=1) & 0xFF == ord('q'):
        break
    
    frame_count += 1

cap.release()
cv2.destroyAllWindows()
landmarker.close()

print("\nHand tracking stopped")
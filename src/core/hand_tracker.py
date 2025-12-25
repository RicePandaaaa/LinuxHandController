"""Hand tracking using MediaPipe."""

from dataclasses import dataclass
from typing import List, Optional
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision


@dataclass
class Hand:
    """Represents a detected hand with landmarks and metadata."""
    landmarks: List  # List of 21 MediaPipe landmarks
    handedness: str  # "Left" or "Right"
    confidence: float = 1.0


class HandTracker:
    """Wrapper around MediaPipe HandLandmarker."""

    def __init__(self,
                 model_path: str = 'hand_landmarker.task',
                 num_hands: int = 2,
                 min_detection_confidence: float = 0.5,
                 min_tracking_confidence: float = 0.5):
        """
        Initialize hand tracker.

        Args:
            model_path: Path to hand_landmarker.task model file
            num_hands: Maximum number of hands to detect
            min_detection_confidence: Minimum confidence for detection
            min_tracking_confidence: Minimum confidence for tracking
        """
        base_options = python.BaseOptions(model_asset_path=model_path)
        options = vision.HandLandmarkerOptions(
            base_options=base_options,
            running_mode=vision.RunningMode.VIDEO,
            num_hands=num_hands,
            min_hand_detection_confidence=min_detection_confidence,
            min_hand_presence_confidence=min_detection_confidence,
            min_tracking_confidence=min_tracking_confidence
        )

        self.landmarker = vision.HandLandmarker.create_from_options(options)

    def process_frame(self, frame, timestamp_ms: int) -> List[Hand]:
        """
        Process frame and return detected hands.

        Args:
            frame: Video frame (numpy array)
            timestamp_ms: Timestamp in milliseconds

        Returns:
            List of Hand objects
        """
        mp_frame = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame)
        results = self.landmarker.detect_for_video(mp_frame, timestamp_ms)

        hands = []
        if results.hand_landmarks:
            for idx in range(len(results.hand_landmarks)):
                # Swap handedness because frame is horizontally flipped for mirror mode
                detected_hand = results.handedness[idx][0].category_name
                corrected_hand = "Right" if detected_hand == "Left" else "Left"

                hands.append(Hand(
                    landmarks=results.hand_landmarks[idx],
                    handedness=corrected_hand,
                    confidence=results.handedness[idx][0].score
                ))

        return hands

    def close(self):
        """Clean up resources."""
        self.landmarker.close()

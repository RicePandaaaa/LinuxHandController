"""Main rendering coordinator."""

from typing import List, Dict
import cv2
import numpy as np
from src.core.hand_tracker import Hand
from src.ui.overlay import LevelBarOverlay, GestureIndicator


class Renderer:
    """Main rendering coordinator for all UI elements."""

    def __init__(self):
        self.volume_bar = LevelBarOverlay((10, 100), color=(0, 255, 0))
        self.brightness_bar = LevelBarOverlay((10, 160), color=(255, 200, 0))
        self.gesture_indicator = GestureIndicator()

    def render_frame(self,
                     frame: np.ndarray,
                     hands: List[Hand],
                     hand_states: Dict,
                     volume_level: int,
                     brightness_level: int,
                     fps: float) -> np.ndarray:
        """Draw all UI elements on the video frame."""
        self._render_landmarks(frame, hands)

        for idx, hand in enumerate(hands):
            state = hand_states.get(idx, {})
            is_claw = state.get('is_claw', False)
            rotation = state.get('rotation', None)
            self.gesture_indicator.render(frame, hand, is_claw, rotation)

        self.volume_bar.render(frame, volume_level, "Volume")
        self.brightness_bar.render(frame, brightness_level, "Brightness")

        self._render_stats(frame, fps, len(hands))

        return frame

    def _render_landmarks(self, frame: np.ndarray, hands: List[Hand]):
        """Draw hand landmarks and labels."""
        for hand in hands:
            color = (0, 255, 0) if hand.handedness == 'Left' else (0, 0, 255)

            for landmark in hand.landmarks:
                x = int(landmark.x * frame.shape[1])
                y = int(landmark.y * frame.shape[0])
                cv2.circle(frame, (x, y), 5, color, -1)

            wrist = hand.landmarks[0]
            label_pos = (
                int(wrist.x * frame.shape[1]),
                int(wrist.y * frame.shape[0]) - 20
            )
            cv2.putText(
                frame,
                f"{hand.handedness} Hand",
                label_pos,
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                color,
                2
            )

    def _render_stats(self, frame: np.ndarray, fps: float, num_hands: int):
        """Draw FPS and hand count."""
        cv2.putText(
            frame,
            f"FPS: {int(fps)}",
            (10, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0, 255, 0),
            2
        )

        cv2.putText(
            frame,
            f"Hands: {num_hands}",
            (10, 70),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0, 255, 0),
            2
        )

"""UI overlay components for visual feedback."""

from typing import Tuple
import cv2
import numpy as np
from src.core.hand_tracker import Hand


class LevelBarOverlay:
    """Renders horizontal level bar with label."""

    def __init__(self,
                 position: Tuple[int, int],
                 width: int = 300,
                 height: int = 30,
                 color: Tuple[int, int, int] = (0, 255, 0)):
        self._pos = position
        self._width = width
        self._height = height
        self._color = color

    def render(self, frame: np.ndarray, level: int, label: str):
        """Draw a level bar showing the current percentage."""
        x, y = self._pos

        cv2.rectangle(
            frame,
            (x, y + 20),
            (x + self._width, y + 20 + self._height),
            (60, 60, 60),
            -1
        )

        filled_width = int((level / 100.0) * self._width)
        if filled_width > 0:
            cv2.rectangle(
                frame,
                (x, y + 20),
                (x + filled_width, y + 20 + self._height),
                self._color,
                -1
            )

        cv2.rectangle(
            frame,
            (x, y + 20),
            (x + self._width, y + 20 + self._height),
            (200, 200, 200),
            2
        )

        text = f"{label}: {level}%"
        cv2.putText(
            frame,
            text,
            (x, y + 15),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (255, 255, 255),
            2
        )


class GestureIndicator:
    """Shows gesture detection status near hand."""

    def render(self, frame: np.ndarray, hand: Hand, is_claw: bool,
               rotation_angle: float = None):
        """Draw claw status and rotation angle near the wrist."""
        wrist_x = int(hand.landmarks[0].x * frame.shape[1])
        wrist_y = int(hand.landmarks[0].y * frame.shape[0])

        status_text = "CLAW" if is_claw else "---"
        status_color = (0, 255, 0) if is_claw else (100, 100, 100)

        cv2.putText(
            frame,
            status_text,
            (wrist_x - 40, wrist_y + 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            status_color,
            2
        )

        if is_claw and rotation_angle is not None:
            angle_text = f"{rotation_angle:.1f}°"
            cv2.putText(
                frame,
                angle_text,
                (wrist_x - 40, wrist_y + 50),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.4,
                (255, 255, 255),
                1
            )

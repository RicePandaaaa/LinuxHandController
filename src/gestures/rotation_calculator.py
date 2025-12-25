"""Palm rotation calculation with angle unwrapping."""

import numpy as np
from src.core.hand_tracker import Hand
from src.utils.geometry import landmark_to_array


class RotationCalculator:
    """Calculates palm rotation with continuous angle tracking."""

    WRIST = 0
    INDEX_MCP = 5
    MIDDLE_MCP = 9
    PINKY_MCP = 17

    def __init__(self):
        self._accumulated_angle = 0.0
        self._last_raw_angle = None
        self._baseline_angle = None

    def calculate_roll(self, hand: Hand) -> float:
        """
        Calculate palm roll angle with unwrapping to handle boundary crossing.

        Returns continuous angle that can exceed ±180°.
        """
        landmarks = hand.landmarks

        # Use the vector across the palm for more stable tracking
        index_mcp = landmark_to_array(landmarks[self.INDEX_MCP])
        pinky_mcp = landmark_to_array(landmarks[self.PINKY_MCP])
        palm_vector = index_mcp - pinky_mcp

        # Calculate angle in the image plane
        raw_angle = np.arctan2(palm_vector[1], palm_vector[0]) * 180.0 / np.pi

        # First detection establishes the baseline as zero
        if self._baseline_angle is None:
            self._baseline_angle = raw_angle
            self._accumulated_angle = 0.0
        elif self._last_raw_angle is not None:
            diff = raw_angle - self._last_raw_angle

            # Handle -180/+180 degree boundary crossing
            if diff > 180:
                diff -= 360
            elif diff < -180:
                diff += 360

            self._accumulated_angle += diff

        self._last_raw_angle = raw_angle

        # Mirror left hand to match right hand rotation direction
        return -self._accumulated_angle if hand.handedness == 'Left' else self._accumulated_angle

    def reset(self):
        """Reset all angle tracking state."""
        self._accumulated_angle = 0.0
        self._last_raw_angle = None
        self._baseline_angle = None

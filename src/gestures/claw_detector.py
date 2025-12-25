"""Claw gesture detection using distance-based approach."""

from typing import List, Dict, Any

import numpy as np

from src.core.hand_tracker import Hand
from src.utils.geometry import distance_3d

# Hysteresis multipliers
HYSTERESIS_SPREAD_MULTIPLIER = 1.2
HYSTERESIS_FINGER_REDUCTION = 1


class ClawDetector:
    """Detects claw gesture by checking if fingertips are clustered together."""

    # MediaPipe hand landmark indices
    WRIST = 0
    THUMB_TIP = 4
    INDEX_TIP = 8
    MIDDLE_TIP = 12
    RING_TIP = 16
    PINKY_TIP = 20
    MIDDLE_MCP = 9

    def __init__(
        self,
        max_fingertip_spread: float = 0.15,
        max_palm_distance: float = 0.20,
        min_fingers_close: int = 3
    ) -> None:
        self.max_fingertip_spread = max_fingertip_spread
        self.max_palm_distance = max_palm_distance
        self.min_fingers_close = min_fingers_close
        self._is_claw = False
        self._debug_info: Dict[str, Any] = {}

    def detect(self, hand: Hand) -> bool:
        """
        Detect claw gesture with hysteresis to prevent rapid toggling.

        Uses looser thresholds when already in claw state to maintain stability.
        """
        landmarks = hand.landmarks

        fingertips = [
            landmarks[self.INDEX_TIP],
            landmarks[self.MIDDLE_TIP],
            landmarks[self.RING_TIP],
            landmarks[self.PINKY_TIP],
        ]

        palm_center = landmarks[self.MIDDLE_MCP]

        fingertip_spread = self._calculate_average_fingertip_distance(fingertips)

        fingers_close_to_palm = 0
        palm_distances = []
        for tip in fingertips:
            dist = distance_3d(tip, palm_center)
            palm_distances.append(dist)
            if dist < self.max_palm_distance:
                fingers_close_to_palm += 1

        self._debug_info = {
            'fingertip_spread': fingertip_spread,
            'palm_distances': palm_distances,
            'fingers_close': fingers_close_to_palm
        }

        if self._is_claw:
            spread_threshold = self.max_fingertip_spread * HYSTERESIS_SPREAD_MULTIPLIER
            fingers_threshold = max(2, self.min_fingers_close - HYSTERESIS_FINGER_REDUCTION)
        else:
            spread_threshold = self.max_fingertip_spread
            fingers_threshold = self.min_fingers_close

        is_claw = (fingertip_spread < spread_threshold and
                   fingers_close_to_palm >= fingers_threshold)

        self._is_claw = is_claw
        return is_claw

    def _calculate_average_fingertip_distance(self, fingertips: List) -> float:
        """Calculate average distance between all pairs of fingertips."""
        distances = [
            distance_3d(fingertips[i], fingertips[j])
            for i in range(len(fingertips))
            for j in range(i + 1, len(fingertips))
        ]
        return float(np.mean(distances)) if distances else 0.0

    def get_debug_info(self) -> Dict[str, Any]:
        """Returns debug information from the last detection."""
        return self._debug_info

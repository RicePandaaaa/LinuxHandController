"""Video capture management."""

from typing import Optional
import cv2
import time


class VideoCapture:
    """Manages camera capture with error handling and frame preprocessing."""

    def __init__(self, camera_index: int = 2, flip_horizontal: bool = True):
        self.camera_index = camera_index
        self.flip_horizontal = flip_horizontal
        self.cap = cv2.VideoCapture(camera_index)

        if not self.cap.isOpened():
            raise RuntimeError(f"Failed to open camera at index {camera_index}")

        self._prev_time = 0
        self._fps = 0.0

    def read_frame(self) -> Optional[any]:
        """Read and preprocess frame from camera."""
        success, frame = self.cap.read()
        if not success:
            return None

        if self.flip_horizontal:
            frame = cv2.flip(frame, 1)

        current_time = time.time()
        if self._prev_time != 0:
            self._fps = 1 / (current_time - self._prev_time)
        self._prev_time = current_time

        return frame

    @property
    def fps(self) -> float:
        """Get current FPS."""
        return self._fps

    def release(self):
        """Release camera resources."""
        self.cap.release()

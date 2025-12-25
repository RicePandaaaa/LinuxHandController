"""Smoothing and filtering for gesture control."""

import time


class ExponentialMovingAverage:
    """Smooths noisy signals using exponential moving average."""

    def __init__(self, alpha: float = 0.3):
        """Initialize with smoothing factor (0.3 balances responsiveness and stability)."""
        self._alpha = alpha
        self._value = None

    def update(self, new_value: float) -> float:
        """Apply EMA smoothing to the new value."""
        if self._value is None:
            self._value = new_value
        else:
            self._value = self._alpha * new_value + (1 - self._alpha) * self._value
        return self._value

    def reset(self):
        """Reset to initial state."""
        self._value = None


class RateLimiter:
    """Limits rate of system control updates."""

    def __init__(self, min_interval_ms: int = 150):
        """Initialize with minimum interval between updates in milliseconds."""
        self._min_interval = min_interval_ms / 1000.0
        self._last_update = 0

    def should_update(self) -> bool:
        """Check if enough time has passed since last update."""
        current_time = time.time()
        if current_time - self._last_update >= self._min_interval:
            self._last_update = current_time
            return True
        return False

    def reset(self):
        """Reset timer."""
        self._last_update = 0


def map_angle_to_level(angle: float, current_level: int, deadzone: float = 10.0) -> int:
    """
    Map rotation angle to control level using wider, less sensitive range.

    Args:
        angle: Rotation angle in degrees (-180 to +180)
        current_level: Current control level (0-100)
        deadzone: Deadzone around neutral position (degrees)

    Returns:
        New level (0-100)
    """
    # Apply deadzone
    if -deadzone <= angle <= deadzone:
        return current_level

    # Use much wider angle range for less sensitivity
    # Map -180° to +180° → 0% to 100% (excluding deadzone)
    if angle < -deadzone:
        # Counterclockwise: Map -180° to -deadzone → 0% to 50%
        # Clamp to -180 minimum
        angle = max(angle, -180.0)
        normalized = (angle + 180) / (180 - deadzone)  # 0.0 to ~1.0
        return int(normalized * 50)
    else:
        # Clockwise: Map +deadzone to +180° → 50% to 100%
        # Clamp to +180 maximum
        angle = min(angle, 180.0)
        normalized = (angle - deadzone) / (180 - deadzone)  # 0.0 to ~1.0
        return int(50 + normalized * 50)

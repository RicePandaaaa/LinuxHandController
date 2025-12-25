"""Configuration dataclasses for the application."""

from dataclasses import dataclass, field


@dataclass
class CameraConfig:
    """Camera configuration."""
    index: int = 2
    flip_horizontal: bool = True


@dataclass
class GestureConfig:
    """Gesture detection configuration."""
    # Claw detection (distance-based)
    max_fingertip_spread: float = 0.15  # Max avg distance between fingertips
    max_palm_distance: float = 0.20     # Max distance from fingertips to palm
    min_fingers_close: int = 3          # Min fingers that must be close to palm

    # Rotation mapping
    rotation_deadzone: float = 5.0  # degrees
    rotation_range: float = 180.0    # degrees (full range)


@dataclass
class ControlConfig:
    """Control system configuration."""
    update_interval_ms: int = 150  # Rate limit
    smoothing_alpha: float = 0.3    # EMA smoothing

    # Volume
    volume_min: int = 0
    volume_max: int = 100

    # Brightness
    brightness_min: int = 5   # Never go completely dark
    brightness_max: int = 100


@dataclass
class AppConfig:
    """Master application configuration."""
    camera: CameraConfig = field(default_factory=CameraConfig)
    gesture: GestureConfig = field(default_factory=GestureConfig)
    control: ControlConfig = field(default_factory=ControlConfig)

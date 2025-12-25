#!/usr/bin/env python3
"""LinuxHandController - Control volume and brightness with hand gestures."""

import logging
import time
from typing import Optional

import cv2

from src.core.hand_tracker import HandTracker
from src.core.video_capture import VideoCapture
from src.gestures.claw_detector import ClawDetector
from src.gestures.rotation_calculator import RotationCalculator
from src.controllers.volume_controller import VolumeController
from src.controllers.brightness_controller import BrightnessController
from src.filters.smoothing import ExponentialMovingAverage, RateLimiter
from src.ui.renderer import Renderer
from src.utils.config import AppConfig

# Angle to percentage conversion constants
DEGREES_PER_10_PERCENT = 10.0

# Logging configuration
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)


def main() -> None:
    """Main application entry point."""
    config = AppConfig()
    logger = logging.getLogger(__name__)

    try:
        camera = VideoCapture(config.camera.index, config.camera.flip_horizontal)
    except RuntimeError as e:
        logger.error(f"Failed to initialize camera: {e}")
        return

    tracker = HandTracker('hand_landmarker.task')
    claw_detector = ClawDetector(
        config.gesture.max_fingertip_spread,
        config.gesture.max_palm_distance,
        config.gesture.min_fingers_close
    )
    rotation_calc = RotationCalculator()

    volume_ctrl = VolumeController()
    brightness_ctrl = BrightnessController()

    logger.info("LinuxHandController starting...")
    if not volume_ctrl.is_available():
        logger.warning("Volume control unavailable (PulseAudio not found)")
    if not brightness_ctrl.is_available():
        logger.warning("Brightness control unavailable (brightnessctl not found)")
        logger.info("Install: sudo apt install brightnessctl")
        logger.info("Add user to video group: sudo usermod -a -G video $USER")

    volume_smoother = ExponentialMovingAverage(config.control.smoothing_alpha)
    brightness_smoother = ExponentialMovingAverage(config.control.smoothing_alpha)
    volume_limiter = RateLimiter(config.control.update_interval_ms)
    brightness_limiter = RateLimiter(config.control.update_interval_ms)

    renderer = Renderer()

    # Previous angles for delta-based control
    prev_volume_angle = None
    prev_brightness_angle = None

    logger.info("Controls:")
    logger.info("  Right hand claw + rotate: Control volume")
    logger.info("  Left hand claw + rotate: Control brightness")
    logger.info("  Press 'q' to quit")
    logger.info("Debug mode enabled - watch console for detection details")

    try:
        while True:
            frame = camera.read_frame()
            if frame is None:
                logger.error("Failed to grab frame")
                break

            timestamp_ms = int(time.time() * 1000)
            hands = tracker.process_frame(frame, timestamp_ms)

            hand_states = {}

            if not hands:
                rotation_calc.reset()

            if hands:
                logger.debug("="*60)

            for idx, hand in enumerate(hands):
                is_claw = claw_detector.detect(hand)
                debug_info = claw_detector.get_debug_info()

                logger.debug(f"{hand.handedness} hand:")
                logger.debug(f"  Fingertip spread: {debug_info.get('fingertip_spread', 0):.3f} "
                             f"(max: {config.gesture.max_fingertip_spread:.3f})")

                palm_dists = debug_info.get('palm_distances', [])
                if palm_dists:
                    logger.debug(f"  Palm distances: I={palm_dists[0]:.3f}, M={palm_dists[1]:.3f}, "
                                 f"R={palm_dists[2]:.3f}, P={palm_dists[3]:.3f}")
                    logger.debug(f"  Max palm distance: {config.gesture.max_palm_distance:.3f}")
                    logger.debug(f"  Fingers close to palm: {debug_info.get('fingers_close', 0)}/{config.gesture.min_fingers_close}")

                logger.debug(f"  Claw detected: {'YES' if is_claw else 'NO'}")

                if is_claw:
                    rotation_angle = rotation_calc.calculate_roll(hand)
                    logger.debug(f"  Rotation angle: {rotation_angle:.1f}°")
                else:
                    rotation_angle = None
                    rotation_calc.reset()

                if is_claw and rotation_angle is not None:
                    hand_states[idx] = {'is_claw': True, 'rotation': rotation_angle}

                    if hand.handedness == 'Right':
                        prev_volume_angle = handle_volume_control(
                            rotation_angle, volume_smoother, volume_ctrl,
                            volume_limiter, prev_volume_angle
                        )
                    elif hand.handedness == 'Left':
                        prev_brightness_angle = handle_brightness_control(
                            rotation_angle, brightness_smoother, brightness_ctrl,
                            brightness_limiter, prev_brightness_angle
                        )
                else:
                    if hand.handedness == 'Right':
                        volume_smoother.reset()
                        prev_volume_angle = None
                    elif hand.handedness == 'Left':
                        brightness_smoother.reset()
                        prev_brightness_angle = None

                    hand_states[idx] = {'is_claw': False}

            volume_level = volume_ctrl.get_level()
            brightness_level = brightness_ctrl.get_level()

            rendered_frame = renderer.render_frame(
                frame, hands, hand_states, volume_level, brightness_level, camera.fps
            )

            cv2.imshow('HandController', rendered_frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    finally:
        camera.release()
        tracker.close()
        cv2.destroyAllWindows()
        logger.info("Hand tracking stopped")


def handle_volume_control(
    rotation_angle: float,
    smoother: ExponentialMovingAverage,
    controller: VolumeController,
    limiter: RateLimiter,
    prev_angle: Optional[float]
) -> float:
    """Process volume changes based on hand rotation delta."""
    logger = logging.getLogger(__name__)
    smoothed_angle = smoother.update(rotation_angle)
    logger.debug(f"  Smoothed angle: {smoothed_angle:.1f}°")

    if prev_angle is not None:
        angle_delta = smoothed_angle - prev_angle
        logger.debug(f"  Angle delta: {angle_delta:+.1f}°")

        volume_change = int(angle_delta / DEGREES_PER_10_PERCENT * 10)

        if volume_change != 0:
            current_volume = controller.get_level()
            new_volume = max(0, min(100, current_volume + volume_change))

            logger.debug(f"  Volume change: {current_volume}% {volume_change:+d}% -> {new_volume}%")

            if limiter.should_update():
                logger.debug(f"  -> Setting volume to {new_volume}%")
                controller.set_level(new_volume)
                return smoothed_angle
            else:
                logger.debug(f"  -> Rate limited (waiting for next update)")
                return prev_angle
        else:
            logger.debug(f"  -> No change (delta too small)")
    else:
        logger.debug(f"  -> Baseline set")

    return smoothed_angle


def handle_brightness_control(
    rotation_angle: float,
    smoother: ExponentialMovingAverage,
    controller: BrightnessController,
    limiter: RateLimiter,
    prev_angle: Optional[float]
) -> float:
    """Process brightness changes based on hand rotation delta."""
    logger = logging.getLogger(__name__)
    smoothed_angle = smoother.update(rotation_angle)
    logger.debug(f"  Smoothed angle: {smoothed_angle:.1f}°")

    if prev_angle is not None:
        angle_delta = smoothed_angle - prev_angle
        logger.debug(f"  Angle delta: {angle_delta:+.1f}°")

        brightness_change = int(angle_delta / DEGREES_PER_10_PERCENT * 10)

        if brightness_change != 0:
            current_brightness = controller.get_level()
            new_brightness = max(5, min(100, current_brightness + brightness_change))

            logger.debug(f"  Brightness change: {current_brightness}% {brightness_change:+d}% -> {new_brightness}%")

            if limiter.should_update():
                logger.debug(f"  -> Setting brightness to {new_brightness}%")
                controller.set_level(new_brightness)
                return smoothed_angle
            else:
                logger.debug(f"  -> Rate limited (waiting for next update)")
                return prev_angle
        else:
            logger.debug(f"  -> No change (delta too small)")
    else:
        logger.debug(f"  -> Baseline set")

    return smoothed_angle


if __name__ == '__main__':
    main()

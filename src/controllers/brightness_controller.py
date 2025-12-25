"""Brightness control using brightnessctl."""

import logging
import subprocess

from src.controllers.base_controller import BaseController

logger = logging.getLogger(__name__)

# Brightness configuration
MIN_BRIGHTNESS_PERCENT = 5
MAX_BRIGHTNESS_PERCENT = 100
DEFAULT_BRIGHTNESS_LEVEL = 50
DEFAULT_MAX_BRIGHTNESS_VALUE = 100


class BrightnessController(BaseController):
    """Controls screen brightness via brightnessctl."""

    def __init__(self) -> None:
        self._max_brightness = self._get_max_brightness()

    def set_level(self, level: int) -> None:
        """Set brightness to a percentage between 5 and 100."""
        level = max(MIN_BRIGHTNESS_PERCENT, min(MAX_BRIGHTNESS_PERCENT, level))

        try:
            result = subprocess.run(
                ['brightnessctl', 'set', f'{level}%'],
                check=False,
                capture_output=True,
                text=True
            )
            if result.returncode != 0:
                logger.error(f"Failed to set brightness: {result.stderr.strip()}")
        except FileNotFoundError:
            logger.error("brightnessctl command not found. Is it installed?")
        except subprocess.SubprocessError as e:
            logger.error(f"Failed to set brightness: {e}")

    def get_level(self) -> int:
        """Get current brightness level as a percentage."""
        try:
            result = subprocess.run(
                ['brightnessctl', 'get'],
                capture_output=True,
                text=True,
                check=True
            )
            current = int(result.stdout.strip())

            if self._max_brightness > 0:
                return int((current / self._max_brightness) * 100)
        except FileNotFoundError:
            logger.error("brightnessctl command not found. Is it installed?")
        except (ValueError, subprocess.SubprocessError) as e:
            logger.error(f"Failed to get brightness level: {e}")

        return DEFAULT_BRIGHTNESS_LEVEL

    def is_available(self) -> bool:
        """Check if brightnessctl is installed."""
        try:
            subprocess.run(
                ['brightnessctl', 'info'],
                capture_output=True,
                check=True
            )
            return True
        except (subprocess.CalledProcessError, FileNotFoundError) as e:
            logger.debug(f"brightnessctl not available: {e}")
            return False

    def _get_max_brightness(self) -> int:
        """Get maximum brightness value from system."""
        try:
            result = subprocess.run(
                ['brightnessctl', 'max'],
                capture_output=True,
                text=True,
                check=True
            )
            return int(result.stdout.strip())
        except FileNotFoundError:
            logger.warning("brightnessctl not found, using default max brightness")
        except (ValueError, subprocess.SubprocessError) as e:
            logger.warning(f"Failed to get max brightness, using default: {e}")

        return DEFAULT_MAX_BRIGHTNESS_VALUE

"""Volume control using PulseAudio pactl command."""

import logging
import re
import subprocess
from typing import Optional

from src.controllers.base_controller import BaseController

logger = logging.getLogger(__name__)

# PulseAudio sink configuration
DEFAULT_SINK_ID = "0"
DEFAULT_VOLUME_LEVEL = 50


class VolumeController(BaseController):
    """Controls system volume via PulseAudio."""

    def __init__(self, sink_id: str = DEFAULT_SINK_ID) -> None:
        self.sink_id = sink_id

    def set_level(self, level: int) -> None:
        """Set volume to a percentage between 0 and 100."""
        level = max(0, min(100, level))
        try:
            subprocess.call(["pactl", "set-sink-volume", self.sink_id, f"{level}%"])
        except FileNotFoundError:
            logger.error("pactl command not found. Is PulseAudio installed?")
        except subprocess.SubprocessError as e:
            logger.error(f"Failed to set volume: {e}")

    def get_level(self) -> int:
        """Get current volume level as a percentage."""
        try:
            result = subprocess.run(
                ["pactl", "get-sink-volume", self.sink_id],
                capture_output=True,
                text=True,
                check=True
            )
            match = re.search(r'(\d+)%', result.stdout)
            if match:
                return int(match.group(1))
        except FileNotFoundError:
            logger.error("pactl command not found. Is PulseAudio installed?")
        except subprocess.SubprocessError as e:
            logger.error(f"Failed to get volume level: {e}")

        return DEFAULT_VOLUME_LEVEL

    def is_available(self) -> bool:
        """Check if PulseAudio is running."""
        try:
            subprocess.run(['pactl', 'info'], capture_output=True, check=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError) as e:
            logger.debug(f"PulseAudio not available: {e}")
            return False

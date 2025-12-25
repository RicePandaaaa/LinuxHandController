"""Base controller interface."""

from abc import ABC, abstractmethod


class BaseController(ABC):
    """Abstract interface for system controllers."""

    @abstractmethod
    def set_level(self, level: int):
        """
        Set control level (0-100).

        Args:
            level: Level value (0-100)
        """
        pass

    @abstractmethod
    def get_level(self) -> int:
        """
        Get current level (0-100).

        Returns:
            Current level value
        """
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """
        Check if controller is available on system.

        Returns:
            True if available, False otherwise
        """
        pass

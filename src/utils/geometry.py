"""Geometry utilities for hand landmark calculations."""

import numpy as np


def distance_3d(p1, p2) -> float:
    """
    Calculate 3D Euclidean distance between two landmarks.

    Args:
        p1, p2: Landmarks with x, y, z attributes

    Returns:
        Euclidean distance
    """
    return np.sqrt((p2.x - p1.x)**2 + (p2.y - p1.y)**2 + (p2.z - p1.z)**2)


def landmark_to_array(landmark) -> np.ndarray:
    """
    Convert MediaPipe landmark to numpy array [x, y, z].

    Args:
        landmark: MediaPipe landmark object

    Returns:
        NumPy array with [x, y, z] coordinates
    """
    return np.array([landmark.x, landmark.y, landmark.z])


def cross_product(v1: np.ndarray, v2: np.ndarray) -> np.ndarray:
    """
    Calculate cross product of two 3D vectors.

    Args:
        v1, v2: 3D numpy arrays

    Returns:
        Cross product vector
    """
    return np.cross(v1, v2)


def angle_between_vectors(v1: np.ndarray, v2: np.ndarray) -> float:
    """
    Calculate angle between two vectors in degrees.

    Args:
        v1, v2: 3D numpy arrays

    Returns:
        Angle in degrees (0-180)
    """
    cos_angle = np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))
    cos_angle = np.clip(cos_angle, -1.0, 1.0)  # Handle numerical errors
    return np.arccos(cos_angle) * 180.0 / np.pi

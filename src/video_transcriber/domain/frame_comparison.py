"""Frame comparison logic for detecting distinct frames."""

import cv2
import numpy as np


def compute_frame_hash(frame: np.ndarray, hash_size: int = 16) -> np.ndarray:
    """Compute a perceptual hash for change detection.

    Uses average hash - fast and effective for slide detection.
    The hash is based on whether each pixel in a downsampled grayscale
    version of the frame is above or below the mean value.

    Args:
        frame: Input frame as numpy array (BGR format)
        hash_size: Size of hash grid (default 16x16 = 256 bits)

    Returns:
        Boolean array representing the perceptual hash
    """
    # Convert to grayscale
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Resize to hash_size x hash_size
    resized = cv2.resize(gray, (hash_size, hash_size), interpolation=cv2.INTER_AREA)

    # Compare each pixel to mean value
    mean_val = resized.mean()

    # Return flattened boolean array
    return (resized > mean_val).flatten()


def frames_similar(hash1: np.ndarray, hash2: np.ndarray) -> float:
    """Compute similarity between two frame hashes.

    Args:
        hash1: First frame hash (boolean array)
        hash2: Second frame hash (boolean array)

    Returns:
        Similarity score from 0.0 (completely different) to 1.0 (identical)
    """
    return float(np.mean(hash1 == hash2))

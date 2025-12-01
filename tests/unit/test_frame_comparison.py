"""Tests for frame comparison logic."""

import numpy as np
import pytest

from video_transcriber.domain.frame_comparison import compute_frame_hash, frames_similar


class TestComputeFrameHash:
    """Tests for frame hash computation."""

    def test_computes_hash_for_black_frame(self):
        """Computes hash for a completely black frame."""
        frame = np.zeros((100, 100, 3), dtype=np.uint8)

        hash_result = compute_frame_hash(frame)

        assert isinstance(hash_result, np.ndarray)
        assert hash_result.dtype == np.bool_
        # Default hash size 16x16 = 256 bits
        assert len(hash_result) == 256

    def test_computes_hash_for_white_frame(self):
        """Computes hash for a completely white frame."""
        frame = np.ones((100, 100, 3), dtype=np.uint8) * 255

        hash_result = compute_frame_hash(frame)

        assert isinstance(hash_result, np.ndarray)
        assert len(hash_result) == 256

    def test_different_frames_produce_different_hashes(self):
        """Different frames with structure should produce different hashes."""
        # Create frame with left half black, right half white
        frame1 = np.zeros((100, 100, 3), dtype=np.uint8)
        frame1[:, 50:] = 255

        # Create frame with top half black, bottom half white
        frame2 = np.zeros((100, 100, 3), dtype=np.uint8)
        frame2[50:, :] = 255

        hash1 = compute_frame_hash(frame1)
        hash2 = compute_frame_hash(frame2)

        # Hashes should be different
        assert not np.array_equal(hash1, hash2)

    def test_same_frame_produces_same_hash(self):
        """Same frame should produce the same hash."""
        frame = np.random.randint(0, 256, (100, 100, 3), dtype=np.uint8)

        hash1 = compute_frame_hash(frame)
        hash2 = compute_frame_hash(frame)

        # Should be identical
        assert np.array_equal(hash1, hash2)

    def test_respects_custom_hash_size(self):
        """Compute hash respects custom hash size parameter."""
        frame = np.zeros((100, 100, 3), dtype=np.uint8)

        hash_8 = compute_frame_hash(frame, hash_size=8)
        hash_32 = compute_frame_hash(frame, hash_size=32)

        # 8x8 = 64 bits, 32x32 = 1024 bits
        assert len(hash_8) == 64
        assert len(hash_32) == 1024


class TestFramesSimilar:
    """Tests for frame similarity comparison."""

    def test_identical_hashes_are_perfectly_similar(self):
        """Identical hashes should return similarity of 1.0."""
        hash1 = np.array([True, False, True, False])
        hash2 = np.array([True, False, True, False])

        similarity = frames_similar(hash1, hash2)

        assert similarity == 1.0

    def test_completely_different_hashes_have_zero_similarity(self):
        """Completely different hashes should return similarity of 0.0."""
        hash1 = np.array([True, True, True, True])
        hash2 = np.array([False, False, False, False])

        similarity = frames_similar(hash1, hash2)

        assert similarity == 0.0

    def test_partially_similar_hashes(self):
        """Partially similar hashes return intermediate similarity."""
        hash1 = np.array([True, True, True, True])
        hash2 = np.array([True, True, False, False])

        similarity = frames_similar(hash1, hash2)

        # 2 out of 4 bits match = 0.5 similarity
        assert similarity == 0.5

    def test_returns_float_between_zero_and_one(self):
        """Similarity is always between 0.0 and 1.0."""
        hash1 = np.random.choice([True, False], size=256)
        hash2 = np.random.choice([True, False], size=256)

        similarity = frames_similar(hash1, hash2)

        assert 0.0 <= similarity <= 1.0
        assert isinstance(similarity, (float, np.floating))

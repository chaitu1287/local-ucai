"""Transform base classes and implementations for text manipulation."""

from abc import ABC, abstractmethod


class Transform(ABC):
    """Base class for text transforms."""

    @abstractmethod
    def __call__(self, text: str) -> str:
        """Apply transform to text."""
        pass


class Compose:
    """Compose multiple transforms together"""

    def __init__(self, transforms: list[Transform]):
        """Initialize composed transforms."""
        self.transforms = transforms

    def __call__(self, text: str) -> str:
        """Apply all transforms in sequence."""
        for transform in self.transforms:
            text = transform(text)
        return text


class RandomCapitalization(Transform):
    """Randomly capitalize characters in text."""

    def __call__(self, text: str) -> str:
        """Apply random capitalization to text."""
        # TODO: Implement this transform
        # Should randomly capitalize letters while preserving readability
        return text


class WordScrambling(Transform):
    """Scramble words while keeping first and last letters fixed."""

    def __call__(self, text: str) -> str:
        """Apply word scrambling to text."""
        # TODO: Implement this transform
        # Research shows humans can read text with scrambled middle letters
        return text


class AsciiNoising(Transform):
    """Add ASCII noise characters to text."""

    def __call__(self, text: str) -> str:
        """Apply ASCII noise to text."""
        # TODO: Implement this transform
        # Adds visual noise while preserving text structure
        return text

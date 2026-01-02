"""PyTorch-style transforms for text manipulation."""

from src.core.transforms.transforms import (
    Transform,
    Compose,
    RandomCapitalization,
    WordScrambling,
    AsciiNoising,
)


def load_transforms(transform_names: list[str]) -> Compose:
    """Load transforms by name and return a Compose instance."""
    transform_map = {
        "RandomCapitalization": RandomCapitalization,
        "WordScrambling": WordScrambling,
        "AsciiNoising": AsciiNoising,
    }

    transforms = []
    for name in transform_names:
        if name not in transform_map:
            raise ValueError(
                f"Unknown transform: {name}. Available: {list(transform_map.keys())}"
            )
        transforms.append(transform_map[name]())

    return Compose(transforms)


__all__ = [
    "Transform",
    "Compose",
    "RandomCapitalization",
    "WordScrambling",
    "AsciiNoising",
    "load_transforms",
]

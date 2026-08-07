"""Deterministic validation helpers for structured LLM output."""

import re

RATING_MIN = 0.0
RATING_MAX = 10.0
_FENCE_PATTERN = re.compile(r'^\s*```(?:json)?\s*|\s*```\s*$', re.IGNORECASE)


def strip_json_fences(response: str) -> str:
    """Remove JSON markdown fences without changing the payload itself."""
    return _FENCE_PATTERN.sub('', response or '').strip()


def clamp_rating(raw_rating) -> float:
    """Convert a model-provided rating to a finite value in the 0-10 range."""
    try:
        rating = float(raw_rating)
    except (TypeError, ValueError):
        return RATING_MIN
    if rating != rating:  # NaN
        return RATING_MIN
    return min(max(rating, RATING_MIN), RATING_MAX)

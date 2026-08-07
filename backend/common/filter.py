def filter_none_values(data: dict) -> dict:
    """Filter out keys where the value is None."""
    return {key: value for key, value in data.items() if value is not None}

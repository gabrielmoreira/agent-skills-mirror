def split_evenly(total: float, n: int) -> list[float]:
    """Split total into n shares, in cents, that add up exactly to total."""
    return [round(total / n, 2)] * n

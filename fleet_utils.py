# fleet_utils.py
# Shared helpers for the KM-Waechter fleet service.
# Dead functions (parse_service_date, chunk_list, is_due) removed — none had callers.

KM_PER_MILE = 1.609344          # exact definition
MILES_PER_KM = 1 / KM_PER_MILE  # ≈ 0.621371


def km_to_miles(km: float) -> float:
    """Convert kilometres to miles. Used by the nightly UK partner report."""
    return km * MILES_PER_KM


def format_number(value: float) -> str:
    """Format a float to one decimal place."""
    return f"{value:.1f}"


def format_percent(value: float) -> str:
    """Format a float as a whole-number percentage string."""
    return f"{int(value)}%"


def mean(values: list) -> float:
    """Return the arithmetic mean of a list, or 0.0 for an empty list."""
    if not values:
        return 0.0
    return sum(values) / len(values)

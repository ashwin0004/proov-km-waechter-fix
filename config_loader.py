# config_loader.py
# Reads settings.cfg for KM-Waechter.
# Hand-rolled in 2013 because ConfigParser felt "too complicated" at the time.

SETTINGS_FILE = "settings.cfg"

KNOWN_KEYS = [
    "service_interval_km",
    "warn_at_percent",
    "report_title",
    "history_file",
    "log_file",
    "mileage_unit",
]


def load_settings(path: str | None = None) -> dict:
    """Parse *path* (defaults to settings.cfg) and return a str→str dict.

    Lines that are blank, start with '#', or contain no '=' are skipped.
    Keys not in KNOWN_KEYS are silently ignored (a typo will never surface —
    this is a known limitation carried over from the original design).
    """
    if path is None:
        path = SETTINGS_FILE
    settings: dict = {}
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, value = line.partition("=")
            key = key.strip()
            value = value.strip()
            if key in KNOWN_KEYS:
                settings[key] = value
    return settings


def get_int(settings: dict, key: str, fallback: int) -> int:
    """Return settings[key] as an int, or *fallback* if absent or not parseable."""
    try:
        return int(settings[key])
    except (KeyError, ValueError):
        return fallback


def get_setting(settings: dict, key: str, fallback: str = "") -> str:
    """Return settings[key], or *fallback* if the key is absent."""
    return settings.get(key, fallback)

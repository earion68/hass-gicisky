"""Badge e-ink constants and device definitions."""

from dataclasses import dataclass


@dataclass
class BadgeEinkDevice:
    """Badge e-ink device configuration."""

    name: str
    width: int
    height: int
    manufacturer: str = "Badge e-ink"


# Standard badge e-ink display configurations
BADGE_EINK_DEVICES = {
    "default": BadgeEinkDevice(
        name="e-ink Badge",
        width=800,
        height=480,
    ),
}

# Known badge e-ink device names/patterns
BADGE_EINK_NAME_PATTERNS = [
    "easyTag",  # easyTag series
    "badge",    # generic badge
    "e-ink",    # generic e-ink
]

# BLE characteristic UUIDs for badge e-ink
BADGE_EINK_WRITE_CHAR = "00001525-1212-efde-1523-785feabcd123"
BADGE_EINK_NOTIFY_CHAR = "00001526-1212-efde-1523-785feabcd123"

# Service UUIDs that might indicate badge e-ink
BADGE_EINK_SERVICE_UUIDS = [
    "0000fff0-0000-1000-8000-00805f9b34fb",  # Generic service
]


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

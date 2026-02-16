"""Constants for the Gicisky Bluetooth integration."""

from __future__ import annotations

DOMAIN = "gicisky"
LOCK = "lock"

# Device types
DEVICE_TYPE_GICISKY = "gicisky"
DEVICE_TYPE_BADGE_EINK = "badge_eink"

# Options
CONF_RETRY_COUNT = "retry_count"
CONF_WRITE_DELAY_MS = "write_delay_ms"
CONF_DEVICE_TYPE = "device_type"

# Defaults
DEFAULT_RETRY_COUNT = 3
DEFAULT_WRITE_DELAY_MS = 0
DEFAULT_DEVICE_TYPE = DEVICE_TYPE_GICISKY

# Badge e-ink characteristics
BADGE_EINK_CHAR_WRITE = "00001525-1212-efde-1523-785feabcd123"
BADGE_EINK_CHAR_NOTIFY = "00001526-1212-efde-1523-785feabcd123"

"""Badge e-ink Bluetooth device parser."""

from __future__ import annotations

import logging
from dataclasses import dataclass

from bluetooth_sensor_state_data import BluetoothData
from home_assistant_bluetooth import BluetoothServiceInfoBleak

from .const import BADGE_EINK_NAME_PATTERNS, BADGE_EINK_WRITE_CHAR, BADGE_EINK_NOTIFY_CHAR

_LOGGER = logging.getLogger(__name__)


@dataclass
class BadgeEinkDevice:
    """Badge e-ink device information."""

    name: str = "Badge e-ink"
    model: str = "Badge e-ink Display"
    manufacturer: str = "Badge e-ink"
    width: int = 800
    height: int = 480
    red: bool = True
    invert_luminance: bool = False


def _has_badge_eink_characteristics(service_info: BluetoothServiceInfoBleak) -> bool:
    """Check if device has badge e-ink characteristics."""
    try:
        if service_info.device.services:
            for svc in service_info.device.services:
                if svc.characteristics:
                    for char in svc.characteristics:
                        if char.uuid.lower() in [
                            BADGE_EINK_WRITE_CHAR.lower(),
                            BADGE_EINK_NOTIFY_CHAR.lower(),
                        ]:
                            return True
    except Exception as e:
        _LOGGER.debug("Error checking characteristics: %s", e)
    return False


def _is_badge_eink_by_name(service_info: BluetoothServiceInfoBleak) -> bool:
    """Check if device name matches badge e-ink patterns."""
    name = (service_info.name or "").lower()
    for pattern in BADGE_EINK_NAME_PATTERNS:
        if pattern.lower() in name:
            _LOGGER.info(
                "Device %s matched badge_eink name pattern: '%s'",
                service_info.address,
                pattern
            )
            return True
    return False


class BadgeEinkBluetoothDeviceData(BluetoothData):
    """Data for Badge e-ink Bluetooth devices."""

    def __init__(self) -> None:
        super().__init__()
        self.last_service_info: BluetoothServiceInfoBleak | None = None
        self.device: BadgeEinkDevice = BadgeEinkDevice()

    def supported(self, data: BluetoothServiceInfoBleak) -> bool:
        """Check if device is a supported badge e-ink device."""
        if not super().supported(data):
            return False
        
        address = data.address
        _LOGGER.debug(
            "Checking if %s is badge_eink - Name: %s, Service UUIDs: %s",
            address,
            data.name,
            data.service_uuids
        )
        
        # Strategy 1: Check for characteristic UUIDs (most reliable)
        if _has_badge_eink_characteristics(data):
            _LOGGER.info("Device %s identified as badge_eink via characteristics", address)
            return True
        
        # Strategy 2: Check device name patterns (fallback)
        if _is_badge_eink_by_name(data):
            _LOGGER.info("Device %s identified as badge_eink via name pattern", address)
            return True
        
        _LOGGER.debug("Device %s not identified as badge_eink", address)
        return False

    def _start_update(self, service_info: BluetoothServiceInfoBleak) -> None:
        """Update from BLE advertisement data."""
        if self._parse_badge_eink(service_info):
            self.last_service_info = service_info

    def _parse_badge_eink(self, service_info: BluetoothServiceInfoBleak) -> bool:
        """Parse badge e-ink device information."""
        # Extract device identifier from address
        identifier = service_info.address.replace(":", "")[-8:]
        self.set_title(f"{identifier} (Badge e-ink)")
        self.set_device_name(f"Badge e-ink {identifier}")
        self.set_device_type(f"Badge e-ink {self.device.width}x{self.device.height}")
        self.set_device_manufacturer(self.device.manufacturer)
        
        return True



"""Badge e-ink Bluetooth device parser."""

from __future__ import annotations

import logging
from dataclasses import dataclass

from bluetooth_sensor_state_data import BluetoothData
from home_assistant_bluetooth import BluetoothServiceInfoBleak

_LOGGER = logging.getLogger(__name__)

# Badge e-ink device uses standard manufacturer ID, we'll detect by service UUIDs
BADGE_EINK_SERVICE_UUID = "0000fff0-0000-1000-8000-00805f9b34fb"


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
        
        # Check for badge e-ink characteristic UUIDs
        has_eink_chars = False
        try:
            for svc in (data.device.services or []):
                for char in (svc.characteristics or []):
                    if char.uuid in [
                        "00001525-1212-efde-1523-785feabcd123",
                        "00001526-1212-efde-1523-785feabcd123",
                    ]:
                        has_eink_chars = True
                        break
        except Exception:
            pass
        
        return has_eink_chars

    def _start_update(self, service_info: BluetoothServiceInfoBleak) -> None:
        """Update from BLE advertisement data."""
        if self._parse_badge_eink(service_info):
            self.last_service_info = service_info

    def _parse_badge_eink(self, service_info: BluetoothServiceInfoBleak) -> bool:
        """Parse badge e-ink device information.
        
        Badge e-ink devices are simpler - they mainly need the address
        and basic device info.
        """
        # Extract device identifier from address
        identifier = service_info.address.replace(":", "")[-8:]
        self.set_title(f"{identifier} (Badge e-ink)")
        self.set_device_name(f"Badge e-ink {identifier}")
        self.set_device_type(f"Badge e-ink {self.device.width}x{self.device.height}")
        self.set_device_manufacturer(self.device.manufacturer)
        
        return True


import logging
from homeassistant.components.text import TextEntity, RestoreText
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.device_registry import DeviceInfo, CONNECTION_BLUETOOTH
from homeassistant.const import STATE_UNAVAILABLE, STATE_UNKNOWN
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.restore_state import RestoreEntity
from propcache.api import cached_property
from .const import (
    DOMAIN,
    DEVICE_TYPE_GICISKY,
    DEVICE_TYPE_BADGE_EINK,
)

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback
):
    async_add_entities([GiciskyTextEntity(hass, entry)])

class GiciskyTextEntity(RestoreText):
    def __init__(self, hass: HomeAssistant, entry: ConfigEntry):
        address = hass.data[DOMAIN][entry.entry_id]['address']
        device_type = hass.data[DOMAIN][entry.entry_id].get('device_type', DEVICE_TYPE_GICISKY)
        self._address = address
        self._device_type = device_type
        self._identifier = address.replace(":", "")[-8:]
        
        # Use appropriate device names based on device type
        if device_type == DEVICE_TYPE_BADGE_EINK:
            self._manufacturer = "Badge e-ink"
        else:
            self._manufacturer = "Gicisky"
        
        self._attr_name = f"{self._manufacturer} {self._identifier} Alias"
        self._attr_unique_id = f"{device_type}_{self._identifier}_alias"
        self._attr_native_max = 32  # Reasonable max length for text fields
        self._attr_native_min = 0
        self._attr_mode = "text"
        self._attr_native_value = f"{self._identifier}"

    @property
    def device_info(self) -> DeviceInfo:
        return DeviceInfo (
            connections = {
                (
                    CONNECTION_BLUETOOTH,
                    self._address,
                )
            },
            name = f"{self._manufacturer} {self._identifier}",
            manufacturer = self._manufacturer,
        )
    
    @cached_property
    def available(self) -> bool:
        """Entity always either data or empty."""
        return True

    def set_value(self, value: str) -> None:
        """Change the selected option."""
        self._attr_native_value = value

    async def async_added_to_hass(self) -> None:
        await super().async_added_to_hass()
        if (last_text_data := await self.async_get_last_text_data()) is None:
            return
        _LOGGER.debug("Restored state: %s", last_text_data)
        self._attr_native_max = last_text_data.native_max
        self._attr_native_min = last_text_data.native_min
        self._attr_native_value = last_text_data.native_value
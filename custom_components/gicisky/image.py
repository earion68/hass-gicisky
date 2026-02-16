"""Support for a single image URL as an ImageEntity."""
import logging
from homeassistant.components.image import ImageEntity, Image
from homeassistant.core import HomeAssistant, callback
from homeassistant.util import dt as dt_util
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.device_registry import DeviceInfo, CONNECTION_BLUETOOTH
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.config_entries import ConfigEntry
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
    image_coordinator = hass.data[DOMAIN][entry.entry_id]["image_coordinator"]
    async_add_entities([GiciskyImageEntity(hass, entry, image_coordinator)])

class GiciskyImageEntity(CoordinatorEntity[DataUpdateCoordinator[bytes]], ImageEntity):
    def __init__(self, hass: HomeAssistant, entry: ConfigEntry, coordinator: DataUpdateCoordinator[bytes]):
        CoordinatorEntity.__init__(self, coordinator)
        ImageEntity.__init__(self, hass)
        # self.hass = hass
        address = hass.data[DOMAIN][entry.entry_id]['address']
        device_type = hass.data[DOMAIN][entry.entry_id].get('device_type', DEVICE_TYPE_GICISKY)
        self._address = address
        self._device_type = device_type
        self._identifier = address.replace(":", "")[-8:]
        
        # Use appropriate device names based on device type
        if device_type == DEVICE_TYPE_BADGE_EINK:
            device_name = "Badge e-ink"
            self._manufacturer = "Badge e-ink"
        else:
            device_name = "Gicisky"
            self._manufacturer = "Gicisky"
        
        self._attr_name = f"{device_name} {self._identifier} Last Updated Content"
        self._attr_unique_id = f"{device_type}_{self._identifier}_last_updated_content"
        self._attr_content_type = "image/png"
        self._cached_image = Image(content_type="image/png", content=coordinator.data)

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
    
    @property
    def data(self) -> bytes:
        """Return coordinator data for this entity."""
        return self.coordinator.data
            
    def image(self) -> bytes | None:
        """Return bytes of image."""
        return self._cached_image.content

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        _LOGGER.debug("Updated image data")
        self._cached_image = Image(content_type="image/png", content=self.data)

        self._attr_image_last_updated = dt_util.now()
        super()._handle_coordinator_update()
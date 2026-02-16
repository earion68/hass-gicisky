"""Config flow for Gicisky Bluetooth integration."""

from __future__ import annotations

from collections.abc import Mapping
import dataclasses
import logging
from typing import Any

from .gicisky_ble import GiciskyBluetoothDeviceData as GiciskyDeviceData
from .badge_eink_ble import BadgeEinkBluetoothDeviceData as BadgeEinkDeviceData
import voluptuous as vol

from homeassistant.components import onboarding
from homeassistant.components.bluetooth import (
    BluetoothServiceInfoBleak,
    async_discovered_service_info,
)
from homeassistant.config_entries import (
    SOURCE_REAUTH,
    ConfigFlow,
    ConfigFlowResult,
    OptionsFlowWithReload,
)
from homeassistant.const import CONF_ADDRESS
from homeassistant.core import callback
from homeassistant.helpers.selector import (
    NumberSelector,
    NumberSelectorConfig,
    NumberSelectorMode,
)

from .const import (
    DOMAIN,
    DEVICE_TYPE_GICISKY,
    DEVICE_TYPE_BADGE_EINK,
    DEFAULT_DEVICE_TYPE,
    CONF_DEVICE_TYPE,
    CONF_RETRY_COUNT,
    CONF_WRITE_DELAY_MS,
    DEFAULT_RETRY_COUNT,
    DEFAULT_WRITE_DELAY_MS,
)
from .badge_eink_ble.const import (
    BADGE_EINK_WRITE_CHAR,
    BADGE_EINK_NOTIFY_CHAR,
    BADGE_EINK_NAME_PATTERNS,
)

_LOGGER = logging.getLogger(__name__)


OPTIONS_SCHEMA = {
    vol.Required(CONF_RETRY_COUNT, default=DEFAULT_RETRY_COUNT): NumberSelector(
        NumberSelectorConfig(
            min=1,
            max=10,
            step=1,
            mode=NumberSelectorMode.BOX,
        )
    ),
    vol.Required(CONF_WRITE_DELAY_MS, default=DEFAULT_WRITE_DELAY_MS): NumberSelector(
        NumberSelectorConfig(
            min=0,
            max=1000,
            step=1,
            mode=NumberSelectorMode.BOX,
            unit_of_measurement="ms",
        )
    ),
}


@dataclasses.dataclass
class Discovery:
    """A discovered bluetooth device."""

    title: str
    discovery_info: BluetoothServiceInfoBleak
    device_type: str
    device: GiciskyDeviceData | BadgeEinkDeviceData


def _get_device_data(device_type: str) -> GiciskyDeviceData | BadgeEinkDeviceData:
    """Get appropriate device data instance based on type."""
    if device_type == DEVICE_TYPE_BADGE_EINK:
        return BadgeEinkDeviceData()
    return GiciskyDeviceData()


def _detect_device_type(service_info: BluetoothServiceInfoBleak) -> str:
    """Detect device type from BLE service info."""
    address = service_info.address
    
    # Strategy 1: Check for badge_eink characteristics
    try:
        if service_info.device.services:
            for svc in service_info.device.services:
                if svc.characteristics:
                    for char in svc.characteristics:
                        if char.uuid.lower() in [
                            BADGE_EINK_WRITE_CHAR.lower(),
                            BADGE_EINK_NOTIFY_CHAR.lower(),
                        ]:
                            _LOGGER.info(
                                "Device %s detected as badge_eink (characteristic %s)",
                                address,
                                char.uuid
                            )
                            return DEVICE_TYPE_BADGE_EINK
    except Exception as e:
        _LOGGER.debug("Error detecting badge_eink characteristics for %s: %s", address, e)
    
    # Strategy 2: Check device name for badge_eink patterns
    name = (service_info.name or "").lower()
    for pattern in BADGE_EINK_NAME_PATTERNS:
        if pattern.lower() in name:
            _LOGGER.info(
                "Device %s detected as badge_eink (name pattern '%s')",
                address,
                pattern
            )
            return DEVICE_TYPE_BADGE_EINK
    
    # Strategy 3: Check for gicisky manufacturer ID
    if 0x5053 in service_info.manufacturer_data:
        _LOGGER.info("Device %s detected as gicisky (manufacturer 0x5053)", address)
        return DEVICE_TYPE_GICISKY
    
    # Log info for debugging
    _LOGGER.debug(
        "Device %s - couldn't auto-detect type. Name: %s, Manufacturer: %s, Service UUIDs: %s",
        address,
        service_info.name,
        {k: v.hex() if isinstance(v, bytes) else v for k, v in service_info.manufacturer_data.items()},
        service_info.service_uuids
    )
    
    return DEFAULT_DEVICE_TYPE


def _title(discovery_info: BluetoothServiceInfoBleak, device: GiciskyDeviceData | BadgeEinkDeviceData) -> str:
    return device.title or device.get_device_name() or discovery_info.name


class GiciskyConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Gicisky Bluetooth."""

    VERSION = 1

    def __init__(self) -> None:
        """Initialize the config flow."""
        self._discovery_info: BluetoothServiceInfoBleak | None = None
        self._discovered_device: GiciskyDeviceData | BadgeEinkDeviceData | None = None
        self._device_type: str = DEFAULT_DEVICE_TYPE
        self._discovered_devices: dict[str, Discovery] = {}

    async def async_step_bluetooth(
        self, discovery_info: BluetoothServiceInfoBleak
    ) -> ConfigFlowResult:
        """Handle the bluetooth discovery step."""
        await self.async_set_unique_id(discovery_info.address)
        self._abort_if_unique_id_configured()
        
        # Detect device type
        device_type = _detect_device_type(discovery_info)
        device = _get_device_data(device_type)

        if not device.supported(discovery_info):
            return self.async_abort(reason="not_supported")

        title = _title(discovery_info, device)
        self.context["title_placeholders"] = {"name": title}
        self._discovery_info = discovery_info
        self._discovered_device = device
        self._device_type = device_type

        return await self.async_step_bluetooth_confirm()

    async def async_step_bluetooth_confirm(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Confirm discovery."""
        if user_input is not None or not onboarding.async_is_onboarded(self.hass):
            return self._async_get_or_create_entry()

        self._set_confirm_only()
        return self.async_show_form(
            step_id="bluetooth_confirm",
            description_placeholders=self.context["title_placeholders"],
        )

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the user step to pick discovered device."""
        if user_input is not None:
            # Check if user selected to specify device type manually
            address = user_input[CONF_ADDRESS]
            
            # Check if this is a manual configuration
            if address.startswith("manual_"):
                return await self.async_step_manual_config()
            
            await self.async_set_unique_id(address, raise_on_progress=False)
            self._abort_if_unique_id_configured()
            discovery = self._discovered_devices[address]

            self.context["title_placeholders"] = {"name": discovery.title}

            self._discovery_info = discovery.discovery_info
            self._discovered_device = discovery.device
            self._device_type = discovery.device_type

            return self._async_get_or_create_entry()

        current_addresses = self._async_current_ids(include_ignore=False)
        for discovery_info in async_discovered_service_info(self.hass, False):
            address = discovery_info.address
            if address in current_addresses or address in self._discovered_devices:
                continue
            
            # Detect device type
            device_type = _detect_device_type(discovery_info)
            device = _get_device_data(device_type)
            
            if device.supported(discovery_info):
                self._discovered_devices[address] = Discovery(
                    title=_title(discovery_info, device),
                    discovery_info=discovery_info,
                    device_type=device_type,
                    device=device,
                )

        titles = {
            address: discovery.title
            for (address, discovery) in self._discovered_devices.items()
        }
        
        # Add option for manual configuration
        titles["manual_config"] = "Configurer manuellement (easyTag non détecté)"
        
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({vol.Required(CONF_ADDRESS): vol.In(titles)}),
        )

    async def async_step_manual_config(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle manual configuration when auto-detection fails."""
        if user_input is not None:
            address = user_input.get("mac_address", "").upper()
            device_type = user_input.get("device_type", DEFAULT_DEVICE_TYPE)
            
            # Validate MAC address format
            if not self._is_valid_mac(address):
                return self.async_show_form(
                    step_id="manual_config",
                    data_schema=vol.Schema({
                        vol.Required("mac_address"): str,
                        vol.Required("device_type"): vol.In([
                            DEVICE_TYPE_GICISKY,
                            DEVICE_TYPE_BADGE_EINK,
                        ]),
                    }),
                    errors={"mac_address": "invalid_mac"},
                )
            
            await self.async_set_unique_id(address, raise_on_progress=False)
            self._abort_if_unique_id_configured()
            
            # Create device based on selected type
            device = _get_device_data(device_type)
            self._device_type = device_type
            self._discovered_device = device
            
            # For manual config, create a minimal service info
            identifier = address.replace(":", "")[-8:]
            self.context["title_placeholders"] = {"name": f"{device_type} {identifier}"}
            
            return self._async_get_or_create_entry()
        
        return self.async_show_form(
            step_id="manual_config",
            data_schema=vol.Schema({
                vol.Required("mac_address", description={"suggested_value": "44:00:00:49:61:56"}): str,
                vol.Required("device_type", default=DEVICE_TYPE_BADGE_EINK): vol.In([
                    DEVICE_TYPE_GICISKY,
                    DEVICE_TYPE_BADGE_EINK,
                ]),
            }),
        )

    @staticmethod
    def _is_valid_mac(address: str) -> bool:
        """Validate MAC address format."""
        if not address:
            return False
        parts = address.split(":")
        if len(parts) != 6:
            return False
        try:
            for part in parts:
                int(part, 16)
            return True
        except ValueError:
            return False

    async def async_step_reauth(
        self, entry_data: Mapping[str, Any]
    ) -> ConfigFlowResult:
        """Handle a flow initialized by a reauth event."""
        device_type = entry_data.get(CONF_DEVICE_TYPE, DEFAULT_DEVICE_TYPE)
        device = _get_device_data(device_type)
        self._discovered_device = device
        self._device_type = device_type

        self._discovery_info = device.last_service_info

        # Otherwise there wasn't actually encryption so abort
        return self.async_abort(reason="reauth_successful")

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return OptionsFlowHandler()

    def _async_get_or_create_entry(
        self, bindkey: str | None = None
    ) -> ConfigFlowResult:
        data: dict[str, Any] = {
            CONF_DEVICE_TYPE: self._device_type,
        }
        if bindkey:
            data["bindkey"] = bindkey

        if self.source == SOURCE_REAUTH:
            return self.async_update_reload_and_abort(
                self._get_reauth_entry(), data=data
            )

        return self.async_create_entry(
            title=self.context["title_placeholders"]["name"],
            data=data,
        )


class OptionsFlowHandler(OptionsFlowWithReload):
    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Manage the options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        # options가 비어있으면 data에서 가져옴
        suggested_values = {**self.config_entry.data, **self.config_entry.options}

        return self.async_show_form(
            step_id="init",
            data_schema=self.add_suggested_values_to_schema(
                vol.Schema(OPTIONS_SCHEMA), suggested_values
            ),
        )

"""Config flow for the VegeHub integration."""

import logging
from typing import Any

import voluptuous as vol

from homeassistant.components.webhook import (
    async_generate_id as webhook_generate_id,
    async_generate_url as webhook_generate_url,
)
from homeassistant.config_entries import (
    ConfigEntry,
    ConfigFlow,
    ConfigFlowResult,
    OptionsFlow,
)
from homeassistant.const import (
    CONF_DEVICE,
    CONF_HOST,
    CONF_IP_ADDRESS,
    CONF_MAC,
    CONF_WEBHOOK_ID,
)
from homeassistant.core import callback
from homeassistant.helpers.service_info import zeroconf
from homeassistant.util.network import is_ip_address
from vegehub import VegeHub

from .const import DOMAIN, OPTION_DATA_TYPE_CHOICES

_LOGGER = logging.getLogger(__name__)


class VegeHubConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for VegeHub integration."""

    _hub: VegeHub
    _hostname: str
    webhook_id: str

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle a flow initiated by the user."""
        errors: dict[str, str] = {}

        if user_input is not None:
            if not is_ip_address(user_input[CONF_IP_ADDRESS]):
                # User-supplied IP address is invalid.
                errors["base"] = "invalid_ip"

            if not errors:
                self._hub = VegeHub(user_input[CONF_IP_ADDRESS])
                self._hostname = self._hub.ip_address
                errors = await self._setup_device()
                if not errors:
                    # Proceed to create the config entry
                    return await self._create_entry()

        # Show the form to allow the user to manually enter the IP address
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_IP_ADDRESS): str,
                }
            ),
            errors=errors,
        )

    async def async_step_zeroconf(
        self, discovery_info: zeroconf.ZeroconfServiceInfo
    ) -> ConfigFlowResult:
        """Handle zeroconf discovery."""

        # Extract the IP address from the zeroconf discovery info
        device_ip = discovery_info.host

        self._async_abort_entries_match({CONF_IP_ADDRESS: device_ip})

        self._hostname = discovery_info.hostname.removesuffix(".local.")
        config_url = f"http://{discovery_info.hostname[:-1]}:{discovery_info.port}"

        # Create a VegeHub object to interact with the device
        self._hub = VegeHub(device_ip)

        try:
            await self._hub.retrieve_mac_address(retries=2)
        except ConnectionError:
            return self.async_abort(reason="cannot_connect")
        except TimeoutError:
            return self.async_abort(reason="timeout_connect")

        if not self._hub.mac_address:
            return self.async_abort(reason="cannot_connect")

        # Check if this device already exists
        await self.async_set_unique_id(self._hub.mac_address)
        self._abort_if_unique_id_configured(
            updates={CONF_IP_ADDRESS: device_ip, CONF_HOST: self._hostname}
        )

        # Add title and configuration URL to the context so that the device discovery
        # tile has the correct title, and a "Visit Device" link available.
        self.context.update(
            {
                "title_placeholders": {"host": self._hostname + " (" + device_ip + ")"},
                "configuration_url": (config_url),
            }
        )

        # If the device is new, allow the user to continue setup
        return await self.async_step_zeroconf_confirm()

    async def async_step_zeroconf_confirm(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle user confirmation for a discovered device."""
        errors: dict[str, str] = {}
        if user_input is not None:
            errors = await self._setup_device()
            if not errors:
                return await self._create_entry()

        # Show the confirmation form
        self._set_confirm_only()
        return self.async_show_form(step_id="zeroconf_confirm", errors=errors)

    async def _setup_device(self) -> dict[str, str]:
        """Set up the VegeHub device."""
        errors: dict[str, str] = {}
        self.webhook_id = webhook_generate_id()
        webhook_url = webhook_generate_url(
            self.hass,
            self.webhook_id,
            allow_external=False,
            allow_ip=True,
        )

        # Send the webhook address to the hub as its server target.
        # This step can happen in the init, because that gets executed
        # every time Home Assistant starts up, and this step should
        # only happen in the initial setup of the VegeHub.
        try:
            await self._hub.setup("", webhook_url, retries=1)
        except ConnectionError:
            errors["base"] = "cannot_connect"
        except TimeoutError:
            errors["base"] = "timeout_connect"

        if not self._hub.mac_address:
            errors["base"] = "cannot_connect"

        return errors

    async def _create_entry(self) -> ConfigFlowResult:
        """Create a config entry for the device."""

        # Check if this device already exists
        await self.async_set_unique_id(self._hub.mac_address)
        self._abort_if_unique_id_configured()

        # Save Hub info to be used later when defining the VegeHub object
        info_data = {
            CONF_IP_ADDRESS: self._hub.ip_address,
            CONF_HOST: self._hostname,
            CONF_MAC: self._hub.mac_address,
            CONF_DEVICE: self._hub.info,
            CONF_WEBHOOK_ID: self.webhook_id,
        }

        # Create the config entry for the new device
        return self.async_create_entry(title=self._hostname, data=info_data)

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: ConfigEntry) -> OptionsFlow:
        """Return the options flow handler for this integration."""
        return VegehubOptionsFlowHandler(config_entry)


class VegehubOptionsFlowHandler(OptionsFlow):
    """Handle an options flow for VegeHub."""

    def __init__(self, config_entry) -> None:
        """Initialize VegeHub options flow."""
        self.coordinator = config_entry.runtime_data

    async def async_step_init(self, user_input=None) -> ConfigFlowResult:
        """Manage the options for VegeHub."""
        if user_input is not None:
            # Update the config entry options with the new user input
            self.hass.config_entries.async_update_entry(
                self.config_entry, options=user_input
            )

            # Trigger a reload of the config entry to apply the new options
            await self.hass.config_entries.async_reload(self.config_entry.entry_id)

            # Process the user inputs and update the config entry options
            return self.async_create_entry(title="", data=user_input)

        num_sensors = self.coordinator.vegehub.num_sensors
        num_actuators = self.coordinator.vegehub.num_actuators

        options_schema: dict[Any, Any] = {}

        if num_sensors > 0:
            # Define the schema for the options that the user can modify
            options_schema.update(
                {
                    vol.Required(
                        f"data_type_{i}",
                        default=self.config_entry.options.get(
                            f"data_type_{i}", OPTION_DATA_TYPE_CHOICES[0]
                        ),
                    ): vol.In(OPTION_DATA_TYPE_CHOICES)
                    for i in range(num_sensors)
                }
            )

        # Check to see if there are actuators. If there are, add the duration field.
        if num_actuators > 0:
            # Get the current duration value from the config entry
            current_duration = self.config_entry.options.get("user_act_duration", 0)
            if current_duration <= 0:
                current_duration = 600

            options_schema.update(
                {vol.Required("user_act_duration", default=current_duration): int}
            )

        _LOGGER.debug(
            # Print the options schema to the log for debugging
            "Options schema: %s",
            options_schema,
        )

        # Show the form to the user with the current options
        return self.async_show_form(
            step_id="init", data_schema=vol.Schema(options_schema)
        )

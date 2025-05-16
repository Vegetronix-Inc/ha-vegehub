"""Switch configuration for VegeHub integration."""

from itertools import count
import logging
from typing import Any

from homeassistant.components.switch import (
    SwitchDeviceClass,
    SwitchEntity,
    SwitchEntityDescription,
)
from homeassistant.const import STATE_OFF, STATE_ON
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback
from homeassistant.helpers.typing import StateType

from .coordinator import VegeHubConfigEntry, VegeHubCoordinator
from .entity import VegeHubEntity

SWITCH_TYPES: dict[str, SwitchEntityDescription] = {
    "switch": SwitchEntityDescription(
        key="switch",
        translation_key="switch",
        device_class=SwitchDeviceClass.SWITCH,
    )
}

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: VegeHubConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up Vegetronix switches from a config entry."""
    switches: list[VegeHubSwitch] = []
    coordinator = config_entry.runtime_data

    # This index corresponds to the actuator number in the VegeHub.
    index = count(0)

    # Add each switch
    for _i in range(coordinator.vegehub.num_actuators):
        switch = VegeHubSwitch(
            index=next(index),
            duration=int(config_entry.options.get("user_act_duration", 0) or 600),
            coordinator=coordinator,
            description=SWITCH_TYPES["switch"],
        )
        switches.append(switch)

    async_add_entities(switches)


class VegeHubSwitch(VegeHubEntity, SwitchEntity):
    """Class for VegeHub Switches."""

    _attr_device_class = SwitchDeviceClass.SWITCH

    def __init__(
        self,
        index: int,
        duration: int,
        coordinator: VegeHubCoordinator,
        description: SwitchEntityDescription,
    ) -> None:
        """Initialize the switch."""
        super().__init__(coordinator)
        self.entity_description = description
        # Set unique ID for pulling data from the coordinator
        self.data_key = f"actuator_{index}".lower()
        self._attr_unique_id = f"{self._mac_address}_{self.data_key}"
        self._attr_translation_placeholders = {"index": str(index + 1)}
        self._attr_available = False
        self.index = index
        self.duration = duration

    @property
    def state(self) -> StateType:
        """Return the switch's current value."""
        if self.coordinator.data is None or self._attr_unique_id is None:
            return STATE_OFF
        if self.coordinator.data.get(self.data_key, 0) > 0:
            return STATE_ON
        return STATE_OFF

    def turn_on(self, **kwargs: Any) -> None:
        """Turn the switch on."""
        _LOGGER.info("Switch %s ON", self.index)
        self.hass.add_job(
            self.coordinator.vegehub.set_actuator, 1, self.index, self.duration
        )

    def turn_off(self, **kwargs: Any) -> None:
        """Turn the switch off."""
        _LOGGER.info("Switch %s OFF", self.index)
        self.hass.add_job(
            self.coordinator.vegehub.set_actuator, 0, self.index, self.duration
        )

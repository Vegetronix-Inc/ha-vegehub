"""Sensor configuration for VegeHub integration."""

from itertools import count
import logging

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
)
from homeassistant.const import PERCENTAGE, UnitOfElectricPotential, UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback
from vegehub import therm200_transform, vh400_transform

from .const import OPTION_DATA_TYPE_CHOICES
from .coordinator import VegeHubConfigEntry, VegeHubCoordinator
from .entity import VegeHubEntity

_LOGGING = logging.getLogger(__name__)

SENSOR_TYPES: dict[str, SensorEntityDescription] = {
    OPTION_DATA_TYPE_CHOICES[0]: SensorEntityDescription(
        key="analog_sensor",
        translation_key="analog_sensor",
        device_class=SensorDeviceClass.VOLTAGE,
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        suggested_display_precision=2,
    ),
    OPTION_DATA_TYPE_CHOICES[1]: SensorEntityDescription(
        key="vh400_sensor",
        translation_key="vh400_sensor",
        device_class=SensorDeviceClass.MOISTURE,
        native_unit_of_measurement=PERCENTAGE,
        suggested_display_precision=2,
    ),
    OPTION_DATA_TYPE_CHOICES[2]: SensorEntityDescription(
        key="therm200_sensor",
        translation_key="therm200_sensor",
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        suggested_display_precision=2,
    ),
    "battery": SensorEntityDescription(
        key="battery",
        translation_key="battery",
        device_class=SensorDeviceClass.VOLTAGE,
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        suggested_display_precision=1,
    ),
}


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: VegeHubConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up Vegetronix sensors from a config entry."""
    sensors: list[VegeHubSensor] = []
    coordinator = config_entry.runtime_data

    # This is the index in the updates from the VegeHub that will correspond to
    # each sensor.
    update_index = count(0)

    # Add each analog sensor input
    for _i in range(coordinator.vegehub.num_sensors):
        index = next(update_index)
        data_type = config_entry.options.get(
            f"data_type_{index}", OPTION_DATA_TYPE_CHOICES[0]
        )
        sensor = VegeHubSensor(
            index=index,
            coordinator=coordinator,
            description=SENSOR_TYPES[data_type],
        )
        sensors.append(sensor)

    # Add the battery sensor
    if not coordinator.vegehub.is_ac:
        sensors.append(
            VegeHubSensor(
                index=next(update_index),
                coordinator=coordinator,
                description=SENSOR_TYPES["battery"],
            )
        )

    async_add_entities(sensors)


class VegeHubSensor(VegeHubEntity, SensorEntity):
    """Class for VegeHub Analog Sensors."""

    _attr_suggested_display_precision = 2

    def __init__(
        self,
        index: int,
        coordinator: VegeHubCoordinator,
        description: SensorEntityDescription,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self.entity_description = description
        # Set unique ID for pulling data from the coordinator
        if description.key == "battery":
            self.data_key = "battery"
        else:
            self.data_key = f"analog_{index}"
            self._attr_translation_placeholders = {"index": str(index + 1)}
        self._attr_unique_id = f"{self._mac_address}_{self.data_key}"
        self._attr_available = False
        self._attr_device_class = description.device_class
        self._attr_native_unit_of_measurement = description.native_unit_of_measurement

    @property
    def native_value(self) -> float | None:
        """Return the sensor's current value."""
        if self.coordinator.data is None or self._attr_unique_id is None:
            return None
        val = self.coordinator.data.get(self.data_key)

        if not val:
            return None

        _LOGGING.debug(
            "Sensor %s: %s = %s",
            self._attr_unique_id,
            self.entity_description.key,
            val,
        )

        if self.entity_description.key == "vh400_sensor":
            # Convert the vh400 sensor value to percentage
            return vh400_transform(val)
        if self.entity_description.key == "therm200_sensor":
            # Convert the therm200 sensor value to Celsius
            return therm200_transform(val)
        return val

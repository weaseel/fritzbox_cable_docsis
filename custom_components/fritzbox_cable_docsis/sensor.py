"""GitHub sensor platform."""
import logging
import re
from datetime import timedelta
from typing import Any, Callable, Dict, Optional
from urllib import parse

import voluptuous as vol
from aiohttp import ClientError

from homeassistant.const import (
    ATTR_VOLTAGE,
    DEVICE_CLASS_SIGNAL_STRENGTH,
    DEVICE_CLASS_ILLUMINANCE,
    SIGNAL_STRENGTH_DECIBELS,
)

from homeassistant.components.sensor import PLATFORM_SCHEMA
from homeassistant.const import (
    CONF_IP_ADDRESS,
    CONF_USERNAME,
    CONF_PASSWORD,
)
from homeassistant.helpers.aiohttp_client import async_get_clientsession
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.typing import (
    ConfigType,
    DiscoveryInfoType,
    HomeAssistantType,
)

from .const import DOMAIN

fritzbox_docsys = []
data_values = []
signals = ["signal 1", "signal 2", "signal 3"]

_LOGGER = logging.getLogger(__name__)
# Time between updating data from GitHub
SCAN_INTERVAL = timedelta(seconds=5)


PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_IP_ADDRESS): cv.string,
        vol.Required(CONF_USERNAME): cv.string,
        vol.Required(CONF_PASSWORD): cv.string,
    }
)


async def async_setup_platform(
    hass: HomeAssistantType,
    config: ConfigType,
    async_add_entities: Callable,
    discovery_info: None,
) -> None:
    """Set up the sensor platform."""
    global fritzbox_docsys
    global data_values

    n = 0
    for signal in signals:
        data_values.append(0)
        fritzbox_docsys.append(FritzBoxDocsis(signal, n))
        n += 1

    async_add_entities(fritzbox_docsys, update_before_add=True)


def async_update_device_state():
    _LOGGER.warning("Updating Device State")
    n = float(0)
    index = 0
    for signal in signals:
        n += 1
        data_values[index] = data_values[index] + n
        _LOGGER.warning("   Value " + str(data_values[index]))
        index += 1

    _LOGGER.warning("Length: " + str(len(data_values)))

    for device in fritzbox_docsys:
        device.async_schedule_update_ha_state(True)


class FritzBoxDocsis(Entity):
    """Representation of a Sensor."""

    device_class = DEVICE_CLASS_SIGNAL_STRENGTH
    _attr_unit_of_measurement = SIGNAL_STRENGTH_DECIBELS

    def __init__(self, name: str, index: int):
        self._increment = index
        self._name = "FritzBoxDocsisInfo_" + str(index)
        self._name_output = "FritzBoxDocsisInfo_" + str(index)
        self._signal_power = float(0)

    @property
    def unique_id(self) -> str:
        """Return the unique ID of the sensor."""
        return str(self.name)

    @property
    def state(self) -> float:
        """Return the unique ID of the sensor."""
        return self._signal_power

    @property
    def name(self) -> str:
        """Return the unique ID of the sensor."""
        return self._name_output

    @property
    def available(self):
        """Return True if device is available."""
        return True

    @property
    def device_info(self):
        """Return a device description for device registry."""

        return {
            'name': self._name_output,
            'signal_power': self._signal_power,
        }

    async def async_update(self):
        _LOGGER.warning("signal_power length: " + str(len(data_values)) + " index: " + str(self._increment))
        if len(data_values) >= self._increment:
            signal_power = data_values[self._increment]
            _LOGGER.warning("Setting " + str(self._increment) + " to ")
            self._signal_power = signal_power
            if self._signal_power > 1000:
                self._signal_power = 0



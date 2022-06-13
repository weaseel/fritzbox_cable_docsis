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

    fritzbox_docsys = [FritzBoxDocsis(config[CONF_IP_ADDRESS], config[CONF_USERNAME], config[CONF_PASSWORD], 1),
                       FritzBoxDocsis("192.168.99.2", config[CONF_USERNAME], config[CONF_PASSWORD], 2)]
    async_add_entities(fritzbox_docsys, update_before_add=True)


def async_update_device_state():
    _LOGGER.warning("Updating Device State")
    n = float(0)
    for value in fritzbox_docsys:
        n += 1
        _LOGGER.warning("   Device " + str(n))
        value.set_signal_power(value.state() + n)


class FritzBoxDocsis(Entity):
    """Representation of a Sensor."""

    device_class = DEVICE_CLASS_SIGNAL_STRENGTH
    _attr_unit_of_measurement = SIGNAL_STRENGTH_DECIBELS

    def __init__(self, ip: str, username: str, password: str, increment: float):
        self._ip_address = ip
        self._username = username
        self._password = password
        self._increment = increment
        self._name = "FritzBoxDocsisInfo_" + str(increment)
        self._signal_power = float(0)

    @property
    def unique_id(self) -> str:
        """Return the unique ID of the sensor."""
        return str(self._ip_address)

    @property
    def state(self) -> float:
        """Return the unique ID of the sensor."""
        return self._signal_power

    @property
    def name(self) -> str:
        """Return the unique ID of the sensor."""
        return self._name

    @property
    def available(self):
        """Return True if device is available."""
        return True

    @property
    def device_info(self):
        """Return a device description for device registry."""

        return {
            'ip_adress': self._ip_address,
            'username': self._username,
            'signal_power': self._signal_power,
        }

    def set_signal_power(self, signal_power):
        _LOGGER.warning("Setting " + str(self._increment) + " to " + str(signal_power))
        self._signal_power = signal_power
        if self._signal_power > 1000:
            self._signal_power = 0



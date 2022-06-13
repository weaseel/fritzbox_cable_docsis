"""GitHub sensor platform."""
import logging
import re
from datetime import timedelta
from typing import Any, Callable, Dict, Optional
from urllib import parse

import voluptuous as vol
from aiohttp import ClientError

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
    _LOGGER.info("FritzBoxDocsis init start")
    fritzbox_docsys = [FritzBoxDocsis(config[CONF_IP_ADDRESS], config[CONF_USERNAME], config[CONF_PASSWORD])]
    async_add_entities(fritzbox_docsys, update_before_add=True)


class FritzBoxDocsis(Entity):
    """Representation of a Sensor."""

    def __init__(self, ip: str, username: str, password: str):
        self._ip_address = ip
        self._username = username
        self._password = password
        self._signal_power = float(0)
        _LOGGER.info("FritzBoxDocsis init done")

    @property
    def unique_id(self) -> str:
        """Return the unique ID of the sensor."""
        return str(self._ip_address)

    @property
    def signal_power(self) -> float:
        """Return the unique ID of the sensor."""
        return self._signal_power

    async def async_update(self):
        """Fetch new state data for the sensor.
        This is the only method that should fetch new data for Home Assistant.
        """
        self._signal_power += 1
        _LOGGER.info("Current Signal Power: " + str(self._signal_power))


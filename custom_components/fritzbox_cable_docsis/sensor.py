"""GitHub sensor platform."""
import logging
import re
from datetime import timedelta
from typing import Any, Callable, Dict, Optional
from urllib import parse

import voluptuous as vol
from aiohttp import ClientError

from homeassistant.const import (
    DEVICE_CLASS_SIGNAL_STRENGTH,
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

from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
    UpdateFailed,
)

from .const import DOMAIN

fritzbox_docsys = []
signals = ["signal 1", "signal 2", "signal 3"]

_LOGGER = logging.getLogger(__name__)
# Time between updating data from GitHub
#SCAN_INTERVAL = timedelta(seconds=5)


PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_IP_ADDRESS): cv.string,
        vol.Required(CONF_USERNAME): cv.string,
        vol.Required(CONF_PASSWORD): cv.string,
    }
)


async def async_setup_entry(hass, entry, async_add_entities):
    """Config entry example."""
    # assuming API object stored here by __init__.py

    coordinator = MyCoordinator(hass)

    # Fetch initial data so we have data when entities subscribe
    #
    # If the refresh fails, async_config_entry_first_refresh will
    # raise ConfigEntryNotReady and setup will try again later
    #
    # If you do not want to retry setup on failure, use
    # coordinator.async_refresh() instead
    #
    await coordinator.async_config_entry_first_refresh()

    async_add_entities(
        FritzBoxDocsis(coordinator, signals[idx], idx) for idx, ent in signals
    )


class MyCoordinator(DataUpdateCoordinator):
    """My custom coordinator."""

    def __init__(self, hass):
        """Initialize my coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            # Name of the data. For logging purposes.
            name="FritzBoxDocsisInfo",
            # Polling interval. Will only be polled if there are subscribers.
            update_interval=timedelta(seconds=10),
        )
        self.dataObject = [0, 0, 0]

    async def _async_update_data(self):
        """Fetch data from API endpoint.

        This is the place to pre-process the data to lookup tables
        so entities can quickly look up their data.
        """
        _LOGGER.warning("COORDINATOR - _async_update_data")

        for i in range(0, 2):
            self.data[i] += i


class FritzBoxDocsis(CoordinatorEntity):
    """Representation of a Sensor."""

    device_class = DEVICE_CLASS_SIGNAL_STRENGTH
    _attr_unit_of_measurement = SIGNAL_STRENGTH_DECIBELS

    def __init__(self, coordinator, name: str, index: int):
        super().__init__(coordinator)
        self.idx = index
        self._name = "FritzBoxDocsisInfo_" + str(name)
        self._signal_power = float(0)

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        _LOGGER.warning("_handle_coordinator_update: " + self._name + " index: " + str(self.idx))
        self._signal_power = self.coordinator.data[self.idx]
        self.async_write_ha_state()

    @property
    def unique_id(self) -> str:
        """Return the unique ID of the sensor."""
        return str(self._name)

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
            'name': self._name,
            'signal_power': self._signal_power,
        }

    async def async_update(self):
        _LOGGER.warning("async_update: " + self._name + " index: " + str(self._signal_power))



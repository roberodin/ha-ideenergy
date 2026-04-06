# Copyright (C) 2021-2022 Luis López <luis@cuarentaydos.com>
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301,
# USA.

import logging
from typing import Any

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import DiscoveryInfoType
from homeassistant.util import slugify

from .const import (
    CONF_HIGH_POWER_THRESHOLD,
    DEFAULT_HIGH_POWER_THRESHOLD,
    DOMAIN,
)
from .datacoordinator import DATA_ATTR_MEASURE_INSTANT, IDeCoordinator

_LOGGER = logging.getLogger(__name__)


class HighPowerConsumptionAlert(BinarySensorEntity):
    """Binary sensor that activates when power consumption exceeds a threshold."""

    _attr_device_class = BinarySensorDeviceClass.POWER
    _attr_has_entity_name = True
    _attr_name = "High Power Consumption"
    _attr_icon = "mdi:flash-alert"

    def __init__(
        self,
        coordinator: IDeCoordinator,
        device_info: DeviceInfo,
        threshold: int,
    ) -> None:
        self._coordinator = coordinator
        self._threshold = threshold
        self._attr_device_info = device_info
        self._attr_entity_registry_enabled_default = True
        self._last_is_on: bool | None = None

        cups = dict(device_info["identifiers"])["cups"]
        self._attr_unique_id = slugify(
            f"{cups}-high-power-consumption", separator="-"
        )

    @property
    def is_on(self) -> bool | None:
        power = self._coordinator.data.get(DATA_ATTR_MEASURE_INSTANT)
        if power is None:
            return None
        return power > self._threshold

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        power = self._coordinator.data.get(DATA_ATTR_MEASURE_INSTANT)
        return {
            "threshold": self._threshold,
            "current_power": power,
        }

    @property
    def should_poll(self) -> bool:
        return False

    @callback
    def _handle_coordinator_update(self) -> None:
        current = self.is_on
        if current != self._last_is_on:
            self._last_is_on = current
            self.async_write_ha_state()

    async def async_added_to_hass(self) -> None:
        self.async_on_remove(
            self._coordinator.async_add_listener(self._handle_coordinator_update)
        )


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType | None = None,
):
    coordinator, device_info = hass.data[DOMAIN][config_entry.entry_id]
    threshold = config_entry.options.get(
        CONF_HIGH_POWER_THRESHOLD, DEFAULT_HIGH_POWER_THRESHOLD
    )

    async_add_entities(
        [HighPowerConsumptionAlert(coordinator, device_info, threshold)]
    )

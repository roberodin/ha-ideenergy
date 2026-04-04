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

from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import DiscoveryInfoType
from homeassistant.util import slugify

from .const import DOMAIN
from .datacoordinator import IDeCoordinator

_LOGGER = logging.getLogger(__name__)

PLATFORM = "button"


class ForceUpdateButton(ButtonEntity):
    """Button to force an immediate update of MEASURE data."""

    def __init__(
        self,
        coordinator: IDeCoordinator,
        device_info: DeviceInfo,
    ) -> None:
        self._coordinator = coordinator
        self._attr_has_entity_name = True
        self._attr_name = "Force Update"
        self._attr_icon = "mdi:refresh"

        cups = dict(device_info["identifiers"])["cups"]
        self._attr_unique_id = slugify(f"{cups}-force-update", separator="-")
        self._attr_device_info = device_info
        self._attr_entity_registry_enabled_default = True

    async def async_press(self) -> None:
        """Handle the button press."""
        _LOGGER.debug("Force update button pressed, triggering MEASURE update")
        await self._coordinator.async_force_measure_update()


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType | None = None,
):
    coordinator, device_info = hass.data[DOMAIN][config_entry.entry_id]

    entities = [
        ForceUpdateButton(coordinator=coordinator, device_info=device_info),
    ]
    async_add_entities(entities)

"""Comfosplit IKARO HW Modbus device model."""

from __future__ import annotations

from modbus_connection import ModbusUnit
from modbus_connection.model import enum

from .base import (
    BaseIdealclimaDevice,
    BaseIdealclimaReadings,
    BaseIdealclimaSettings,
)
from .enums import IkaroMode


class IkaroReadings(BaseIdealclimaReadings):
    """Input registers for Comfosplit IKARO HW."""


class IkaroSettings(BaseIdealclimaSettings):
    """Holding registers for Comfosplit IKARO HW."""

    mode = enum(28302, IkaroMode, signed=True, writable=True, force_fc16=True)


class IkaroHW(BaseIdealclimaDevice[IkaroReadings, IkaroSettings]):
    """Comfosplit IKARO HW fan coil unit."""

    def __init__(self, unit: ModbusUnit) -> None:
        """Initialize an IKARO HW device bound to a ModbusUnit."""
        super().__init__(unit, IkaroReadings(unit), IkaroSettings(unit))

    async def async_set_power(self, enabled: bool, *, stop_fan: bool = True) -> None:
        """Turn the unit on or off; stops the fan by default when turning off."""
        await self._async_set_power(enabled, stop_fan=stop_fan)

    async def async_set_mode(self, mode: IkaroMode) -> None:
        """Set the operating mode (register 28302)."""
        await self.settings.write("mode", mode)

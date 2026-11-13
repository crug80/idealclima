"""Shared base components and device logic for Idealclima units."""

from __future__ import annotations

from modbus_connection import ModbusUnit
from modbus_connection.model import (
    Component,
    Device,
    UpdateReport,
    boolean,
    enum,
    gauge,
)

from .enums import FanSpeed


class BaseIdealclimaReadings(Component):
    """Common input registers shared by Idealclima fan coil units."""

    register_space = "input"

    ambient_temperature = gauge(46801, 0.1, signed=True, unit="°C")


class BaseIdealclimaSettings(Component):
    """Common holding registers shared by Idealclima fan coil units."""

    register_space = "holding"
    max_gap = 0

    power = boolean(28301, writable=True, force_fc16=True)
    fan_speed = enum(28303, FanSpeed, signed=True, writable=True, force_fc16=True)
    target_temp_cool = gauge(
        28310, 0.1, signed=True, writable=True, unit="°C", force_fc16=True
    )
    target_temp_heat = gauge(
        28311, 0.1, signed=True, writable=True, unit="°C", force_fc16=True
    )


class BaseIdealclimaDevice[
    R: BaseIdealclimaReadings,
    S: BaseIdealclimaSettings,
](Device):
    """Base device wrapping readings and settings components."""

    readings: R
    settings: S

    def __init__(self, unit: ModbusUnit, readings: R, settings: S) -> None:
        """Initialize the device with a shared Modbus unit and its components."""
        super().__init__(unit)
        self.readings = readings
        self.settings = settings

    async def async_update_readings(self) -> UpdateReport:
        """Poll input registers (live sensor readings)."""
        return await self.async_poll(("readings",))

    async def async_update_settings(self) -> UpdateReport:
        """Poll holding registers (configuration and setpoints)."""
        return await self.async_poll(("settings",))

    async def async_update(self) -> UpdateReport:
        """Poll both readings and settings."""
        return await self.async_poll(("readings", "settings"))

    async def _async_set_power(self, enabled: bool, *, stop_fan: bool) -> None:
        """Set unit power and optionally stop the fan when turning off."""
        await self.settings.write("power", enabled)
        if not enabled and stop_fan:
            await self.settings.write("fan_speed", FanSpeed.OFF)

    async def async_set_fan_speed(self, speed: FanSpeed) -> None:
        """Set the target fan speed (register 28303)."""
        await self.settings.write("fan_speed", speed)

    async def async_set_target_temp_cool(self, temperature: float) -> None:
        """Set the cooling target temperature in °C (register 28310)."""
        await self.settings.write("target_temp_cool", temperature)

    async def async_set_target_temp_heat(self, temperature: float) -> None:
        """Set the heating target temperature in °C (register 28311)."""
        await self.settings.write("target_temp_heat", temperature)

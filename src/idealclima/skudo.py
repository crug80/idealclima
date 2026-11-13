"""Radiantore SKUDO DC Inverter Modbus device model."""

from __future__ import annotations

from modbus_connection import ModbusUnit
from modbus_connection.model import boolean, enum, gauge, integer

from .base import (
    BaseIdealclimaDevice,
    BaseIdealclimaReadings,
    BaseIdealclimaSettings,
)
from .enums import SkudoMode, TemperatureUnit


def _validate_timer_hours(value: int) -> int:
    """Validate SKUDO timer hours (0 = disabled, 1-11 hours)."""
    if not 0 <= value <= 11:
        raise ValueError(f"Timer hours must be between 0 and 11, got {value}")
    return value


class SkudoReadings(BaseIdealclimaReadings):
    """Input registers for Radiantore SKUDO DC Inverter (46801-46810).

    Uses ``max_gap = 1`` so 46801-46810 are polled in a single 0x04 request
    while skipping 46803 and 46807.
    """

    max_gap = 1

    coil_temperature = gauge(46802, 0.1, signed=True, unit="°C")
    fan_rpm = integer(46804, signed=True, unit="rpm")
    valve_command = boolean(46805)
    power_state = boolean(46806)
    motor_alarm = boolean(46808)
    ambient_sensor_alarm = boolean(46809)
    coil_sensor_alarm = boolean(46810)


class SkudoSettings(BaseIdealclimaSettings):
    """Holding registers for Radiantore SKUDO DC Inverter (28301-28327)."""

    mode = enum(28302, SkudoMode, signed=True, writable=True, force_fc16=True)
    key_lock = boolean(28304, writable=True, force_fc16=True)
    sleep = boolean(28305, writable=True, force_fc16=True)
    timer_off_hours = integer(
        28306, signed=True, writable=_validate_timer_hours, force_fc16=True
    )
    timer_on_hours = integer(
        28307, signed=True, writable=_validate_timer_hours, force_fc16=True
    )
    max_target_temp = gauge(
        28308, 0.1, signed=True, writable=True, unit="°C", force_fc16=True
    )
    min_target_temp = gauge(
        28309, 0.1, signed=True, writable=True, unit="°C", force_fc16=True
    )
    target_temp_auto_cool = gauge(
        28312, 0.1, signed=True, writable=True, unit="°C", force_fc16=True
    )
    target_temp_auto_heat = gauge(
        28313, 0.1, signed=True, writable=True, unit="°C", force_fc16=True
    )
    anti_draft_threshold = gauge(
        28314, 0.1, signed=True, writable=True, unit="°C", force_fc16=True
    )
    anti_draft_enabled = boolean(28315, writable=True, force_fc16=True)
    super_silence_enabled = boolean(28316, writable=True, force_fc16=True)
    valve_present = boolean(28317, writable=True, force_fc16=True)
    temperature_unit = enum(
        28319, TemperatureUnit, signed=True, writable=True, force_fc16=True
    )
    key_lock_enabled = boolean(28322, writable=True, force_fc16=True)
    remote_enabled_with_key_lock = boolean(28323, writable=True, force_fc16=True)
    password_enabled = boolean(28324, writable=True, force_fc16=True)
    fan_intermittent = boolean(28327, writable=True, force_fc16=True)


class SkudoDCInverter(BaseIdealclimaDevice[SkudoReadings, SkudoSettings]):
    """Radiantore SKUDO DC Inverter fan coil unit."""

    def __init__(self, unit: ModbusUnit) -> None:
        """Initialize a SKUDO DC Inverter device bound to a ModbusUnit."""
        super().__init__(unit, SkudoReadings(unit), SkudoSettings(unit))

    async def async_set_power(self, enabled: bool, *, stop_fan: bool = False) -> None:
        """Turn the unit on or off."""
        await self._async_set_power(enabled, stop_fan=stop_fan)

    async def async_set_mode(self, mode: SkudoMode) -> None:
        """Set the operating mode (register 28302)."""
        await self.settings.write("mode", mode)

    async def async_set_key_lock(self, locked: bool) -> None:
        """Lock or unlock the onboard panel keys (register 28304)."""
        await self.settings.write("key_lock", locked)

    async def async_set_sleep(self, enabled: bool) -> None:
        """Enable or disable sleep mode (register 28305)."""
        await self.settings.write("sleep", enabled)

    async def async_set_timer_off_hours(self, hours: int) -> None:
        """Set auto-off timer in hours, 0 to disable or 1-11 (register 28306)."""
        await self.settings.write("timer_off_hours", hours)

    async def async_set_timer_on_hours(self, hours: int) -> None:
        """Set auto-on timer in hours, 0 to disable or 1-11 (register 28307)."""
        await self.settings.write("timer_on_hours", hours)

    async def async_set_max_target_temp(self, temperature: float) -> None:
        """Set maximum allowed target temperature in °C (register 28308)."""
        await self.settings.write("max_target_temp", temperature)

    async def async_set_min_target_temp(self, temperature: float) -> None:
        """Set minimum allowed target temperature in °C (register 28309)."""
        await self.settings.write("min_target_temp", temperature)

    async def async_set_target_temp_auto_cool(self, temperature: float) -> None:
        """Set cooling target temperature in auto mode in °C (register 28312)."""
        await self.settings.write("target_temp_auto_cool", temperature)

    async def async_set_target_temp_auto_heat(self, temperature: float) -> None:
        """Set heating target temperature in auto mode in °C (register 28313)."""
        await self.settings.write("target_temp_auto_heat", temperature)

    async def async_set_anti_draft_threshold(self, temperature: float) -> None:
        """Set coil anti-draft threshold temperature in °C (register 28314)."""
        await self.settings.write("anti_draft_threshold", temperature)

    async def async_set_anti_draft_enabled(self, enabled: bool) -> None:
        """Enable or disable the anti-draft function (register 28315)."""
        await self.settings.write("anti_draft_enabled", enabled)

    async def async_set_super_silence_enabled(self, enabled: bool) -> None:
        """Enable or disable super silence speed availability (register 28316)."""
        await self.settings.write("super_silence_enabled", enabled)

    async def async_set_valve_present(self, present: bool) -> None:
        """Configure whether a water valve actuator is present (register 28317)."""
        await self.settings.write("valve_present", present)

    async def async_set_temperature_unit(self, unit: TemperatureUnit) -> None:
        """Set display temperature unit (register 28319)."""
        await self.settings.write("temperature_unit", unit)

    async def async_set_key_lock_enabled(self, enabled: bool) -> None:
        """Enable or disable the key lock feature (register 28322)."""
        await self.settings.write("key_lock_enabled", enabled)

    async def async_set_remote_enabled_with_key_lock(self, enabled: bool) -> None:
        """Allow or block IR remote control when key lock is active (register 28323)."""
        await self.settings.write("remote_enabled_with_key_lock", enabled)

    async def async_set_password_enabled(self, enabled: bool) -> None:
        """Enable or disable onboard terminal password protection (register 28324)."""
        await self.settings.write("password_enabled", enabled)

    async def async_set_fan_intermittent(self, enabled: bool) -> None:
        """Enable or disable intermittent fan at target temperature (register 28327)."""
        await self.settings.write("fan_intermittent", enabled)

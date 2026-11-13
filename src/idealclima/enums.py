"""Enumerations for Idealclima Modbus fan coil units."""

from __future__ import annotations

from enum import IntEnum


class FanSpeed(IntEnum):
    """Fan speed values for holding register 28303."""

    OFF = 0
    SUPER_SILENCE = 1
    LOW = 2
    MEDIUM = 3
    HIGH = 4
    AUTO = 6


class IkaroMode(IntEnum):
    """Operating mode values for Comfosplit IKARO HW (register 28302)."""

    OFF = 0
    COOL = 1
    DRY = 2
    FAN_ONLY = 3
    HEAT = 4


class SkudoMode(IntEnum):
    """Operating mode values for Radiantore SKUDO DC Inverter (register 28302)."""

    AUTO = 0
    COOL = 1
    DRY = 2
    FAN_ONLY = 3
    HEAT = 4


class TemperatureUnit(IntEnum):
    """Display temperature unit for SKUDO DC Inverter (register 28319)."""

    CELSIUS = 0
    FAHRENHEIT = 1

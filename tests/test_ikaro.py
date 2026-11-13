"""Tests for Comfosplit IKARO HW."""

from __future__ import annotations

import pytest
from modbus_connection.mock import MockModbusUnit, WriteEvent

from idealclima import FanSpeed, IkaroHW, IkaroMode


@pytest.mark.asyncio
async def test_ikaro_update_and_registers(mock_modbus_unit: MockModbusUnit) -> None:
    """Verify IKARO HW reads ambient temperature and holding settings."""
    mock_modbus_unit.load_raw(
        {
            "input": {46801: 235},
            "holding": {
                28301: 1,
                28302: IkaroMode.COOL,
                28303: FanSpeed.MEDIUM,
                28310: 240,
                28311: 210,
            },
        }
    )

    device = IkaroHW(mock_modbus_unit)
    report = await device.async_update()

    assert report.complete
    assert device.readings.ambient_temperature == pytest.approx(23.5)
    assert device.settings.power is True
    assert device.settings.mode is IkaroMode.COOL
    assert device.settings.fan_speed is FanSpeed.MEDIUM
    assert device.settings.target_temp_cool == pytest.approx(24.0)
    assert device.settings.target_temp_heat == pytest.approx(21.0)


@pytest.mark.asyncio
async def test_ikaro_writes_use_fc16_and_stop_fan_on_off(
    mock_modbus_unit: MockModbusUnit,
) -> None:
    """Verify IKARO writes use FC16 and turning off stops the fan by default."""
    events: list[WriteEvent] = []
    mock_modbus_unit.on_write(events.append)

    device = IkaroHW(mock_modbus_unit)
    await device.async_set_mode(IkaroMode.HEAT)
    await device.async_set_fan_speed(FanSpeed.HIGH)
    await device.async_set_target_temp_cool(25.5)
    await device.async_set_target_temp_heat(21.5)
    await device.async_set_power(False)

    assert mock_modbus_unit.holding[28302] == IkaroMode.HEAT
    assert mock_modbus_unit.holding[28310] == 255
    assert mock_modbus_unit.holding[28311] == 215
    assert mock_modbus_unit.holding[28301] == 0
    assert mock_modbus_unit.holding[28303] == FanSpeed.OFF
    assert all(event.function_code == 16 for event in events)


@pytest.mark.asyncio
async def test_ikaro_power_off_without_stopping_fan(
    mock_modbus_unit: MockModbusUnit,
) -> None:
    """Verify stop_fan=False leaves register 28303 untouched."""
    mock_modbus_unit.load_raw({"holding": {28301: 1, 28303: FanSpeed.LOW}})

    device = IkaroHW(mock_modbus_unit)
    await device.async_set_power(False, stop_fan=False)

    assert mock_modbus_unit.holding[28301] == 0
    assert mock_modbus_unit.holding[28303] == FanSpeed.LOW

"""Tests for Radiantore SKUDO DC Inverter."""

from __future__ import annotations

import pytest
from modbus_connection.mock import MockModbusUnit, WriteEvent

from idealclima import FanSpeed, SkudoDCInverter, SkudoMode, TemperatureUnit


@pytest.mark.asyncio
async def test_skudo_update_readings_and_settings(
    mock_modbus_unit: MockModbusUnit,
) -> None:
    """Verify SKUDO DC Inverter reads all input and holding registers."""
    mock_modbus_unit.load_raw(
        {
            "input": {
                46801: 230,
                46802: 385,
                46803: 3,  # intentionally ignored
                46804: 850,
                46805: 1,
                46806: 1,
                46807: 1,  # intentionally ignored
                46808: 0,
                46809: 0,
                46810: 1,
            },
            "holding": {
                28301: 1,
                28302: SkudoMode.AUTO,
                28303: FanSpeed.AUTO,
                28304: 0,
                28305: 1,
                28306: 2,
                28307: 0,
                28308: 300,
                28309: 180,
                28310: 245,
                28311: 205,
                28312: 250,
                28313: 195,
                28314: 250,
                28315: 1,
                28316: 0,
                28317: 1,
                28319: TemperatureUnit.CELSIUS,
                28322: 1,
                28323: 1,
                28324: 0,
                28327: 1,
            },
        }
    )

    device = SkudoDCInverter(mock_modbus_unit)
    report = await device.async_update()

    assert report.complete
    assert device.readings.ambient_temperature == pytest.approx(23.0)
    assert device.readings.coil_temperature == pytest.approx(38.5)
    assert device.readings.fan_rpm == 850
    assert device.readings.valve_command is True
    assert device.readings.power_state is True
    assert device.readings.motor_alarm is False
    assert device.readings.ambient_sensor_alarm is False
    assert device.readings.coil_sensor_alarm is True

    assert device.settings.power is True
    assert device.settings.mode is SkudoMode.AUTO
    assert device.settings.fan_speed is FanSpeed.AUTO
    assert device.settings.key_lock is False
    assert device.settings.sleep is True
    assert device.settings.timer_off_hours == 2
    assert device.settings.timer_on_hours == 0
    assert device.settings.max_target_temp == pytest.approx(30.0)
    assert device.settings.min_target_temp == pytest.approx(18.0)
    assert device.settings.target_temp_cool == pytest.approx(24.5)
    assert device.settings.target_temp_heat == pytest.approx(20.5)
    assert device.settings.target_temp_auto_cool == pytest.approx(25.0)
    assert device.settings.target_temp_auto_heat == pytest.approx(19.5)
    assert device.settings.anti_draft_threshold == pytest.approx(25.0)
    assert device.settings.anti_draft_enabled is True
    assert device.settings.super_silence_enabled is False
    assert device.settings.valve_present is True
    assert device.settings.temperature_unit is TemperatureUnit.CELSIUS
    assert device.settings.key_lock_enabled is True
    assert device.settings.remote_enabled_with_key_lock is True
    assert device.settings.password_enabled is False
    assert device.settings.fan_intermittent is True


@pytest.mark.asyncio
async def test_skudo_writes_use_fc16_and_do_not_stop_fan_by_default(
    mock_modbus_unit: MockModbusUnit,
) -> None:
    """Verify SKUDO writes use FC16 and turning off keeps register 28303."""
    events: list[WriteEvent] = []
    mock_modbus_unit.on_write(events.append)
    mock_modbus_unit.load_raw({"holding": {28301: 1, 28303: FanSpeed.MEDIUM}})

    device = SkudoDCInverter(mock_modbus_unit)
    await device.async_set_power(False)
    await device.async_set_mode(SkudoMode.AUTO)
    await device.async_set_key_lock(True)
    await device.async_set_sleep(True)
    await device.async_set_timer_off_hours(5)
    await device.async_set_timer_on_hours(3)
    await device.async_set_max_target_temp(31.0)
    await device.async_set_min_target_temp(16.0)
    await device.async_set_target_temp_auto_cool(25.5)
    await device.async_set_target_temp_auto_heat(20.0)
    await device.async_set_anti_draft_threshold(26.0)
    await device.async_set_anti_draft_enabled(False)
    await device.async_set_super_silence_enabled(True)
    await device.async_set_valve_present(True)
    await device.async_set_temperature_unit(TemperatureUnit.FAHRENHEIT)
    await device.async_set_key_lock_enabled(True)
    await device.async_set_remote_enabled_with_key_lock(False)
    await device.async_set_password_enabled(True)
    await device.async_set_fan_intermittent(True)

    assert mock_modbus_unit.holding[28301] == 0
    assert mock_modbus_unit.holding[28303] == FanSpeed.MEDIUM
    assert mock_modbus_unit.holding[28302] == SkudoMode.AUTO
    assert mock_modbus_unit.holding[28304] == 1
    assert mock_modbus_unit.holding[28305] == 1
    assert mock_modbus_unit.holding[28306] == 5
    assert mock_modbus_unit.holding[28307] == 3
    assert mock_modbus_unit.holding[28308] == 310
    assert mock_modbus_unit.holding[28309] == 160
    assert mock_modbus_unit.holding[28312] == 255
    assert mock_modbus_unit.holding[28313] == 200
    assert mock_modbus_unit.holding[28314] == 260
    assert mock_modbus_unit.holding[28315] == 0
    assert mock_modbus_unit.holding[28316] == 1
    assert mock_modbus_unit.holding[28317] == 1
    assert mock_modbus_unit.holding[28319] == TemperatureUnit.FAHRENHEIT
    assert mock_modbus_unit.holding[28322] == 1
    assert mock_modbus_unit.holding[28323] == 0
    assert mock_modbus_unit.holding[28324] == 1
    assert mock_modbus_unit.holding[28327] == 1
    assert all(event.function_code == 16 for event in events)


@pytest.mark.asyncio
async def test_skudo_timer_validation(mock_modbus_unit: MockModbusUnit) -> None:
    """Verify SKUDO timer hours reject values outside 0-11."""
    device = SkudoDCInverter(mock_modbus_unit)

    with pytest.raises(ValueError, match="between 0 and 11"):
        await device.async_set_timer_off_hours(12)

    with pytest.raises(ValueError, match="between 0 and 11"):
        await device.async_set_timer_on_hours(-1)

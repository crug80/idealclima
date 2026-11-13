# idealclima

Async Python library for controlling Idealclima Modbus fan coil units ([**Comfosplit IKARO HW**](https://www.idealclima.eu/it/radiantori/terminali-idronici/ikaro) and [**Radiantore SKUDO DC Inverter**](https://www.idealclima.eu/it/radiantori/terminali-idronici/radiantore-skudo-dc-inverter)), built on [`modbus-connection`](https://github.com/home-assistant-libs/modbus-connection) for Home Assistant Core integrations and standalone use.

## Requirements & Notes

- **Modbus Unit Address**: Units ship with default Modbus address `15`, which only allows changing the address. **You must assign a unique address** (`1–32`) to each unit before using this library.
- **Serial Settings**: `9600 bps`, `8N1`.
- **Write Function**: Both models only support Modbus function `0x10` (Write Multiple Registers), which is enforced automatically via `force_fc16=True`.

## Installation

For Home Assistant or when providing your own `ModbusUnit`:

```bash
pip install idealclima
```

For standalone usage with `tmodbus`:

```bash
pip install "idealclima[tmodbus]"
```

## Usage

```python
import asyncio
from modbus_connection import ModbusSerialParams
from modbus_connection.tmodbus import ModbusConnection
from idealclima import FanSpeed, IkaroHW, IkaroMode

async def main() -> None:
    conn = ModbusConnection(
        ModbusSerialParams(device="/dev/ttyUSB0", baudrate=9600)
    )
    async with conn:
        unit = conn.for_unit(20)
        ikaro = IkaroHW(unit)
        await ikaro.async_update()
        print(ikaro.readings.ambient_temperature)
        await ikaro.async_set_mode(IkaroMode.COOL)
        await ikaro.async_set_fan_speed(FanSpeed.LOW)
        await ikaro.async_set_power(True)

asyncio.run(main())
```

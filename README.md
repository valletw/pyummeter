[![CircleCI](https://circleci.com/gh/valletw/pyummeter.svg?style=shield)](https://github.com/valletw/pyummeter)

# Python UM-Meter interface

Support RDTech UM24C, UM25C, UM34C.

## Library usage

Open an UM-Meter interface and request data:

```python
from pyummeter import UMmeter

with UMmeter("/path/to/serial/port") as meter:
    data = meter.get_data()
    print(f"{data['voltage']} V / {data['power']} W")
```

It is also possible to export the data to a CSV file:

```python
from datetime import datetime
from pyummeter import UMmeter
from pyummeter.export_csv import ExportCSV

csv = ExportCSV("/path/to/csv")
with UMmeter("/path/to/serial/port") as meter:
    csv.update(datetime.now(), meter.get_data())
```

List of data available:

- `model`: UM-Meter model name (*exported to CSV*)
- `voltage`: Voltage (V) (*exported to CSV*)
- `intensity`: Intensity (A) (*exported to CSV*)
- `power`: Power (W) (*exported to CSV*)
- `resistance`: Resistance (Ohm) (*exported to CSV*)
- `usb_voltage_dp`: USB Voltage D+ (V) (*exported to CSV*)
- `usb_voltage_dn`: USB Voltage D- (V) (*exported to CSV*)
- `charging_mode`: Charging mode short name (*exported to CSV*)
- `charging_mode_full`: Charging mode full name
- `temperature_celsius`: Temperature (°C) (*exported to CSV*)
- `temperature_fahrenheit`: Temperature (°F)
- `data_group_selected`: Selected data group (index)
- `data_group`: Data for each data group (list) (*exported to CSV, only the selected group*)
  - `capacity`: Capacity (Ah)
  - `energy`: Energy (Wh)
- `record_capacity_threshold`: [Record mode] Capacity threshold (Ah) (*exported to CSV*)
- `record_energy_threshold`: [Record mode] Energy threshold (Wh) (*exported to CSV*)
- `record_intensity_threshold`: [Record mode] Intensity threshold (A) (*exported to CSV*)
- `record_duration`: [Record mode] Duration (seconds) (*exported to CSV*)
- `record_enabled`: [Record mode] Enable status (*exported to CSV*)
- `screen_index`: Screen index
- `screen_timeout`: Screen timeout
- `screen_brightness`: Screen brightness
- `checksum`: Checksum of all data

Meter control managed (not available on all model):

- Screen control:
  - Change (next/previous)
  - Rotate
  - Set timeout (0 to 9 minutes)
  - Set brightness (0 to 5)
- Data group control:
  - Select (0 to 9, next)
  - Clear
- Record threshold (0 to 300 mA)

## Running example

### Bluetooth initialisation

```shell
$ sudo killall rfcomm
$ rfkill block bluetooth
$ rfkill unblock bluetooth
$ sudo bluetoothctl
[bluetooth] power on
[bluetooth] agent on
[bluetooth] scan on
[bluetooth] pair <MAC>
$ sudo rfcomm connect /dev/rfcomm0 <MAC>
```

### Demo application usage

```shell
poetry install
poetry run task demo -t /dev/rfcomm0
```

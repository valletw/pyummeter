[![CircleCI](https://circleci.com/gh/valletw/pyummeter.svg?style=shield)](https://github.com/valletw/pyummeter)

# Python UM-Meter interface

Support RDTech UM24C, UM25C, UM34C.

## Running

### Bluetooth initialisation

```
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

```
$ poetry install --no-dev
$ poetry run task demo -p /dev/rfcomm0
```

""" UM-Meter controller """
#
# Information from "https://sigrok.org/wiki/RDTech_UM_series"
#
from datetime import timedelta
from struct import unpack
from typing import List, Optional, TypedDict
from pyummeter.interface_base import UMmeterInterface


class UMmeterDataGroup(TypedDict):
    """ UM-Meter data group format """
    capacity: float
    energy: float


class UMmeterData(TypedDict):
    """ UM-Meter data format """
    model: str
    voltage: float
    intensity: float
    power: float
    resistance: float
    usb_voltage_dp: float
    usb_voltage_dn: float
    charging_mode: str
    charging_mode_full: str
    temperature_celsius: int
    temperature_fahrenheit: int
    data_group_selected: int
    data_group: List[UMmeterDataGroup]
    record_capacity_threshold: float
    record_energy_threshold: float
    record_intensity_threshold: float
    record_duration: timedelta
    record_enabled: bool
    screen_index: int
    screen_timeout: timedelta
    screen_brightness: int
    checksum: int


class UMmeter():
    """ UM-Meter instance """
    _MODEL = {
        0x0963: "UM24C",
        0x09c9: "UM25C",
        0x0d4c: "UM34C"
    }
    _CHARGING_MODE = {
        0: ("Unknown", "Unknown"),
        1: ("QC2", "Qualcomm Quick Charge 2.0"),
        2: ("QC3", "Qualcomm Quick Charge 3.0"),
        3: ("APP2.4A", "Apple (max. 2.4 A)"),
        4: ("APP2.1A", "Apple (max. 2.1 A)"),
        5: ("APP1.0A", "Apple (max. 1.0 A)"),
        6: ("APP0.5A", "Apple (max. 0.5 A)"),
        7: ("DCP1.5A", "Dedicated Charging Port (max. 1.5 A)"),
        8: ("Samsung", "Samsung")
    }

    def __init__(self, com: UMmeterInterface):
        self._com: UMmeterInterface = com

    def __str__(self):
        return f"<UM-Meter: com={self._com}>"

    def __enter__(self):
        self.open()
        return self

    def __exit__(self, _1, _2, _3):
        self.close()

    def is_open(self):
        """ Check if connection is opened """
        return self._com.is_open()

    def open(self):
        """ Open connection """
        self._com.open()

    def close(self):
        """ Close connection """
        self._com.close()

    def set_timeout(self, timeout_s: int):
        """ Configure receive timeout in seconds """
        if self.is_open():
            self._com.set_timeout(timedelta(seconds=timeout_s))

    def get_data(self) -> Optional[UMmeterData]:
        """ Request new data dump

            Supported on: UM24C/UM25C/UM34C.
        """
        # Send and wait to received data dump.
        self._com.send(bytearray([0xf0]))
        raw = self._com.receive(130)
        if len(raw) == 130:
            # Extract information.
            (
                mod, volt, amp, watt, temp_c, temp_f, dg_cur, dg, udp, udn,
                cmode, rt_mah, rt_wh, rt_ma, rt_dur, rt_en, sc_time, sc_light,
                ohm, sc_cur, _1, crc
            ) = unpack(">HHHLHHH80sHHHLLHLHHHLHBB", raw)
            # Get model for conversion.
            model = UMmeter._get_model_name(mod)
            # Parse data group.
            data_group: List[UMmeterDataGroup] = []
            for dg_n in [dg[i:i + 8] for i in range(0, len(dg), 8)]:
                dg_cap, dg_wh = unpack(">LL", dg_n)
                data_group.append({
                    "capacity": UMmeter._convert_data_group_capacity(model, dg_cap),
                    "energy": UMmeter._convert_data_group_energy(model, dg_wh)
                })
            # Format information.
            data: UMmeterData = {
                "model": model,
                "voltage": UMmeter._convert_voltage(model, volt),
                "intensity": UMmeter._convert_intensity(model, amp),
                "power": UMmeter._convert_power(model, watt),
                "resistance": UMmeter._convert_resistance(model, ohm),
                "temperature_celsius": temp_c,
                "temperature_fahrenheit": temp_f,
                "data_group_selected": dg_cur,
                "data_group": data_group,
                "usb_voltage_dp": UMmeter._convert_usb_voltage(model, udp),
                "usb_voltage_dn": UMmeter._convert_usb_voltage(model, udn),
                "charging_mode": UMmeter._get_charging_mode_name(cmode),
                "charging_mode_full": UMmeter._get_charging_mode_full_name(cmode),
                "record_capacity_threshold":
                    UMmeter._convert_record_threshold_capacity(model, rt_mah),
                "record_energy_threshold":
                    UMmeter._convert_record_threshold_energy(model, rt_wh),
                "record_intensity_threshold":
                    UMmeter._convert_record_threshold_intensity(model, rt_ma),
                "record_duration": timedelta(seconds=rt_dur),
                "record_enabled": bool(rt_en == 1),
                "screen_timeout": timedelta(minutes=sc_time),
                "screen_brightness": sc_light,
                "screen_index": sc_cur,
                "checksum": crc
            }
            return data
        return None

    def screen_next(self):
        """ Go to next screen

            Supported on: UM24C/UM25C/UM34C.
        """
        self._com.send(bytearray([0xf1]))

    def screen_previous(self):
        """ Go to previous screen

            Supported on: UM25C/UM34C.
        """
        self._com.send(bytearray([0xf3]))

    def screen_rotate(self):
        """ Rotate screen

            Supported on: UM24C/UM25C/UM34C.
        """
        self._com.send(bytearray([0xf2]))

    def screen_timeout(self, minutes: int):
        """ Set screen timeout in minutes (0-9)

            Supported on: UM24C/UM25C/UM34C.
        """
        if minutes < 0 or 9 < minutes:
            raise ValueError("UM-Meter: timeout invalid range")
        self._com.send(bytearray([0xe0 + minutes]))

    def screen_brightness(self, brightness: int):
        """ Set screen brightness (0: dim, 5: full)

            Supported on: UM24C/UM25C/UM34C.
        """
        if brightness < 0 or 5 < brightness:
            raise ValueError("UM-Meter: brightness invalid range")
        self._com.send(bytearray([0xd0 + brightness]))

    def data_threshold(self, threshold_ma: int):
        """ Set recording threshold in mA (0-300)

            Supported on: UM24C/UM25C/UM34C.
        """
        if threshold_ma < 0 or 300 < threshold_ma:
            raise ValueError("UM-Meter: threshold invalid range")
        self._com.send(bytearray([0xb0 + int(round(threshold_ma / 10))]))

    def data_group_set(self, group: int):
        """ Set the selected data group (0-9)

            Supported on: UM25C/UM34C.
        """
        if group < 0 or 9 < group:
            raise ValueError("UM-Meter: group invalid range")
        self._com.send(bytearray([0xa0 + group]))

    def data_group_next(self):
        """ Switch to next data group

            Supported on: UM24C.
        """
        self._com.send(bytearray([0xf3]))

    def data_group_clear(self):
        """ Clear data group

            Supported on: UM24C/UM25C/UM34C.
        """
        self._com.send(bytearray([0xf4]))

    @staticmethod
    def _get_model_name(value: int) -> str:
        """ Get model name """
        if value in UMmeter._MODEL:
            return UMmeter._MODEL[value]
        return "Unknown"

    @staticmethod
    def _get_charging_mode_name(value: int) -> str:
        """ Get charging mode name """
        if value in UMmeter._CHARGING_MODE:
            return UMmeter._CHARGING_MODE[value][0]
        return "Unknown"

    @staticmethod
    def _get_charging_mode_full_name(value: int) -> str:
        """ Get charging mode name """
        if value in UMmeter._CHARGING_MODE:
            return UMmeter._CHARGING_MODE[value][1]
        return "Unknown"

    @staticmethod
    def _convert_voltage(model: str, value: int) -> float:
        """ Apply voltage conversion by model type """
        if model in ["UM25C"]:
            return value / 1000
        if model in ["UM24C", "UM34C"]:
            return value / 100
        return 0

    @staticmethod
    def _convert_usb_voltage(model: str, value: int) -> float:
        """ Apply USB voltage conversion by model type """
        if model in ["UM25C", "UM24C", "UM34C"]:
            return value / 100
        return 0

    @staticmethod
    def _convert_intensity(model: str, value: int) -> float:
        """ Apply intensity conversion by model type """
        if model in ["UM25C"]:
            return value / 10000
        if model in ["UM24C", "UM34C"]:
            return value / 1000
        return 0

    @staticmethod
    def _convert_power(model: str, value: int) -> float:
        """ Apply power conversion by model type """
        if model in ["UM25C", "UM24C", "UM34C"]:
            return value / 1000
        return 0

    @staticmethod
    def _convert_resistance(model: str, value: int) -> float:
        """ Apply resistance conversion by model type """
        if model in ["UM25C", "UM24C", "UM34C"]:
            return value / 10
        return 0

    @staticmethod
    def _convert_record_threshold_intensity(model: str, value: int) -> float:
        """ Apply data group intensity conversion by model type """
        if model in ["UM25C", "UM24C", "UM34C"]:
            return value / 100
        return 0

    @staticmethod
    def _convert_record_threshold_capacity(model: str, value: int) -> float:
        """ Apply data group capacity conversion by model type """
        if model in ["UM25C", "UM24C", "UM34C"]:
            return value / 1000
        return 0

    @staticmethod
    def _convert_record_threshold_energy(model: str, value: int) -> float:
        """ Apply data group energy conversion by model type """
        if model in ["UM25C", "UM24C", "UM34C"]:
            return value / 1000
        return 0

    @staticmethod
    def _convert_data_group_capacity(model: str, value: int) -> float:
        """ Apply data group capacity conversion by model type """
        if model in ["UM25C", "UM24C", "UM34C"]:
            return value / 1000
        return 0

    @staticmethod
    def _convert_data_group_energy(model: str, value: int) -> float:
        """ Apply data group energy conversion by model type """
        if model in ["UM25C", "UM24C", "UM34C"]:
            return value / 1000
        return 0

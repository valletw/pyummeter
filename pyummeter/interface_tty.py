""" UM-Meter interface TTY """
from datetime import timedelta
from typing import Optional
from pyummeter.interface_base import UMmeterInterface
import serial


class UMmeterInterfaceTTY(UMmeterInterface):
    _BAUD = 9600
    _MODE = "8N1"

    def __init__(self, path: str):
        assert path is not None
        assert len(path) != 0
        self._tty = path
        self._config = {
            "baudrate": self._BAUD,
            "bytesize": int(self._MODE[0]),
            "parity": self._MODE[1],
            "stopbits": int(self._MODE[2])
        }
        # Do not open serial interface on init.
        self._com: Optional[serial.Serial] = None
        self._is_open = False

    def __str__(self):
        return f"<TTY: path={self._tty} open={self.is_open()}>"

    def is_open(self) -> bool:
        """ Check if interface is open """
        return self._is_open

    def open(self):
        """ Open interface """
        if not self.is_open():
            try:
                if self._com is None:
                    # No instance, create it and open interface.
                    self._com = serial.Serial(self._tty, **self._config)
                else:
                    # Instance already created, just open it.
                    self._com.open()
                self._is_open = True
            except Exception as exp:
                raise IOError("UM-Meter: could not open TTY interface") from exp

    def close(self):
        """ Close interface """
        if self.is_open() and self._com is not None:
            self._com.close()
            self._is_open = False

    def set_timeout(self, timeout: timedelta):
        """ Configure receive timeout """
        if self._com is None:
            raise IOError("UM-Meter: TTY interface is not opened")
        self._com.timeout = int(timeout.total_seconds())

    def send(self, data: bytearray) -> int:
        """ Send raw data to interface, return number of bytes sent """
        if not self.is_open() or self._com is None:
            raise IOError("UM-Meter: TTY interface is not opened")
        return self._com.write(data)

    def receive(self, nb: int) -> bytearray:
        """ Receive 'nb' bytes of raw data from interface, return bytes received """
        if not self.is_open() or self._com is None:
            raise IOError("UM-Meter: TTY interface is not opened")
        return self._com.read(nb)

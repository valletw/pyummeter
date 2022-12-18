""" UM-Meter interface base """
from abc import ABC, abstractmethod
from datetime import timedelta


class UMmeterInterface(ABC):
    def __str__(self):
        return "<UM-Meter interface base>"

    @abstractmethod
    def is_open(self) -> bool:
        """ Check if interface is open """
        raise NotImplementedError

    @abstractmethod
    def open(self):
        """ Open interface """
        raise NotImplementedError

    @abstractmethod
    def close(self):
        """ Close interface """
        raise NotImplementedError

    @abstractmethod
    def set_timeout(self, timeout: timedelta):
        """ Configure receive timeout """
        raise NotImplementedError

    @abstractmethod
    def send(self, data: bytearray) -> int:
        """ Send raw data to interface, return number of bytes sent """
        raise NotImplementedError

    @abstractmethod
    def receive(self, nb: int) -> bytearray:
        """ Receive 'nb' bytes of raw data from interface, return bytes received """
        raise NotImplementedError

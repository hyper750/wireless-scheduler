from abc import ABC, abstractmethod

from wireless_scheduler.devices.wifi_status import WifiStatus


class AbstractDevice(ABC):

    @abstractmethod
    def login(self, user: str, password: str):
        """Login to router page

        :param user: user to login with
        :type user: str
        :param password: password of the user
        :type password: str
        """
        pass

    @abstractmethod
    def get_wifi_status(self) -> WifiStatus:
        """Wifi status, including ssid, channel, wifi enabled...

        :return: info of the wifi
        :rtype: WifiStatus
        """
        pass

    @abstractmethod
    def wifi_turn_on(self):
        """Turn on the wifi"""
        pass

    @abstractmethod
    def wifi_turn_off(self):
        """Turn off the wifi"""
        pass

from abc import abstractmethod

import requests

from .abstract_device import AbstractDevice


class AbstractHttpDevice(AbstractDevice):

    def __init__(self, host: str):
        self.host = host
        self.session = requests.Session()

    @abstractmethod
    def is_bad_login(self, response: requests.models.Response) -> bool:
        """Check if the login went ok or not

        :param response: response of the login request
        :type response: requests.models.Response
        :return: the login failed
        :rtype: bool
        """
        pass

    def get_host(self) -> str:
        """Get http host

        :return: host to make the http requests
        :rtype: str
        """
        return self.host

    def get_session(self) -> requests.Session:
        """Return current session

        :return: session to work with
        :rtype: requests.Session
        """
        return self.session

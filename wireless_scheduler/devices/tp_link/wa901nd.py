import base64
import hashlib
import http
import re

from requests.models import Response
from wireless_scheduler.devices.abstract_http_device import AbstractHttpDevice
from wireless_scheduler.devices.exceptions import LoginFailed
from wireless_scheduler.devices.wifi_status import WifiStatus


class DeviceWA901ND(AbstractHttpDevice):

    LOGIN_URL = 'http://{host}/userRpm/LoginRpm.htm'
    WIFI_URL = 'http://{host}/{session_id}/userRpm/WlanNetworkRpm.htm'

    def __init__(self, host: str):
        super().__init__(host)
        self.session_id = None

    def format_auth(self, user: str, password: str) -> str:
        """Format auth to make requests to that host

        :param user: user to access with
        :type user: str
        :param password: password for that user
        :type password: str
        :return: formatted user and password
        :rtype: str
        """
        # Encode user and password as encrypt.js is doing
        # Encode password to md5 hash
        encoded_password = hashlib.md5(password.encode('utf-8')).hexdigest()
        # Encode base64 user and password
        encoded_auth = base64.b64encode(
            '{user}:{password}'.format(
                user=user,
                password=encoded_password
            ).encode('utf-8')
        ).decode('utf-8')
        return 'Basic {}'.format(encoded_auth)

    def is_bad_login(self, response: Response) -> bool:
        """Check if the login went ok or not

        :param response: response of the login request
        :type response: Response
        :return: the login failed
        :rtype: bool
        """
        # HTTP status is ok, 200, but the error is reflected inside the html
        html_bad_request = 'username or password is incorrect' in response.text.lower()
        return response.status_code != http.HTTPStatus.OK or html_bad_request

    def parse_session_id(self, html_response: str) -> str:
        """Get session id from response

        :param html_response: html response
        :type html_response: str
        :return: session id
        :rtype: str
        """
        # '<body><script language="javaScript">window.parent.location.href = "http://192.168.1.2/HLTBQVGBHHZTWXBB/userRpm/Index.htm";\n</script></body></html>\n'
        session_id_regex = re.compile(
            'http://{host}/(.+)/userRpm/Index\.htm'.format(
                host=self.get_host()
            )
        )
        return session_id_regex.search(html_response).group(1)

    def login(self, user: str, password: str):
        """Login to router page

        :param user: user to login with
        :type user: str
        :param password: password of the user
        :type password: str
        """
        # Set cookies for the next requests
        # Cookie: Authorization=Basic%20YXNkOjc4MTU2OTZlY2JmMWM5NmU2ODk0Yjc3OTQ1NmQzMzBl
        self.get_session().cookies.set(
            'Authorization', self.format_auth(user, password)
        )

        response = self.get_session().get(
            # Login url with the formatted host
            self.LOGIN_URL.format(host=self.get_host()),

            # GET parameters
            params=dict(
                Save='Save'
            )
        )

        if self.is_bad_login(response):
            raise LoginFailed(
                "Login requests failed, make sure the user/password is correct"
            )

        self.session_id = self.parse_session_id(response.text)

    def get_wifi_status(self) -> WifiStatus:
        """Wifi status, including ssid, channel, wifi enabled...

        :return: info of the wifi
        :rtype: WifiStatus
        """
        response = self.get_session().get(
            self.WIFI_URL.format(
                host=self.get_host(),
                session_id=self.session_id
            )
        )
        # TODO: Throws unauthorized
        # '<hr><h1><B>You have no authority to access this router!</B></h1><hr>'
        import pdb
        pdb.set_trace()

        # TODO: Check bad request

        return response

    def wifi_turn_on(self):
        """Turn on the wifi"""
        # TODO: To implement
        pass

    def wifi_turn_off(self):
        """Turn off the wifi"""
        # TODO: To implement
        pass

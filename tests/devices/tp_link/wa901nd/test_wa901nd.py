import http
import os
import unittest
from unittest.mock import MagicMock, patch

from wireless_scheduler.devices.exceptions import LoginFailed
from wireless_scheduler.devices.tp_link.wa901nd import DeviceWA901ND


class TestWA901ND(unittest.TestCase):

    HOST = '192.168.1.2'
    PATH = 'tests/devices/tp_link/wa901nd'
    BAD_LOGIN_REQUEST_HTML = os.path.join(
        PATH,
        "bad_request.html"
    )

    def setUp(self) -> None:
        self.device = DeviceWA901ND(self.HOST)

    def test_format_auth(self):
        self.assertEqual(
            'Basic YXNkOjc4MTU2OTZlY2JmMWM5NmU2ODk0Yjc3OTQ1NmQzMzBl',
            self.device.format_auth('asd', 'asd')
        )

    def test_is_bad_login(self):
        # Bad request from html
        with open(self.BAD_LOGIN_REQUEST_HTML, "r") as f:
            bad_request_html = MagicMock(
                text=f.read(),
                status_code=http.HTTPStatus.OK
            )
            self.assertEqual(
                self.device.is_bad_login(bad_request_html),
                True
            )

        # Bad request html status code
        empty_response = MagicMock(
            text="",
            status_code=http.HTTPStatus.BAD_REQUEST
        )
        self.assertEqual(
            self.device.is_bad_login(empty_response),
            True
        )

        # Ok request
        ok_request_html = MagicMock(
            text="",
            status_code=http.HTTPStatus.OK
        )
        self.assertEqual(
            self.device.is_bad_login(ok_request_html),
            False
        )

    def test_login(self):
        device = DeviceWA901ND(self.HOST)

        # Bad credentials
        with open(self.BAD_LOGIN_REQUEST_HTML, "r") as f:
            function_response = MagicMock(
                text=f.read(), status_code=http.HTTPStatus.OK)
            ok_request_mock = MagicMock(return_value=function_response)
            with patch('requests.Session.get', ok_request_mock):
                with self.assertRaises(LoginFailed):
                    device.login('bad_login', 'bad_login')

        # Good credentials
        html = '<body><script language="javaScript">window.parent.location.href = "http://192.168.1.2/HLTBQVGBHHZTWXBB/userRpm/Index.htm";\n</script></body></html>\n'
        function_response = MagicMock(
            text=html, status_code=http.HTTPStatus.OK)
        ok_request_mock = MagicMock(return_value=function_response)
        with patch('requests.Session.get', ok_request_mock):
            device.login('ok_login', 'ok_login')
            self.assertEqual(
                'HLTBQVGBHHZTWXBB',
                device.session_id
            )

    def test_parse_session_id(self):
        html = '<body><script language="javaScript">window.parent.location.href = "http://192.168.1.2/HLTBQVGBHHZTWXBB/userRpm/Index.htm";\n</script></body></html>\n'
        self.assertEqual(
            'HLTBQVGBHHZTWXBB',
            self.device.parse_session_id(html)
        )

        html = '<body><script language="javaScript">window.parent.location.href = "http://192.168.1.2/EPPCWNRARCPORNRC/userRpm/Index.htm";\n</script></body></html>\n'
        self.assertEqual(
            'EPPCWNRARCPORNRC',
            self.device.parse_session_id(html)
        )

        html = '<body><script language="javaScript">window.parent.location.href = "http://192.168.1.2/userRpm/Index.htm";\n</script></body></html>\n'
        with self.assertRaises(AttributeError):
            self.device.parse_session_id(html)

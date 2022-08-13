from dataclasses import dataclass


@dataclass
class WifiStatus:
    enabled: bool
    ssid: str
    channel: int

"""
    API Methods for radio-browser
"""
import socket
from typing import List


def get_ip_for_radio_browser() -> List[str]:
    """
        Gives all the important addresses of radio browser.
        (Documentation recommends calling the API via IP)
    """
    return [
        info[4][0]
        for info in
        socket.getaddrinfo("api.radio-browser.info")
        ]

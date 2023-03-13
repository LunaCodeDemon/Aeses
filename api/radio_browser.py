"""
    API Methods for radio-browser
"""
import socket
from typing import List, NamedTuple
import httpx


class RadioEntry(NamedTuple):
    """
        Commonly used data that a station has.
    """
    stationuuid: str
    name: str
    url: str
    url_resolved: str
    homepage: str
    tags: str
    language: str
    languagecodes: str
    votes: int


def get_ip_for_radio_browser() -> List[str]:
    """
        Gives all the important addresses of radio browser.
        (Documentation recommends calling the API via IP)
    """
    return [
        info[4][0] for info in socket.getaddrinfo("all.api.radio-browser.info")
    ]


def search_radio(name: str) -> List[RadioEntry]:
    """
        Search a radio with a partial name.
    """
    # TODO: use ip instead of general domain.
    #api_ip = choice(get_ip_for_radio_browser())
    #print(api_ip)
    result = httpx.get(
        "http://all.api.radio-browser.info/json/stations/search",
        params={
            "name": name,
            "limit": 10,
            "offset": 0
        })

    if result.status_code != 200:
        return []

    return [
        RadioEntry(stationuuid=raw_entry["stationuuid"],
                   name=raw_entry["name"],
                   url=raw_entry["url"],
                   url_resolved=raw_entry["url_resolved"],
                   homepage=raw_entry["homepage"],
                   tags=raw_entry["tags"],
                   language=raw_entry["language"],
                   languagecodes=raw_entry["languagecodes"],
                   votes=raw_entry["votes"]) for raw_entry in result.json()
    ]

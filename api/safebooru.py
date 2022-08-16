"This module interfaces with safebooru.org"
from typing import Tuple, NamedTuple
import xml.etree.ElementTree as ET
from functools import lru_cache
from random import randint
import httpx


class SafebooruConnectionError(Exception):
    "Couldn't connect to safebooru."


class SafebooruNothingFound(Exception):
    "Couldn't find anything for given tags."
    tags: Tuple[str]

    def __init__(self, tags: Tuple[str]) -> None:
        "set the tags"
        super().__init__(self.__doc__)
        self.tags = tags


SAFEBOORU_DEFAULTS = {'page': "dapi", 'q': "index"}
SAFEBOORU_BASEURL = "https://safebooru.org/index.php"


class SafebooruPost(NamedTuple):
    "Dataclass for safebooru.org posts (only contains necessary data)"
    post_id: int
    file_url: str
    post_url: str
    has_comments: bool


@lru_cache(maxsize=3)
def count(tags: Tuple[str] = None) -> int:
    "Gets the amount of entries for the search"
    result = httpx.get(SAFEBOORU_BASEURL,
                       params={**SAFEBOORU_DEFAULTS, 'limit': 0, 'tags': tags, 's': "post"})
    if result.status_code != 200:
        raise SafebooruConnectionError
    # read retrieved data
    tree = ET.fromstring(result.text)
    return int(tree.attrib['count'])


async def random_post(tags: Tuple[str] = None) -> SafebooruPost:
    "Get a random post from booru"
    available = count(tags)-1
    if available < 0:
        raise SafebooruNothingFound(tags=tags)
    rng = randint(0, available)
    result = httpx.get(SAFEBOORU_BASEURL,
        params={**SAFEBOORU_DEFAULTS, 'limit': 1, 'tags': tags, 's': "post", 'pid': rng})
    if result.status_code != 200:
        raise SafebooruConnectionError
    # read retrived data
    tree = ET.fromstring(result.text)
    post_data = tree[0].attrib
    return SafebooruPost(
        post_id=int(post_data['id']),
        file_url=post_data['file_url'],
        post_url=f"https://safebooru.org/index.php?page=post&s=view&id={post_data['id']}",
        has_comments=post_data['has_comments']
    )

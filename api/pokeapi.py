"This module interfaces with pokeapi"
from random import choice
import httpx
from discord import Embed

POKEAPI_BASEURL = "https://pokeapi.co/api/v2"


def get_full_pokemon_list():
    "Get the entire list of pokemon that exist."
    return httpx.get(f"{POKEAPI_BASEURL}/pokemon?limit=100000&offset=0").json()


def get_pokemon(search_tag: str):
    "Get a pokemon from pokeapi."
    return httpx.get(f"{POKEAPI_BASEURL}/pokemon/{search_tag}").json()


def get_random_pokemon():
    "Get a random pokemon from pokeapi"
    name = choice(get_full_pokemon_list()['results'])['name']
    return get_pokemon(name)


def seek_optimial_front_sprite(data) -> str:
    "Seek for default front sprites for a pokemon."
    other = data['sprites']['other']
    img_link = data['sprites']['front_default']
    sprite_list = [other[v]
                   for v in other if v in ["home", "official-artwork"]]

    # seek if better one exists.
    for sprite in sprite_list:
        if sprite['front_default']:
            img_link = sprite['front_default']
            break
    return img_link


def gen_pokemon_embed(data) -> Embed:
    "Generate an embed for given pokemon."
    if not data:
        raise ValueError

    img_link = seek_optimial_front_sprite(data)
    ptypes = [t['type']['name'] for t in data['types']]

    embed = Embed()
    embed.title = data['name']
    embed.add_field(name="Types", value=','.join(ptypes))
    embed.set_image(url=img_link)
    return embed

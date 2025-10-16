"This module interfaces with pokeapi"
from random import choice
import httpx
import hikari

POKEAPI_BASEURL = "https://pokeapi.co/api/v2"


def get_full_pokemon_list():
    "Get the entire list of pokemon that exist."
    return httpx.get(f"{POKEAPI_BASEURL}/pokemon?limit=100000&offset=0").json()


def get_pokemon(search_tag: str):
    "Get a pokemon from pokeapi."
    return httpx.get(f"{POKEAPI_BASEURL}/pokemon/{search_tag}").json()


def get_random_pokemon():
    "Get a random pokemon from pokeapi"
    name = choice(get_full_pokemon_list()["results"])["name"]
    return get_pokemon(name)


def create_pokemon_embed(pokemon_data: dict) -> hikari.Embed | None:
    """Generates an embed from Pokémon data."""
    if not pokemon_data or "name" not in pokemon_data:
        return None

    name = pokemon_data.get("name", "Unknown").capitalize()
    poke_id = pokemon_data.get("id", "N/A")

    embed = hikari.Embed(title=name, description=f"ID: {poke_id}")

    if sprites := pokemon_data.get("sprites"):
        if front_default := sprites.get("front_default"):
            embed.set_thumbnail(front_default)

    if types_data := pokemon_data.get("types"):
        types = ", ".join([t["type"]["name"] for t in types_data])
        embed.add_field("Types", types, inline=True)

    if stats_data := pokemon_data.get("stats"):
        for stat in stats_data:
            stat_name = stat["stat"]["name"].replace("-", " ").capitalize()
            embed.add_field(stat_name, str(stat["base_stat"]), inline=True)

    return embed

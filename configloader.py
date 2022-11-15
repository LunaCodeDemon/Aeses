"This module is there to load .ini files"
import yaml

# pylint: disable=consider-using-with
config = yaml.full_load(open("dialogs.yml", encoding="utf-8"))

# pylint: disable=consider-using-with
emote_links = yaml.full_load(open("emote-links.yml", encoding="utf-8"))

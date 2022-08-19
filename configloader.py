"This module is there to load .ini files"
import yaml

# pylint: disable=consider-using-with
config = yaml.full_load(open("config.yml", encoding="utf-8"))

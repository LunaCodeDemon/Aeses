"This module is there to load .ini files"
import configparser

config = configparser.ConfigParser()

config.read("dialogs.ini")

#!/usr/bin/env python
# -*- coding: utf-8 -*-

from http.client import HTTPException
import discord
from textfilter import check_message

client = discord.Client()

@client.event
async def on_ready():
    "This event will be triggered when the client is ready to use."
    print(f"Discord client logged in as {client}")

@client.event
async def on_message(message: discord.Message):
    "This will be triggered whenever a user sends a message."
    if message.author == client.user:
        return

    # filter
    if check_message(message):
        try:
            message.delete()
        except discord.Forbidden:
            print("Couldn't delete filtered message, missing permissions.")
        except discord.NotFound:
            print("Couldn't find filtered message, is there another filter bot?")
        except HTTPException:
            print("Deletion of filtered message failed due to API Error")

@client.event
async def on_message_edit(old: discord.Message, updated: discord.Message):
    "This will be triggered whenever a user edits a message."
    if updated.author == client.user:
        return

    # filter
    if check_message(updated):
        try:
            updated.delete()
        except discord.Forbidden:
            print("Couldn't delete filtered message, missing permissions.")
        except discord.NotFound:
            print("Couldn't find filtered message, is there another filter bot?")
        except HTTPException:
            print("Deletion of filtered message failed due to API Error")

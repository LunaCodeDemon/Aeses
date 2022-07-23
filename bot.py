#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
from http.client import HTTPException
import discord
from discord.ext import commands
from textfilter import check_message

client = commands.Bot(command_prefix="!")

@client.event
async def on_ready():
    "This event will be triggered when the client is ready to use."
    print(f"Discord client logged in as {client.user.name}")

@client.event
async def on_message(message: discord.Message):
    "This will be triggered whenever a user sends a message."
    if message.author == client.user:
        return

    # filter
    if check_message(message):
        try:
            message.delete()
        except (discord.Forbidden, discord.NotFound, HTTPException):
            logging.exception("Deletion of filtered message failed.")
        
        return

    await client.process_commands(message)

@client.event
async def on_message_edit(old: discord.Message, updated: discord.Message):
    "This will be triggered whenever a user edits a message."
    if updated.author == client.user:
        return

    # filter
    if check_message(updated):
        try:
            updated.delete()
        except (discord.Forbidden, discord.NotFound, HTTPException):
            logging.exception("Deletion of filtered message failed.")

EXTENSION_FOLDER = 'cogs'
for file in os.listdir(EXTENSION_FOLDER):
    if file.endswith('.py'):
        module_path = f"{EXTENSION_FOLDER}.{os.path.splitext(file)[0]}"
        client.load_extension(module_path)

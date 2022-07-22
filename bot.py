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


@client.command()
async def test(ctx: commands.Context):
    "sends hello world back"
    await ctx.send("Hello World")

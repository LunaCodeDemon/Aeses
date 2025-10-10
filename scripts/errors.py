"""A collections of functions that reply to errors."""
import logging
import httpx
import tanjun
from api import safebooru
from configloader import config

def read_timeout(_: tanjun.abc.Context, error: httpx.ReadTimeout):
    """This gets triggered if the bot gets a read timeout."""
    logging.warning("Bot got a timeout from %s", error.request.url)

def safebooru_connection_error(ctx: tanjun.abc.Context, _: safebooru.SafebooruConnectionError):
    """This is triggered when the connection to safebooru fails."""
    message = config['exceptions']['safebooru_connection_error']
    if ctx.has_responded:
        return ctx.edit_initial_response(message)
    return ctx.respond(message)

def safebooru_nothing_found(ctx: tanjun.abc.Context, error: safebooru.SafebooruNothingFound):
    """This is triggerd if nothing is found on safebooru query."""
    tags_str = ', '.join(list(error.tags))
    message = config['exceptions']['safebooru_nothing_found'].format(tags=tags_str)
    if ctx.has_responded:
        return ctx.edit_initial_response(message)
    return ctx.respond(message)

# This dictionary is now much smaller as most errors are handled by Tanjun's built-in hooks and checks.
error_dictionary = {
    safebooru.SafebooruConnectionError: safebooru_connection_error,
    safebooru.SafebooruNothingFound: safebooru_nothing_found,
}
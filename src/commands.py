from typing import List

import discord

import src.config as cfg
from .classes import Message
from .client import client
from .log import logger
from .utils import find_item, gen_command_find_guild_channel

commands_map = {}


def command(*, name: str, aliases=[]):
    def decorator(func):
        def wrapper(*args, **kwargs):
            if not client.is_ready():
                logger.warning('error: client not ready')
                return
            try:
                return func(*args, **kwargs)
            except Exception as e:
                logger.exception(e)
        wrapper.__name__ = func.__name__
        for s in [name] + aliases:
            if commands_map.get(s) is not None:
                logger.warning(
                    f'warning: command {s} ({wrapper.__name__}) already exists')
            commands_map[s] = wrapper
        return wrapper
    return decorator


@command(name='listen', aliases=['l'])
def listen_command(message: Message):
    cmd_args = message.parts[1:]
    if not cmd_args:
        guild = client.get_guild(cfg.current_guild_id)
        guild = guild.name if guild else ""
        channel = client.get_channel(cfg.current_channel_id)
        channel = f'#{channel.name}' if channel else ""
        logger.info(f'info: listening to: {guild}{channel}')
        return

    def gc(guild, channel):
        cfg.current_guild_id = guild.id
        cfg.current_channel_id = channel.id
        logger.info(f'info: now listening to: {guild.name}#{channel.name}')

    def g(guild):
        cfg.current_guild_id = guild.id
        cfg.current_channel_id = None
        logger.info(f'info: now listening to: {guild.name}')

    def c(channel):
        cfg.current_guild_id = channel.guild.id
        cfg.current_channel_id = channel.id
        logger.info(
            f'info: now listening to: {channel.guild.name}#{channel.name}')
    gen_command_find_guild_channel(cmd_args, gc=gc, g=g, c=c)


@command(name='all', aliases=['a', 'lall'])
def all_command(message: Message):
    cfg.current_guild_id = None
    cfg.current_channel_id = None
    logger.info(f'info: now listening to: all')

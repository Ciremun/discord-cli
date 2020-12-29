import re
from typing import List

import discord

import src.config as cfg
from .classes import Message
from .client import client
from .log import logger
from .utils import find_item

commands_map = {}
listen_re = re.compile(r'^([^#]{1,100})?#?([\w-]{1,100})?$')


def command(*, name: str, aliases=[]):
    def decorator(func):
        def wrapper(*args, **kwargs):
            if not client.is_ready():
                logger.error('error: client not ready')
                return
            try:
                return func(*args, **kwargs)
            except Exception as e:
                logger.exception(e)
        wrapper.__name__ = func.__name__
        for s in [name] + aliases:
            if commands_map.get(s) is not None:
                logger.warning(f'warning: command {s} ({wrapper.__name__}) already exists')
            commands_map[s] = wrapper
        return wrapper
    return decorator


@command(name='listen', aliases=['l'])
def listen_command(message: Message):
    args = message.parts[1:]
    if not args:
        guild = client.get_guild(cfg.current_guild_id)
        guild = guild.name if guild else ""
        channel = client.get_channel(cfg.current_channel_id)
        channel = f'#{channel.name}' if channel else ""
        logger.info(f'info: listening to: {guild}{channel}')
        return
    args = ' '.join(args)
    if args := re.match(listen_re, args):
        guild_name, channel_name = args.groups()
        if guild_name and channel_name:
            if guild := find_item(guild_name.lower(), client.guilds):
                if channel := find_item(channel_name, guild.channels):
                    cfg.current_guild_id = guild.id
                    cfg.current_channel_id = channel.id
                    logger.info(
                        f'info: now listening to: {guild.name}#{channel.name}')
                else:
                    logger.info(f'error: channel {channel_name} not found')
            else:
                logger.info(f'error: guild {guild_name} not found')
        elif guild_name and not channel_name:
            if guild := find_item(guild_name.lower(), client.guilds):
                cfg.current_guild_id = guild.id
                cfg.current_channel_id = None
                logger.info(f'info: now listening to: {guild.name}')
            else:
                logger.info(f'error: guild {guild_name} not found')
        elif not guild_name and channel_name:
            if channel := find_item(channel_name, [c for g in client.guilds for c in g.channels]):
                cfg.current_guild_id = channel.guild.id
                cfg.current_channel_id = channel.id
                logger.info(
                    f'info: now listening to: {channel.guild.name}#{channel.name}')
            else:
                logger.info(f'error: channel {channel_name} not found')
    else:
        logger.info('error: invalid guild/channel')


@command(name='all', aliases=['a', 'lall'])
def all_command(message: Message):
    cfg.current_guild_id = None
    cfg.current_channel_id = None
    logger.info(f'info: now listening to: all')

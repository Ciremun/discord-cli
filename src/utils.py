import re
from typing import Iterable, Callable

from discord.utils import find

from .client import client
from .log import logger

listen_re = re.compile(r'^([^#]{1,100})?#?([\w-]{1,100})?$')


def find_item(name: str, items: Iterable):
    return find(lambda x: x.name.lower() == name, items)


def gen_command_find_guild_channel(cmd_args: list[str], **functions):
    cmd_args = ' '.join(cmd_args)
    if cmd_args := re.match(listen_re, cmd_args):
        guild_name, channel_name = cmd_args.groups()
        if guild_name and channel_name:
            if guild := find_item(guild_name.lower(), client.guilds):
                if channel := find_item(channel_name, guild.channels):
                    functions['gc'](guild, channel)
                else:
                    logger.info(f'error: channel {channel_name} not found')
            else:
                logger.info(f'error: guild {guild_name} not found')
        elif guild_name and not channel_name:
            if guild := find_item(guild_name.lower(), client.guilds):
                functions['g'](guild)
            else:
                logger.info(f'error: guild {guild_name} not found')
        elif not guild_name and channel_name:
            if channel := find_item(channel_name, [c for g in client.guilds for c in g.channels]):
                functions['c'](channel)
            else:
                logger.info(f'error: channel {channel_name} not found')
    else:
        logger.info('error: invalid guild/channel')

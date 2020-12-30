import re
from typing import Iterable, Callable

from discord import TextChannel
from discord.utils import find

from .client import client, print_chat_message, fix_discord_emotes, message_attachments
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
                    if not isinstance(channel, TextChannel):
                        logger.info(
                            f'error: not a text channel {channel_name}')
                        return
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
                if not isinstance(channel, TextChannel):
                    logger.info(f'error: not a text channel {channel_name}')
                    return
                functions['c'](channel)
            else:
                logger.info(f'error: channel {channel_name} not found')
    else:
        logger.info('error: invalid guild/channel')


async def fetch_print_messages(channel: TextChannel, limit: int):
    history = await channel.history(limit=limit).flatten()
    for m in reversed(history):
        m.content = fix_discord_emotes(m.content)
        attachments = message_attachments(m)
        print_chat_message(
            f'[{m.guild.name}#{m.channel.name}] {m.author.display_name}: {m.clean_content}{attachments}')

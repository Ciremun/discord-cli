from typing import List

from discord import Guild
from discord.abc import GuildChannel

import src.config as cfg
from .classes import Message
from .client import client
from .log import logger

commands_map = {}


def command(*, name: str):
    def decorator(func):
        def wrapper(*args, **kwargs):
            if not client.is_ready():
                logger.error('error: client not ready')
                return
            try:
                return func(*args, **kwargs)
            except Exception as e:
                logger.exception(e)
        wrapper.__name__ = name
        commands_map[name] = wrapper
        return wrapper
    return decorator


@command(name='listen')
def listen_command(message: Message):
    find_guild = message.parts[1:]
    if not find_guild:
        guild = client.get_guild(cfg.current_guild_id)
        if guild is not None:
            guild = guild.name
        channel = client.get_channel(cfg.current_channel_id)
        if channel is not None:
            channel = channel.name
        logger.info(f'info: current guild#channel is: {guild}#{channel}')
        return
    has_channel_name = False
    channel_name = message.parts[-1]
    parts_len = len(message.parts)
    if channel_name[0] == '#':
        if parts_len == 2:
            logger.error('error: single channel name is not allowed')
            return
        has_channel_name = True
        channel_name = channel_name[1:]
    if channel_name.startswith("channel:"):
        channel_id = channel_name.split(':')[1]
        if channel_id.isdigit():
            channel = client.get_channel(int(channel_id))
            if channel is not None:
                setattr(cfg, 'current_guild_id', channel.guild.id)
                setattr(cfg, 'current_channel_id', channel.id)
                logger.info(
                    f'info: now listening to: {channel.guild.name}#{channel.name}')
            else:
                logger.error(f'error: channel_id not found: {channel_id}')
        else:
            logger.error(f'error: channel_id is not a digit: {channel_id}')
        return
    if find_guild[0].startswith("guild:"):
        guild_id = find_guild[0].split(':')[1]
        if guild_id.isdigit():
            guild = client.get_guild(int(guild_id))
            if guild is not None:
                setattr(cfg, 'current_guild_id', guild.id)
                setattr(cfg, 'current_channel_id', None)
                logger.info(f'info: now listening to: {guild.name}')
            else:
                logger.error(f'error: guild_id not found: {guild_id}')
        else:
            logger.error(f'error: guild_id is not a digit: {guild_id}')
        return
    find_guild = ' '.join(find_guild[:-1] if has_channel_name else find_guild)
    find_guild_lower = find_guild.lower()
    maybe_guild = []
    for guild in client.guilds:
        guild_name_lower = guild.name.lower()
        if find_guild_lower == guild_name_lower:
            setattr(cfg, 'current_guild_id', guild.id)
            if has_channel_name:
                maybe_channel = []
                for channel in guild.channels:
                    if channel.name == channel_name:
                        setattr(cfg, 'current_channel_id', channel.id)
                        logger.info(
                            f'info: now listening to: {guild.name}#{channel_name}')
                        if channel.guild.id != guild.id:
                            logger.warning(
                                f'warning: #{channel_name} is not a child of {guild.name}')
                        break
                    elif channel_name in channel.name:
                        maybe_channel.append(channel.name)
                else:
                    message = f'error: guild "{guild.name}" has no channel {channel_name}'
                on_name_not_found(message, maybe_channel)
            else:
                setattr(cfg, 'current_channel_id', None)
                logger.info(f'info: now listening to: {guild.name}')
            break
        elif find_guild_lower in guild_name_lower:
            maybe_guild.append(guild.name)
    else:
        message = f'error: guild "{find_guild}" not found'
        on_name_not_found(message, maybe_guild)


@command(name='all')
def all_command(message: Message):
    setattr(cfg, 'current_guild_id', None)
    setattr(cfg, 'current_channel_id', None)
    logger.info(f'info: now listening to: all')


def on_name_not_found(message: str, similar_names: List[str]):
    logger.error(message)
    if similar_names:
        newline = '\n'
        logger.info(f'similar names are:\n{newline.join(similar_names)}')

import re
import textwrap
import shutil

from discord import Client, Message, DMChannel, GroupChannel, MessageType

import src.config as cfg
from .log import logger

client = Client()
discord_emote_re = re.compile(r'<a?:(\w+|\d+):(\d{18})>')

if cfg.chat_log:
    print_func = logger.info
else:
    print_func = print


def listen_all() -> bool:
    return cfg.current_guild_id is None


def listen_guild(message: Message) -> bool:
    return cfg.current_guild_id == message.guild.id and cfg.current_channel_id is None


def listen_channel(message: Message) -> bool:
    return cfg.current_guild_id == message.guild.id and cfg.current_channel_id == message.channel.id


def fix_discord_emotes(message: str) -> str:
    return re.sub(discord_emote_re, r'\1', message)


def direct_message(message: Message) -> bool:
    return any(isinstance(message.channel, x) for x in [DMChannel, GroupChannel])


def term_col() -> int:
    return shutil.get_terminal_size().columns


def print_chat_message(message: str):
    message = textwrap.fill(message, term_col())
    print_func(message)


def fix_message(message: Message):
    message.content = fix_discord_emotes(message.content)
    message.content = message_attachments(message)
    message.content = message_references(message)
    return message


def message_attachments(message: Message):
    return message.content + '\n' + '\n'.join(a.url for a in message.attachments) if message.attachments else message.content


def message_references(message: Message):
    if ref := message.reference:
        if reply := ref.resolved:
            if isinstance(reply, Message):
                return f'@{reply.author.display_name} {message.content}'
    return message.content


def output_direct_message(message: Message):
    channel = message.channel.recipient if isinstance(message.channel, DMChannel) else message.channel.name or ', '.join(
        x.display_name for x in message.channel.recipients)
    if message.type == MessageType.call:
        output = '[*Call]'
    else:
        message = fix_message(message)
        output = message.clean_content
    print_chat_message(
        f'[*{channel}] {message.author.display_name}: {output}')


def output_message(message: Message):
    output = '['
    if cfg.current_guild_id is None:
        output += message.guild.name
    message = fix_message(message)
    print_chat_message(
        f'{output}#{message.channel.name}] {message.author.display_name}: {message.clean_content}')


@client.event
async def on_ready():
    logger.info(f'logged on as {client.user}')
    if cfg.current_guild_id is None:
        guild = 'all'
    else:
        guild = client.get_guild(cfg.current_guild_id)
        if guild:
            guild = guild.name
        else:
            logger.info(f'error: guild "{cfg.current_guild_id}" not found')
            return
    channel = client.get_channel(cfg.current_channel_id)
    if channel:
        channel = f'#{channel.name}'
    else:
        channel = ''
    logger.info(f'listening to: {guild}{channel}')


@client.event
async def on_message(message):
    if direct_message(message):
        output_direct_message(message)
    elif listen_all() or listen_guild(message) or listen_channel(message):
        output_message(message)

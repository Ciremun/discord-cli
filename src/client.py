import re
import textwrap
import shutil

import discord

import src.config as cfg
from .log import logger

client = discord.Client()
discord_emote_re = re.compile(r'<a?:(\w+|\d+):(\d{18})>')

if cfg.chat_log:
    print_func = logger.info
else:
    print_func = print


def listen_all() -> bool:
    return cfg.current_guild_id is None


def listen_guild(message: discord.Message) -> bool:
    return cfg.current_guild_id == message.guild.id and cfg.current_channel_id is None


def listen_channel(message: discord.Message) -> bool:
    return cfg.current_guild_id == message.guild.id and cfg.current_channel_id == message.channel.id


def fix_discord_emotes(message: str) -> str:
    return re.sub(discord_emote_re, r'\1', message)


def direct_message(message: discord.Message) -> bool:
    return any(isinstance(message.channel, x) for x in [discord.DMChannel, discord.GroupChannel])


def term_col() -> int:
    return shutil.get_terminal_size().columns - 1


def print_chat_message(message: str):
    message = textwrap.fill(message, term_col())
    print_func(message)


def message_attachments(message: discord.Message):
    return '\n' + '\n'.join(a.url for a in message.attachments) if message.attachments else ""


async def output_direct_message(message: discord.Message):
    message.content = fix_discord_emotes(message.content)
    channel = 'PM' if isinstance(message.channel, discord.DMChannel) else message.channel.name or ', '.join(
        x.display_name for x in message.channel.recipients)
    output = '[*Incoming Call]' if message.type == discord.MessageType.call else message.clean_content
    attachments = message_attachments(message)
    print_chat_message(
        f'[*{channel}] {message.author.display_name}: {output}{attachments}')


async def output_message(message: discord.Message):
    output = '['
    if cfg.current_guild_id is None:
        output += message.guild.name
    message.content = fix_discord_emotes(message.content)
    attachments = message_attachments(message)
    print_chat_message(
        f'{output}#{message.channel.name}] {message.author.display_name}: {message.clean_content}{attachments}')


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
        await output_direct_message(message)
        await message.ack()
    elif listen_all() or listen_guild(message) or listen_channel(message):
        await output_message(message)
        await message.ack()

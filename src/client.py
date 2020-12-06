import discord

import src.config as cfg
from .log import logger

client = discord.Client()

if cfg.chat_log:
    print_chat_message = logger.info
else:
    print_chat_message = print


def listen_all() -> bool:
    return cfg.current_guild_id is None

def listen_guild(message: discord.Message) -> bool:
    return cfg.current_guild_id == message.guild.id and cfg.current_channel_id is None

def listen_channel(message: discord.Message) -> bool:
    return cfg.current_guild_id == message.guild.id and cfg.current_channel_id == message.channel.id

async def output_message(message: discord.Message):
    output = '['
    if cfg.current_guild_id is None:
        output += message.guild.name
    print_chat_message(f'{output}#{message.channel.name}] {message.author.display_name}: {message.content}')

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
            logger.error(f'error: guild "{cfg.current_guild_id}" not found')
            return
    channel = client.get_channel(cfg.current_channel_id)
    if channel:
        channel = f'#{channel.name}'
    else:
        channel = ''
    logger.info(f'listening to: {guild}{channel}')

@client.event
async def on_message(message):
    if listen_all() or listen_guild(message) or listen_channel(message):
        await output_message(message)

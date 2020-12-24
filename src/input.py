import asyncio
from threading import Thread

from src.log import logger
from .classes import Message, QueueThread
from .client import client
import src.config as cfg
import src.commands as c

qthread = QueueThread('commands', daemon=True)


def read_input():
    logger.info('type commands or messages here')
    while True:
        input_str = input()
        if input_str.startswith(cfg.prefix):
            message = Message(input_str)
            command_name = message.parts[0][len(cfg.prefix):]
            command = c.commands_map.get(command_name)
            if command:
                qthread.create_task(command, message)
            else:
                logger.info(f'error: command {input_str} not found')
        else:
            channel = client.get_channel(cfg.current_channel_id)
            if channel is None:
                logger.info('error: no current channel')
                continue
            asyncio.run_coroutine_threadsafe(
                channel.send(input_str), client.loop)


input_thread = Thread(target=read_input)
input_thread.daemon = True

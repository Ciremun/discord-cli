from threading import Thread

from src.log import logger
from .classes import Message, QueueThread
import src.config as cfg
import src.commands as c

qthread = QueueThread('commands', daemon=True)

def read_input():
    logger.info('type commands or messages here')
    while True:
        input_str = input()
        if not input_str.startswith(cfg.prefix):
            continue
        message = Message(input_str)
        command_name = message.parts[0][len(cfg.prefix):]
        command = c.commands_map.get(command_name)
        if command:
            qthread.create_task(command, message)
        else:
            logger.error(f'error: {command_name} command not found')

input_thread = Thread(target=read_input)
input_thread.daemon = True

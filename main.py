from src.client import client
from src.input import input_thread
import src.config as cfg
import src.commands

if __name__ == '__main__':
    input_thread.start()
    client.run(cfg.token, bot=cfg.bot)

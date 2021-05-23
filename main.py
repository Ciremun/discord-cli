from src.client import client
from src.input import input_thread
import src.config as cfg
import src.commands

if __name__ == '__main__':
    input_thread.start()

    # discord is becoming worse sadge
    client.run(cfg.token, bot=True)

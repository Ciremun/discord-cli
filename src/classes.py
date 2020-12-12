from queue import Queue
from threading import Thread

class Message:

    def __init__(self, message: str):
        self.content = message
        self.parts = message.split()

    def __str__(self):
        return self.content

class QueueThread(Thread):

    def __init__(self, name: str, **kwargs):
        Thread.__init__(self, **kwargs)
        self.name = name
        self.q = Queue()
        self.start()

    def run(self):
        while True:
            task = self.q.get()
            try:
                task['func'](*task['args'], **task['kwargs'])
            finally:
                self.q.task_done()

    def create_task(self, func, *args, **kwargs):
        self.q.put({'func': func, 'args': args, 'kwargs': kwargs})

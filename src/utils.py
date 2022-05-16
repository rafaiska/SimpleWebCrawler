import _queue
from multiprocessing import Queue


def pop_queue(queue: Queue, timeout=None):
    try:
        return queue.get(block=True if timeout else False, timeout=timeout)
    except _queue.Empty:
        return None

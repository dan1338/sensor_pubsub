from queue import PriorityQueue
import time

class MessageQueue:
    """
    Orders messages based on sequence number.
    Keeps track of time when it was last updated to allow flushing during a stall
    """
    def __init__(self, seq_wrap=((1 << 32) - 1)):
        self.seq_num = 0
        self.seq_wrap = seq_wrap
        self.pq = PriorityQueue()
        self.last_pop_time = None

    def _update_last_pop(self):
        self.last_pop_time = time.perf_counter()

    def get_stall_time(self) -> float:
        return time.perf_counter() - self.last_pop_time if self.last_pop_time else 0

    def put_message(self, seq_num: int, msg: object):
        self.pq.put((seq_num, msg))

        # Initalize the stall timer
        if self.last_pop_time is None:
            self._update_last_pop()

    def pop_message(self, force_order=True) -> object | None:
        if self.pq.empty():
            return None

        seq_num, msg = self.pq.get()
        is_ordered = (self.seq_num == seq_num)

        # Return if its ordered or we're flushing
        if is_ordered or not force_order:
            self._update_last_pop()
            self.seq_num = (self.seq_num + 1) & self.seq_wrap
            return msg

        # Put the message back
        self.pq.put((seq_num, msg))

        return None

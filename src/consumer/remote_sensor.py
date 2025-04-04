import logging

from ..transport import IMUPayload
from .message_queue import MessageQueue

logger = logging.getLogger(__name__)

class RemoteSensor:
    def __init__(self, id_: int, stall_time: float):
        self.id = id_
        self.stall_time = stall_time
        self.message_queue = MessageQueue()

    def put_message(self, seq_num: int, msg: IMUPayload):
        self.message_queue.put_message(seq_num, msg)

    def update(self):
        # Handle ordered messages
        while imu_state := self.message_queue.pop_message():
            self._update(imu_state)

        if self.message_queue.get_stall_time() >= self.stall_time:
            # Flush the rest if stalled
            while imu_state := self.message_queue.pop_message(force_order=False):
                self._update(imu_state)

    def _update(self, imu_state: IMUPayload):
        pass

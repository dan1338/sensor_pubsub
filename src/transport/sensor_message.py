from typing import Tuple
import struct

class SensorMessage:
    """
    Class for easy assembly of a sensor message into a fixed size buffer

    Buffer layout:
    +----+---------+------+
    | id | seq_num | body |
    +----+---------+------+
    0    1         5      5 + body_size

    id      - identifies the sender
    seq_num - the sequence number of current packet
    body    - the message payload
    """
    def __init__(self, body_size):
        self.header_size = 5 # For sender id + sequence number
        self.body_size = body_size
        total_size = self.header_size + self.body_size

        self.buf = bytearray(total_size)

    def get_buffer(self) -> bytearray:
        return self.buf

    def pack(self, id_: int, seq_num: int, body: bytes):
        struct.pack_into('<BI', self.buf, 0, id_, seq_num)
        self.buf[self.header_size:] = body

    def unpack(self) -> Tuple[int, int, bytes]:
        id_, seq_num = struct.unpack_from('<BI', self.buf)
        return id_, seq_num, bytes(self.buf[self.header_size:])

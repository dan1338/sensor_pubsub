import struct
from collections import namedtuple

IMUPayload = namedtuple('IMUPayload', """
    acc_x
    acc_y
    acc_z
    acc_timestamp
    gyro_x
    gyro_y
    gyro_z
    gyro_timestamp
    mag_x
    mag_y
    mag_z
    mag_timestamp
""")

# Struct format string for un/packing the IMUPayload
IMUPayload_format = '3fI3fI3fI'
IMUPayload_size = struct.calcsize(IMUPayload_format)

# Sanity check
assert IMUPayload_size == 48

def pack_imu_payload(imu_payload: IMUPayload) -> bytes:
    return struct.pack(IMUPayload_format, *imu_payload)

def unpack_imu_payload(buffer: bytes) -> IMUPayload:
    return IMUPayload._make(struct.unpack(IMUPayload_format, buffer))

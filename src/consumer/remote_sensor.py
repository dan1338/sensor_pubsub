import logging
import numpy as np
import quaternion as quat

from ..transport import IMUPayload
from .message_queue import MessageQueue

logger = logging.getLogger(__name__)

class RemoteSensor:
    """
    Represents a remote sensor sending us state updates.
    Messages are submitted with put_message and calling update will process the state changes
    """
    def __init__(self, id_: int, stall_time: float):
        self.id = id_
        self.stall_time = stall_time
        self.message_queue = MessageQueue()
        
        # Estimated orientation of the system
        self.orientation = np.quaternion(1, 0, 0, 0)
        self.prev_state = None

        # Weight for gyroscope data
        self.gyro_alpha = 0.98

    def put_message(self, seq_num: int, msg: IMUPayload):
        self.message_queue.put_message(seq_num, msg)

    def update(self):
        # Handle ordered messages
        while imu_state := self.message_queue.pop_message():
            self._update(imu_state)

        # Flush the rest if stalled
        if self.message_queue.get_stall_time() >= self.stall_time:
            logging.warn(f'stalled for {self.message_queue.get_stall_time()}s')
            while imu_state := self.message_queue.pop_message(force_order=False):
                self._update(imu_state)

    def _update(self, imu_state: IMUPayload):
        """
        Update the estimated orientation of the system based on sensor readings.
        This implementation combines a rotation estimate from integration of gyroscope rates and absolute orientation estimate from
        tilt-compensated magnetometer readings. The impact of each term is controlled by the gyro_alpha coefficient
        """
        normalize = lambda x: x / np.linalg.norm(x)

        if self.prev_state is not None:
            acc_dt = (imu_state.acc_timestamp - self.prev_state.acc_timestamp) / 1e3
            gyro_dt = (imu_state.gyro_timestamp - self.prev_state.gyro_timestamp) / 1e3
            mag_dt = (imu_state.mag_timestamp - self.prev_state.mag_timestamp) / 1e3

            accel = np.array([self.prev_state.acc_x, self.prev_state.acc_y, self.prev_state.acc_z])
            gyro = np.array([self.prev_state.gyro_x, self.prev_state.gyro_y, self.prev_state.gyro_z])
            mag = np.array([self.prev_state.mag_x, self.prev_state.mag_y, self.prev_state.mag_z])

            # Find the compass orientation based on accelerometer and tilt-compensated magnetometer readings
            up = -normalize(accel)
            right = normalize(np.cross(mag, up))
            forward = normalize(np.cross(right, up))
            compass_orientation = quat.from_rotation_matrix(np.c_[right, up, forward])

            # Find the delta rotation from the integrated gyro readings
            gyro_rotation = quat.from_rotation_vector(gyro * gyro_dt)

            # Blend the compass orientation and the gyro orientation
            self.orientation = quat.slerp(compass_orientation, gyro_rotation * self.orientation, 0, 1, self.gyro_alpha)

        self.prev_state = imu_state

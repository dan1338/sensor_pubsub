import time
import numpy as np
from typing import Tuple

from ..transport.imu_payload import IMUPayload

class IMUGenerator:
    """
    Generates randomized imu data
    """

    def __init__(self, delta_time: float):
        self.start_time = time.perf_counter()
        self.delta_time = delta_time

    def _random_acc(self) -> Tuple[float, float, float]:
        r = np.random.normal(size=3)
        r /= np.linalg.norm(r)
        r *= 9.81

        return r

    def _random_gyro(self) -> Tuple[float, float, float]:
        r = np.random.normal(size=3) * 180 * self.delta_time

        return r

    def _random_mag(self) -> Tuple[float, float, float]:
        r = np.random.normal(size=3) * self.delta_time

        return r


    def get_next(self) -> IMUPayload:
        current_time = (time.perf_counter() - self.start_time) * 1000 # ms

        return IMUPayload(
            *self._random_acc(),
            int(current_time),
            *self._random_gyro(),
            int(current_time),
            *self._random_mag(),
            int(current_time),
        )

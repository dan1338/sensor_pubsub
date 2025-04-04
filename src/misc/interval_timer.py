import time

class IntervalTimer:
    """
    A timer that aligns operations to a fixed repetition interval.
    Uses sleep for longer waits and spins for short, precise adjustments.
    """
    def __init__(self, frequency_hz: int):
        self.interval = 1.0 / frequency_hz
        self.next_time = time.perf_counter()
        self.sleep_threshold = 0.004 # 4ms

    def reset(self):
        self.next_time = time.perf_counter()

    def wait(self):
        """
        Wait until the next scheduled interval
        """
        now = time.perf_counter()
        time_left = self.next_time - now

        if time_left > self.sleep_threshold:
            # Sleep for most of the duration, leaving a small buffer
            time.sleep(max(0, time_left - 0.0001))

            # Recheck time after waking
            while time.perf_counter() < self.next_time:
                pass # Spin for the last bit
        elif time_left > 0:
            # Spin for short durations
            while time.perf_counter() < self.next_time:
                pass

        self.next_time += self.interval

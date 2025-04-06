import numpy as np
import quaternion as quat
from typing import Tuple

class IMUSimulator:
    """
    Simulates a sensor system with 3 axis accelerometer, gyroscope, and magnetometer performing random motion based on random sampled and integrated angular velocity.
    """

    def __init__(self, time_step: float, max_angular_vel: float = np.pi / 4, accel_noise: float = 0.05, gyro_noise: float = 0.01, mag_noise: float = 10):
        self.orientation = np.quaternion(1, 0, 0, 0)
        self.dt = time_step

        self.gravity = np.array([0, -9.81, 0])          # m/s^2
        self.magnetic_field = np.array([0, 400, -200])  # mGauss

        # Limits the maximum angular velocity
        self.max_angular_vel = max_angular_vel
        
        # Sensor noise levels
        self.accel_noise = accel_noise  # m/s^2
        self.gyro_noise = gyro_noise    # rad/s
        self.mag_noise = mag_noise      # mGauss
        
        # For smooth motion
        self.current_angular_vel = np.zeros(3)
        self.max_angular_accel = max_angular_vel * 10  # rad/s^2

    def _get_rotation(self) -> np.quaternion:
        # Apply random acceleration instead of random velocity
        angular_accel = np.random.normal(0, self.max_angular_accel, 3)
        
        # Update angular velocity with acceleration and apply damping
        self.current_angular_vel += angular_accel * self.dt
        
        # Clamp angular velocity to maximum
        self.current_angular_vel = np.clip(self.current_angular_vel, -self.max_angular_vel, self.max_angular_vel)
        
        # Create rotation quaternion from angular velocity
        angle = np.linalg.norm(self.current_angular_vel)
        if angle > 0:
            axis = self.current_angular_vel / np.linalg.norm(self.current_angular_vel)
            return quat.from_rotation_vector(axis * angle * self.dt)

        return np.quaternion(1, 0, 0, 0)

    def __next__(self) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        q_rotation = self._get_rotation()
        
        # Update orientation
        self.orientation = q_rotation * self.orientation
        
        # Accelerometer: gravity in sensor frame + noise
        accel = quat.rotate_vectors(self.orientation, self.gravity)
        accel += np.random.normal(0, self.accel_noise, 3)
        
        # Gyroscope: angular velocity + noise
        gyro = self.current_angular_vel.copy()
        gyro += np.random.normal(0, self.gyro_noise, 3)
        
        # Magnetometer: magnetic field in sensor frame + noise
        mag = quat.rotate_vectors(self.orientation, self.magnetic_field)
        mag += np.random.normal(0, self.mag_noise, 3)
        
        return (accel, gyro, mag)
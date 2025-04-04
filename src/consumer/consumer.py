import argparse
import logging
from socket import socket, AF_UNIX, SOCK_DGRAM

from ..misc import setup_logging
from ..transport import SensorMessage, IMUPayload_size, unpack_imu_payload
from .remote_sensor import RemoteSensor

logger = logging.getLogger(__name__)

def consume_loop(sock, stall_time: float):
    sensor_msg = SensorMessage(IMUPayload_size)
    buf = sensor_msg.get_buffer()

    # Dictionary of all sensors connected and broadcasting their state
    remote_sensors = dict()

    while True:
        recv_size = 0

        try:
            recv_size = sock.recv_into(buf, len(buf))
        except TimeoutError:
            logger.debug('recv timeout')
        except Exception as e:
            logger.error(f'recv threw an exception {e}')

        # Make sure packet was received
        if recv_size == len(buf):
            sender_id, seq_num, packed_payload = sensor_msg.unpack()

            if logger.getEffectiveLevel() > logging.DEBUG:
                logger.info(f'message received id:{sender_id} seq:{seq_num}')
            else:
                logger.debug(f'message received id:{sender_id} seq:{seq_num} {buf}')

            imu_payload = unpack_imu_payload(packed_payload)
            logger.debug(f'received imu payload {imu_payload}')

            # Create message queue if first message from this sender
            if sender_id not in remote_sensors:
                remote_sensors[sender_id] = RemoteSensor(sender_id, stall_time)

            # Get message queue for sender
            remote_sensor = remote_sensors[sender_id]
            remote_sensor.put_message(seq_num, imu_payload)

        # Process imu data
        for remote_sensor in remote_sensors.values():
            logger.info(f'updating remote sensor {remote_sensor.id}')
            remote_sensor.update()

def open_consumer_sock(path: str) -> socket:
    sock = socket(AF_UNIX, SOCK_DGRAM, 0)

    from os import access, unlink, F_OK
    # Remove if socket already exists
    if access(path, F_OK):
        logger.debug('socket already exists')
        unlink(path)
        logger.debug('removed existing socket')

    sock.bind(path)
    logger.info(f'socket bound at {path}')

    return sock

def main():
    parser = argparse.ArgumentParser(prog='consumer.py')
    parser.add_argument('--socket-path',
        required=True,
        help='set path to the UNIX socket')
    parser.add_argument('--timeout-ms',
        default=100,
        type=int,
        help='set how long the consumer should wait for missing packets')
    parser.add_argument(
        '--log-level',
        default='INFO',
        choices=['debug', 'info', 'warning', 'error', 'critical'],
        help='set logging level (default: info)')

    args = parser.parse_args()

    setup_logging(args.log_level)

    logger.debug(f'socket path: {args.socket_path}')
    logger.debug(f'timeout: {args.timeout_ms}ms')

    try:
        sock = open_consumer_sock(args.socket_path)

        timeout_s = args.timeout_ms / 1e3
        sock.settimeout(timeout_s)
        consume_loop(sock, timeout_s)
    except KeyboardInterrupt:
        pass
    except Exception as e:
        logger.error(e)

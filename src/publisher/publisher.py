import argparse
import logging
from socket import socket, AF_UNIX, SOCK_DGRAM

from ..misc import setup_logging, IntervalTimer
from ..transport import SensorMessage, IMUPayload_size, pack_imu_payload
from .imu_generator import IMUGenerator

logger = logging.getLogger(__name__)

def publish_loop(sock: socket, socket_path: str, sender_id: int, frequency_hz: int):
    # Packet sequence counter
    seq_num = 0
    seq_wrap = (1 << 32) - 1 # UINT32_MAX

    sensor_msg = SensorMessage(IMUPayload_size)
    imu_generator = IMUGenerator(delta_time=(1.0 / frequency_hz))

    # The timer allows to send payloads at set interval
    timer = IntervalTimer(frequency_hz)
    timer.reset()

    while True:
        imu_payload = imu_generator.get_next()
        logger.debug(f'generated imu payload {imu_payload}')

        packed_payload = pack_imu_payload(imu_payload)
        sensor_msg.pack(sender_id, seq_num, packed_payload)
        buf = sensor_msg.get_buffer()

        # Wait for the interval timer to signal
        timer.wait()

        if logger.getEffectiveLevel() > logging.DEBUG:
            logger.info(f'sending message seq:{seq_num}')
        else:
            logger.debug(f'sending message seq:{seq_num} {buf}')

        try:
            sock.sendto(buf, socket_path)
        except Exception as e:
            logger.error(f'send threw an exception {e}')

        # Increment the sequence number with modulo
        seq_num = (seq_num + 1) & seq_wrap

def open_publisher_sock(path: str) -> socket:
    sock = socket(AF_UNIX, SOCK_DGRAM, 0)

    return sock

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--socket-path',
        required=True,
        help='set path to the UNIX socket')
    parser.add_argument('--frequency-hz',
        default=100,
        type=int,
        help='set the frequency with with the payload is sent')
    parser.add_argument('--sender-id',
        type=int,
        default=0,
        help='set the identity of the sender (default: 0)')
    parser.add_argument(
        '--log-level',
        default='INFO',
        choices=['debug', 'info', 'warning', 'error', 'critical'],
        help='set logging level (default: info)')

    args = parser.parse_args()

    setup_logging(args.log_level)

    logger.debug(f'socket path: {args.socket_path}')
    logger.debug(f'frequency: {args.frequency_hz}Hz')
    logger.debug(f'sender_id: {args.sender_id}')

    try:
        sock = open_publisher_sock(args.socket_path)
        publish_loop(sock, args.socket_path, args.sender_id, args.frequency_hz)
    except KeyboardInterrupt:
        pass
    except Exception as e:
        logger.error(e)

if __name__ == "__main__":
    main()

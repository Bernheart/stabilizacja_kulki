import time
from lib.comm.robot_protocol import RobotProtocol


class RobotComm:
    def __init__(self, port, baudrate, timeout=1):
        import serial
        self.arduino = serial.Serial(port, baudrate, timeout=timeout)

    def send_command(self, cmd: str, params=None, retries=3, timeout=1.0) -> tuple[bool, str | None]:
        frame = RobotProtocol.build_frame(cmd, params)
        for attempt in range(retries):
            self.arduino.reset_input_buffer()
            self.arduino.write(frame.encode())
            self.arduino.flush()

            start_time = time.time()
            while time.time() - start_time < timeout:
                if self.arduino.in_waiting > 0:
                    response = self.arduino.readline().decode(errors="ignore").strip()
                    if not response:
                        continue

                    # ACK, NACK, or DATA
                    if response.startswith("<ACK"):
                        return True, response
                    elif response.startswith("<NACK"):
                        print(f"[ERROR] Command failed: {response}")
                        break
                    elif response.startswith("<DATA") or response.startswith("<INFO"):
                        print(f"[DATA] {response}")
                        return True, response
            # Timeout → retry
            wait = timeout * (2 ** attempt)  # exponential backoff
            print(f"[WARN] No response, retrying in {wait:.1f}s...")
            time.sleep(wait)

        return False, None

    def close(self):
        self.ser.close()
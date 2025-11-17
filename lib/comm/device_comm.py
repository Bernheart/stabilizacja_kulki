import serial
import time
from threading import Event
from lib.comm.robot_protocol import RobotProtocol # or device_protocol.py

class DeviceComm:
    def __init__(self, port, baudrate, timeout=1):
        self.arduino = serial.Serial(port, baudrate, timeout=timeout)
        if not self.arduino.is_open:
            raise serial.SerialException(f"Could not open port {port}")
            
        time.sleep(2) # Give Arduino time to reset
        # self.arduino.flushInput()
        self.wait_for_ready()

    def wait_for_ready(self, timeout=5):
        """Wait for the Arduino to send its <READY> signal."""
        print(f"[INFO] Waiting for device <READY> on {self.arduino.port}...")
        start_time = time.time()
        while time.time() - start_time < timeout:
            if self.arduino.in_waiting > 0:
                line = self.read_line()
                if line and "<READY>" in line:
                    print("[INFO] Device is READY.")
                    return
        raise serial.SerialTimeoutException("Device did not send <READY>.")

    def send_command(self, cmd: str, params=None) -> tuple[bool, str | None]:
        """Builds and sends a frame, then waits for a response."""
        frame = RobotProtocol.build_frame(cmd, params)
        try:
            self.arduino.reset_input_buffer()
            self.arduino.write(frame.encode('utf-8'))
            self.arduino.flush()
        except Exception as e:
            print(f"[ERROR] Serial write failed: {e}")
            return False, None

        # Wait for a response (ACK, NACK, INFO, DATA)
        start_time = time.time()
        while time.time() - start_time < self.arduino.timeout:
            response = self.read_line()
            if not response:
                continue

            if response.startswith(("<ACK", "<NACK", "<INFO", "<DATA")):
                if response.startswith("<NACK"):
                    print(f"[CMD_ERROR] {response}")
                return True, response

        print(f"[WARN] Command timeout for: {frame}")
        return False, None

    def read_line(self) -> str | None:
        """Reads a single line from serial, handling errors."""
        if not self.arduino or not self.arduino.is_open:
            return None
        try:
            if self.arduino.in_waiting > 0:
                line = self.arduino.readline()
                return line.decode('utf-8', errors="ignore").strip()
        except Exception as e:
            print(f"[ERROR] Serial read error: {e}")
        return None

    def listen_for_data(self, stop_event: Event):
        """Continuously read and print data lines until stop_event is set."""
        print("[INFO] Telemetry listener started... (Press Enter on empty line to stop test)")
        while not stop_event.is_set():
            line = self.read_line()
            if line:
                if line.startswith(("<DATA", "<INFO")):
                    print(f"[TELEMETRY] {line}")
                # We ignore ACK/NACK here, they are for send_command
            else:
                time.sleep(0.01) # Avoid busy-waiting
        print("[INFO] Telemetry listener stopped.")

    def close(self):
        if self.arduino and self.arduino.is_open:
            # Send stop command before closing
            self.send_command("D", 0)
            self.arduino.close()
            print(f"[INFO] Serial port {self.arduino.port} closed.")
import serial
import time
import random

# Change this to your fake Arduino port (the second one from socat)
PORT = "/dev/ttys038"
BAUDRATE = 9600

# Internal state to mimic Arduino globals
state = {
    "LEFT_MOTOR_PIN": 9,
    "RIGHT_MOTOR_PIN": 10,
    "SONAR_PIN": "A0",
    "IR_PIN": "A1",
    "FORWARD_DIR": 1,
    "ROTATION_DIR": 1,
    "CURRENT_SPEED": 150,
}

# ======== Checksum ========
def calc_checksum(data: str) -> int:
    """Sum of ASCII chars before last | mod 256"""
    return sum(ord(c) for c in data) % 256

def validate_checksum(full_frame: str) -> bool:
    try:
        frame = full_frame.strip("<>")
        parts = frame.split("|")
        if len(parts) < 3:
            return False
        given = int(parts[-1])
        data = "|".join(parts[:-1])
        return calc_checksum(data) == given
    except Exception:
        return False


# ======== Command Handlers ========
def handle_move(param):
    print(f"[FAKE] Moving robot {param} cm")
    time.sleep(abs(int(param)) * 0.05)
    return ["<INFO|MOVE_DONE>"]

def handle_rotate(param):
    print(f"[FAKE] Rotating robot {param} deg")
    time.sleep(abs(int(param)) * 0.01)
    return ["<INFO|ROT_DONE>"]

def handle_stop(_):
    print("[FAKE] Stop robot")
    return []

def handle_speed(param):
    v = max(0, min(255, int(param)))
    state["CURRENT_SPEED"] = v
    return [f"<INFO|SPEED_SET|{v}>"]

def handle_sonar(_):
    distance = random.randint(5, 300)
    return [f"<DATA|B|{distance}>"]

def handle_ir(_):
    val = random.randint(0, 1023)
    return [f"<DATA|I|{val}>"]

def handle_config(param):
    print(f"[FAKE] Config updated: {param}")
    return ["<INFO|CONFIG_UPDATED>"]


COMMANDS = {
    "M": handle_move,
    "R": handle_rotate,
    "S": handle_stop,
    "V": handle_speed,
    "B": handle_sonar,
    "I": handle_ir,
    "C": handle_config,
}


# ======== Main Loop ========
def run_fake_arduino():
    with serial.Serial(PORT, BAUDRATE, timeout=1) as ser:
        print(f"[FAKE] Arduino simulator started on {PORT}")
        ser.write(b"<READY>\n")

        while True:
            if not ser.in_waiting:
                time.sleep(0.05)
                continue

            frame = ser.readline().decode(errors="ignore").strip()
            if not frame:
                continue

            print(f"[FAKE] Received: {frame}")

            if not frame.startswith("<") or not frame.endswith(">"):
                ser.write(b"<NACK|BAD_FORMAT>\n")
                continue

            if not validate_checksum(frame):
                ser.write(b"<NACK|CHK_ERR>\n")
                continue

            # Remove <> and split
            inner = frame.strip("<>")
            parts = inner.split("|")
            cmd = parts[0]
            param = parts[1] if len(parts) > 1 else ""

            handler = COMMANDS.get(cmd[0])
            if not handler:
                ser.write(f"<NACK|{cmd}|UNKNOWN_CMD>\n".encode())
                continue

            responses = handler(param)
            for resp in responses:
                ser.write((resp + "\n").encode())
            ser.write((f"<ACK|{cmd}>\n").encode())


if __name__ == "__main__":
    run_fake_arduino()
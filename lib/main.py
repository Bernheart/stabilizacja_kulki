import sys
from lib.managers.command_manager import CommandManager
from lib.managers.robot_context import RobotContext
from lib.config.app_config import AppConfig


def main():
    print("=== PC ↔ Arduino Robot Control Interface ===")

    # --- Load config ---
    try:
        config = AppConfig()
        port = config.serial.port
        baudrate = config.serial.baudrate
        timeout = config.serial.timeout
    except Exception as e:
        print(f"[ERROR] Failed to load configuration: {e}")
        sys.exit(1)

    # --- Initialize Robot Context ---
    try:
        robot_context = RobotContext(port, baudrate)
        print(f"[INFO] Connected to {port} @ {baudrate} baud.")
    except Exception as e:
        print(f"[ERROR] Could not open serial port '{port}': {e}")
        print("Tip: use socat virtual ports to emulate Arduino for testing.")
        sys.exit(1)

    # --- Initialize Command Manager ---
    # Inject the robot context so robot commands can use it
    cmd_manager = CommandManager(robot_context)

    # --- Run interactive terminal ---
    try:
        cmd_manager.run()
    except KeyboardInterrupt:
        print("\n[INFO] Interrupted by user.")
    finally:
        print("[INFO] Closing connection...")
        try:
            robot_context.comm.close()
        except Exception:
            pass
        print("[INFO] Exiting system. Goodbye!")


if __name__ == "__main__":
    main()
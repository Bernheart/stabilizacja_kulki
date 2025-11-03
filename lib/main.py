import sys
from lib.managers.command_manager import CommandManager
from lib.managers.device_context import DeviceContext
from lib.config.app_config import AppConfig

def main():
    print("=== Project 2: Ball Balancer Interface ===")

    # --- Load config ---
    try:
        config = AppConfig()
    except Exception as e:
        print(f"[ERROR] Failed to load configuration: {e}")
        sys.exit(1)

    # --- Initialize Device Context ---
    try:
        # Pass timeout from config
        device_context = DeviceContext(
            config.serial.port,
            config.serial.baudrate,
            config.serial.timeout
        )
    except Exception as e:
        print(f"[ERROR] Could not open serial port '{config.serial.port}': {e}")
        sys.exit(1)

    # --- Initialize Command Manager ---
    cmd_manager = CommandManager(device_context)

    # --- Run interactive terminal ---
    try:
        cmd_manager.run()
    except KeyboardInterrupt:
        print("\n[INFO] Interrupted by user.")
    finally:
        print("[INFO] Closing connection...")
        try:
            # Ask manager to stop threads and send stop command
            cmd_manager.cleanup()
            device_context.comm.close()
        except Exception:
            pass
        print("[INFO] Exiting system. Goodbye!")


if __name__ == "__main__":
    main()
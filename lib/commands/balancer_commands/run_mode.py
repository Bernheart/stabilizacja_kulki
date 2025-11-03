import time
from lib.commands.command import Command
from lib.managers.device_context import DeviceContext

class RunModeCommand(Command):
    def __init__(self, manager):
        self.manager = manager # Injects the CommandManager

    def name(self) -> str: return "run"
    
    def execute(self, context: DeviceContext, *args, **kwargs):
        print("[RUN] Starting grading run...")
        
        # Stop any active listener
        self.manager.stop_listener_thread()
        
        # Send command to start run mode
        success, resp = context.comm.send_command("R")
        if not success:
            print(f"[ERROR] Could not start run mode: {resp}")
            return
        
        print(f"[RUN] {resp}. Stabilizing (10s) and measuring (3s)...")
        print("[RUN] Waiting for <INFO|MAE|...> response...")
        
        # Block and listen for the *final* result
        # The run takes 13s + processing. We'll wait up to 20s.
        start_time = time.time()
        result_found = False
        try:
            while time.time() - start_time < 20.0:
                line = context.comm.read_line()
                if line:
                    if line.startswith("<INFO|MAE"):
                        print(f"\n[RESULT] {line}\n")
                        result_found = True
                        break
                    elif line.startswith("<NACK"):
                        print(f"\n[RUN_ERROR] {line}\n")
                        result_found = True
                        break
                    else:
                        print(f"[RUN_INFO] {line}") # e.g., <INFO|PHASE_2_START>
                time.sleep(0.05)
            
            if not result_found:
                print("[ERROR] Did not receive MAE result from device. Timed out.")

        except KeyboardInterrupt:
            print("\n[RUN] Run interrupted by user. Sending STOP.")
            self.manager.stop_listener_thread()
            context.comm.send_command("D", 0) # Send stop

    def help(self) -> str:
        return "run — Starts the 13-second official grading run."
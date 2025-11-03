from lib.commands.command import Command
from lib.managers.device_context import DeviceContext

class TestModeCommand(Command):
    def __init__(self, manager):
        self.manager = manager # Injects the CommandManager

    def name(self) -> str: return "test"
    
    def execute(self, context: DeviceContext, *args, **kwargs):
        # Stop any listener that might be running
        self.manager.stop_listener_thread()
        
        # Send command to start test mode
        success, resp = context.comm.send_command("D", 1)
        if not success:
            print(f"[ERROR] Could not start test mode: {resp}")
            return
            
        print(f"[TEST] {resp}")
        # Start the listener to print telemetry
        self.manager.start_listener_thread()

    def help(self) -> str:
        return "test — Starts test mode, printing telemetry. Press Enter to stop."
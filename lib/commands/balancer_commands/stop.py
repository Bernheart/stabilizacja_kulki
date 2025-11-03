from lib.commands.command import Command
from lib.managers.device_context import DeviceContext

class StopCommand(Command):
    def __init__(self, manager):
        self.manager = manager # Injects the CommandManager

    def name(self) -> str: return "stop"
    
    def execute(self, context: DeviceContext, *args, **kwargs):
        print("[STOP] Stopping all PID activity...")
        self.manager.stop_listener_thread()
        success, resp = context.comm.send_command("D", 0) # 'D' with param 0 stops all
        print(f"[STOP] {resp if success else 'Failed'}")

    def help(self) -> str:
        return "stop — Stops any active PID loop (test or run mode)."
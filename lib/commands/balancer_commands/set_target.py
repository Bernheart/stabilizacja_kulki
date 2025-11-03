from lib.commands.command import Command
from lib.managers.device_context import DeviceContext

class SetTargetCommand(Command):
    def name(self) -> str: return "target"
    
    def execute(self, context: DeviceContext, *args, **kwargs):
        if not args:
            return print(self.help())
        try:
            dist = float(args[0])
            success, resp = context.comm.send_command("T", dist)
            print(f"[TARGET] {resp if success else 'Failed'}")
        except ValueError:
            print("[ERROR] Invalid distance. Must be a float (e.g., 15.5)")
        except Exception as e:
            print(f"[ERROR] {e}")

    def help(self) -> str:
        return "target <cm> — Sets the target distance (float)."
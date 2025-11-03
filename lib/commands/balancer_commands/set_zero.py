from lib.commands.command import Command
from lib.managers.device_context import DeviceContext

class SetZeroCommand(Command):
    def name(self) -> str: return "zero"
    
    def execute(self, context: DeviceContext, *args, **kwargs):
        if not args:
            return print(self.help())
        try:
            zero_pos = int(args[0])
            if not 0 <= zero_pos <= 180:
                print("[ERROR] Angle must be between 0 and 180.")
                return
            success, resp = context.comm.send_command("Z", zero_pos)
            print(f"[ZERO] {resp if success else 'Failed'}")
        except ValueError:
            print("[ERROR] Invalid angle. Must be an integer (e.g., 90)")
        except Exception as e:
            print(f"[ERROR] {e}")

    def help(self) -> str:
        return "zero <angle> — Sets the servo's zero (level) position (int, 0-180)."
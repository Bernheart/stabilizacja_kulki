from lib.commands.command import Command
from lib.managers.device_context import DeviceContext

class SetPidCommand(Command):
    def name(self) -> str: return "pid"
    
    def execute(self, context: DeviceContext, *args, **kwargs):
        if len(args) != 3:
            return print(self.help())
        try:
            kp, ki, kd = float(args[0]), float(args[1]), float(args[2])
            # Send as a single string parameter, separated by ';'
            params = f"{kp};{ki};{kd}"
            success, resp = context.comm.send_command("P", params)
            print(f"[PID] {resp if success else 'Failed'}")
        except ValueError:
            print("[ERROR] Invalid gains. Must be 3 floats (e.g., 2.1 0.5 0.01)")
        except Exception as e:
            print(f"[ERROR] {e}")

    def help(self) -> str:
        return "pid <Kp> <Ki> <Kd> — Sets PID gains (3 floats)."
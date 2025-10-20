from lib.commands.command import Command
from lib.managers.robot_context import RobotContext

class RotateRobot(Command):
    def name(self) -> str:
        return "rotate"

    def execute(self, context: RobotContext, *args, **kwargs):
        deg = int(args[0]) if args else 0
        success, resp = context.comm.send_command("R", deg)
        print("[ROTATE]", resp if success else "Failed")

    def help(self) -> str:
        return "rotate <deg> — rotate robot by given degrees (+right / -left)"
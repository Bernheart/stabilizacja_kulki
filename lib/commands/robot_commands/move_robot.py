from lib.commands.command import Command
from lib.managers.robot_context import RobotContext

class MoveRobot(Command):
    def name(self) -> str:
        return "move"

    def execute(self, context: RobotContext, *args, **kwargs):
        distance = int(args[0]) if args else 0
        success, resp = context.comm.send_command("M", distance)
        print("[MOVE]", resp if success else "Failed")

    def help(self) -> str:
        return "move <cm> — move the robot by given centimeters (+forward / -backward)"
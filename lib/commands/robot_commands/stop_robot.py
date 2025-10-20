from lib.commands.command import Command
from lib.managers.robot_context import RobotContext

class StopRobot(Command):
    def name(self) -> str:
        return "stop"

    def execute(self, context: RobotContext, *args, **kwargs):
        success, resp = context.comm.send_command("S")
        print("[STOP]", resp if success else "Failed")

    def help(self) -> str:
        return "stop — immediately stop all motors"
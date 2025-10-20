from lib.commands.command import Command
from lib.managers.robot_context import RobotContext

class InfraredSensor(Command):
    def name(self) -> str:
        return "ir"

    def execute(self, context: RobotContext, *args, **kwargs):
        success, resp = context.comm.send_command("I")
        print("[IR]", resp if success else "Failed")

    def help(self) -> str:
        return "ir — read IR sensor value"
from lib.commands.command import Command
from lib.managers.robot_context import RobotContext

class BeemSonar(Command):
    def name(self) -> str:
        return "sonar"

    def execute(self, context: RobotContext, *args, **kwargs):
        success, resp = context.comm.send_command("B")
        print("[SONAR]", resp if success else "Failed")

    def help(self) -> str:
        return "sonar — read sonar distance in cm"
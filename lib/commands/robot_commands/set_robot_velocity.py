from lib.commands.command import Command
from lib.managers.robot_context import RobotContext

class SetRobotVelocity(Command):
    def name(self) -> str:
        return "velocity"

    def execute(self, context: RobotContext, *args, **kwargs):
        v = int(args[0]) if args else 150
        success, resp = context.comm.send_command("V", v)
        print("[VELOCITY]", resp if success else "Failed")

    def help(self) -> str:
        return "velocity <0–255> — set linear speed"
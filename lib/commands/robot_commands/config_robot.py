from lib.commands.command import Command
from lib.managers.robot_context import RobotContext

class ConfigureRobot(Command):
    def name(self) -> str:
        return "config"

    def execute(self, context: RobotContext, *args, **kwargs):
        if not args:
            print("Usage: config L9;R10;S0;I1;F1;T-1")
            return
        config_str = args[0]
        success, resp = context.comm.send_command("C", config_str)
        print("[CONFIG]", resp if success else "Failed")

    def help(self) -> str:
        return "config <L9;R10;S0;I1;F1;T-1> — configure pins and directions"
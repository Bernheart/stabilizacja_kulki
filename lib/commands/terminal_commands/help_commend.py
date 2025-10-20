from lib.commands.command import Command


class HelpCommand(Command):
    def __init__(self, commands: dict[str, Command], robot_commands: dict[str, Command]):
        self.commands = commands
        self.robot_commands = robot_commands

    def name(self) -> str:
        return "help"

    def execute(self, context, *args, **kwargs):
        if args:
            cmd_name = args[0]
            cmd = self.commands.get(cmd_name) or self.robot_commands.get(cmd_name)
            if cmd:
                print(cmd.help())
            else:
                print(f"Command '{cmd_name}' not found.")
        else:
            print("Available commands:")
            for cmd in self.commands.values():
                print(f"- {cmd.name()}: {cmd.help()}")
            print("Robot commands:") 
            for cmd in self.robot_commands.values():
                print(f"- {cmd.name()}: {cmd.help()}")

    def help(self) -> str:
        return "Shows help for available commands or a specific one."
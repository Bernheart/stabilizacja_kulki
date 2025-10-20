from lib.commands.command import Command
from lib.managers.command_context import CommandContext


class QuitCommand(Command):
    def name(self) -> str:
        return "quit"

    def execute(self, context: CommandContext, *args, **kwargs):
        print("Exiting program...")
        context.running = False

    def help(self) -> str:
        return "Exits the program."
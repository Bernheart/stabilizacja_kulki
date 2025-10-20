from lib.commands.command import Command
from lib.managers.command_context import CommandContext


class StatusCommand(Command):
    def name(self) -> str:
        return "status"

    def execute(self, context: CommandContext, *args, **kwargs):
        print(f"Status: {context.status_message}")

    def help(self) -> str:
        return "Displays the current system status."
from lib.commands.command import Command
from lib.managers.command_context import CommandContext


class HistoryCommand(Command):
    def name(self) -> str:
        return "history"

    def execute(self, context: CommandContext, *args, **kwargs):
        if not context.history:
            print("No commands executed yet.")
        else:
            print("Command history:")
            for i, entry in enumerate(context.history, 1):
                print(f"{i}. {entry}")

    def help(self) -> str:
        return "Displays the list of previously executed commands."
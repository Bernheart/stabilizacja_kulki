from lib.commands.command import Command
from lib.managers.command_context import CommandContext


class SaveLogCommand(Command):
    def name(self) -> str:
        return "savelog"

    def execute(self, context: CommandContext, *args, **kwargs):
        filename = args[0] if args else "command_log.txt"
        with open(filename, "w") as f:
            for entry in context.history:
                f.write(entry + "\n")
        print(f"Command history saved to {filename}")

    def help(self) -> str:
        return "Saves the command history to a file. Usage: savelog [filename]"
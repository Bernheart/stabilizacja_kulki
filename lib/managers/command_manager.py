import readline
from lib.commands.terminal_commands.help_commend import HelpCommand
from lib.commands.terminal_commands.history_commend import HistoryCommand
from lib.commands.terminal_commands.quit_commend import QuitCommand
from lib.commands.terminal_commands.save_log_commend import SaveLogCommand
from lib.commands.terminal_commands.status_commend import StatusCommand
from lib.managers.command_context import CommandContext

# --- Robot-related imports ---
from lib.commands.command import Command
from lib.commands.robot_commands.beem_sonar import BeemSonar
from lib.commands.robot_commands.infrared_sensor import InfraredSensor
from lib.commands.robot_commands.move_robot import MoveRobot
from lib.commands.robot_commands.rotate_robot import RotateRobot
from lib.commands.robot_commands.set_robot_velocity import SetRobotVelocity
from lib.commands.robot_commands.stop_robot import StopRobot
from lib.managers.robot_context import RobotContext


class CommandManager:
    def __init__(self, robot_context: RobotContext):
        # --- Contexts ---
        self.context = CommandContext()
        self.robot_context = robot_context

        # --- Dictionaries for commands ---
        self.commands: dict[str, Command] = {}
        self.robot_commands: dict[str, Command] = {}

        # --- Register terminal commands ---
        for cmd in [HelpCommand(self.commands, self.robot_commands), StatusCommand(),
                    HistoryCommand(), SaveLogCommand(), QuitCommand()]:
            self.commands[cmd.name()] = cmd

        # --- Register robot commands ---
        for cmd in [MoveRobot(), RotateRobot(), SetRobotVelocity(),
                    StopRobot(), BeemSonar(), InfraredSensor()]:
            self.robot_commands[cmd.name()] = cmd

        # --- Combine all command names for autocompletion ---
        self.all_command_names = list(self.commands.keys()) + list(self.robot_commands.keys())

        # --- Configure readline depending on backend ---
        if 'libedit' in readline.__doc__:
            # macOS (libedit)
            readline.parse_and_bind("bind ^I rl_complete")
        else:
            # Linux / GNU readline
            readline.parse_and_bind("tab: complete")

        readline.set_completer(self.completer)
        readline.set_completer_delims(" \t\n")
        readline.parse_and_bind('"\\e[A": history-search-backward')  # ↑
        readline.parse_and_bind('"\\e[B": history-search-forward')   # ↓

    # ---- Autocomplete ----
    def completer(self, text, state):
        """Autocomplete both terminal and robot commands."""
        options = [cmd for cmd in self.all_command_names if cmd.startswith(text)]
        if state < len(options):
            return options[state]
        return None

    # ---- Main loop ----
    def run(self):
        print("Command system ready. Type 'help' for available commands.")
        while self.context.running:
            try:
                user_input = input("> ").strip()
                if not user_input:
                    continue

                self.context.history.append(user_input)
                readline.add_history(user_input)

                parts = user_input.split()
                cmd_name, args = parts[0], parts[1:]

                # --- Check in terminal commands ---
                if cmd_name in self.commands:
                    cmd = self.commands[cmd_name]
                    cmd.execute(self.context, *args)

                # --- Check in robot commands ---
                elif cmd_name in self.robot_commands:
                    cmd = self.robot_commands[cmd_name]
                    cmd.execute(self.robot_context, *args)

                else:
                    print(f"Unknown command: {cmd_name}. Type 'help' for available commands.")

            except (EOFError, KeyboardInterrupt):
                print("\nExiting...")
                break
            except Exception as e:
                print(f"Error: {e}")
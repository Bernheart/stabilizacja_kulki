try:
    import readline
except ImportError:
    import pyreadline3 as readline

import sys
from threading import Thread, Event

from lib.commands.terminal_commands.help_commend import HelpCommand
from lib.commands.terminal_commands.history_commend import HistoryCommand
from lib.commands.terminal_commands.quit_commend import QuitCommand
from lib.commands.terminal_commands.save_log_commend import SaveLogCommand
from lib.commands.terminal_commands.status_commend import StatusCommand
from lib.managers.command_context import CommandContext
from lib.managers.device_context import DeviceContext
from lib.commands.command import Command

# --- New Balancer-related imports ---
from lib.commands.balancer_commands.set_target import SetTargetCommand
from lib.commands.balancer_commands.set_pid import SetPidCommand
from lib.commands.balancer_commands.set_zero import SetZeroCommand
from lib.commands.balancer_commands.test_mode import TestModeCommand
from lib.commands.balancer_commands.run_mode import RunModeCommand
from lib.commands.balancer_commands.stop import StopCommand


class CommandManager:
    def __init__(self, device_context: DeviceContext):
        self.context = CommandContext()
        self.device_context = device_context
        self.commands: dict[str, Command] = {}
        self.device_commands: dict[str, Command] = {}

        # Telemetry thread management
        self.telemetry_thread: Thread | None = None
        self.stop_event = Event()

        # --- Register terminal commands ---
        term_cmds = [HelpCommand(self.commands, self.device_commands), StatusCommand(),
                     HistoryCommand(), SaveLogCommand(), QuitCommand()]
        for cmd in term_cmds:
            self.commands[cmd.name()] = cmd

        # --- Register device commands ---
        # We pass 'self' (the manager) to commands that need to control the listener thread
        dev_cmds = [SetTargetCommand(), SetPidCommand(), SetZeroCommand(),
                    TestModeCommand(self), RunModeCommand(self), StopCommand(self)]
        for cmd in dev_cmds:
            self.device_commands[cmd.name()] = cmd

        # --- Combine all command names for autocompletion ---
        self.all_command_names = list(self.commands.keys()) + list(self.device_commands.keys())
        self._configure_readline()

    def _configure_readline(self):
        if 'libedit' in readline.__doc__: # macOS
            readline.parse_and_bind("bind ^I rl_complete")
        else: # Linux
            readline.parse_and_bind("tab: complete")
        readline.set_completer(self.completer)
        readline.set_completer_delims(" \t\n")

    def completer(self, text, state):
        options = [cmd for cmd in self.all_command_names if cmd.startswith(text)]
        return options[state] if state < len(options) else None

    # ---- Thread Management ----
    
    def start_listener_thread(self):
        """Starts the telemetry listener thread if not already running."""
        if self.telemetry_thread and self.telemetry_thread.is_alive():
            return 
        self.stop_event.clear()
        self.telemetry_thread = Thread(
            target=self.device_context.comm.listen_for_data,
            args=(self.stop_event,),
            daemon=True
        )
        self.telemetry_thread.start()

    def stop_listener_thread(self):
        """Stops the telemetry listener thread."""
        if self.telemetry_thread and self.telemetry_thread.is_alive():
            self.stop_event.set()
            self.telemetry_thread.join(timeout=1.0)
        self.telemetry_thread = None
        self.stop_event.clear()

    def cleanup(self):
        """Stops all device activity and threads before exit."""
        print("[INFO] Cleaning up resources...")
        self.stop_listener_thread()
        # Send a final stop command to make sure
        try:
            self.device_context.comm.send_command("D", 0)
        except Exception:
            pass # Ignore errors on exit

    # ---- Main loop ----
    
    def run(self):
        print("Ball Balancer Interface. Type 'help' for commands.")
        # Start a general listener thread for any spontaneous <INFO> messages
        # self.start_listener_thread() 
        # Note: Disabled for this project, as Arduino only talks after a command.

        while self.context.running:
            try:
                user_input = input("> ").strip()
                if not user_input:
                    # Pressing Enter on an empty line is the signal to stop TEST mode
                    if self.telemetry_thread and self.telemetry_thread.is_alive():
                        print("[INFO] Stopping test mode...")
                        self.stop_listener_thread()
                        # Send stop command to Arduino
                        self.device_context.comm.send_command("D", 0)
                    continue

                self.context.history.append(user_input)
                readline.add_history(user_input)

                parts = user_input.split()
                cmd_name, args = parts[0], parts[1:]

                if cmd_name in self.commands:
                    self.commands[cmd_name].execute(self.context, *args)
                elif cmd_name in self.device_commands:
                    self.device_commands[cmd_name].execute(self.device_context, *args)
                else:
                    print(f"Unknown command: {cmd_name}. Type 'help' for commands.")

            except (EOFError, KeyboardInterrupt):
                self.context.running = False
            except Exception as e:
                print(f"[ERROR] Main loop: {e}")
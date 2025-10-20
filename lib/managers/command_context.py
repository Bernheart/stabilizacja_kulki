class CommandContext:
    """Holds shared state for commands."""
    def __init__(self):
        self.history = []
        self.running = True
        self.status_message = "System initialized."
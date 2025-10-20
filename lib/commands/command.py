from abc import ABC, abstractmethod

class Command(ABC):
    """Abstract base class for all commands."""

    @abstractmethod
    def name(self) -> str:
        """Return the name of the command."""
        pass

    @abstractmethod
    def execute(self, context, *args, **kwargs):
        """Execute the command logic."""
        pass

    def help(self) -> str:
        """Optional method: return help text for this command."""
        return f"No help available for '{self.name()}'."
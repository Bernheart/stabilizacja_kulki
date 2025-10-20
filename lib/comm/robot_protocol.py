class RobotProtocol:
    @staticmethod
    def build_frame(cmd: str, params=None) -> str:
        """
        Build a communication frame for Arduino.
        Format: <CMD|PARAM|CHECKSUM>
        Example: "<M|50|167>"
        """
        # Build core content
        if params is None:
            content = cmd
        elif isinstance(params, (list, tuple)):
            content = f"{cmd}|{'|'.join(map(str, params))}"
        else:
            content = f"{cmd}|{params}"

        # Compute checksum = sum of ASCII codes % 256
        checksum = sum(ord(c) for c in content) % 256

        # Full frame with delimiters
        frame = f"<{content}|{checksum}>"
        return frame
from lib.comm.device_comm import DeviceComm

class DeviceContext:
    """Holds the shared communication object for the device."""
    def __init__(self, port, baudrate, timeout=1):
        try:
            self.comm = DeviceComm(port, baudrate, timeout=timeout)
        except Exception as e:
            print(f"[CRITICAL] Failed to initialize DeviceComm: {e}")
            raise
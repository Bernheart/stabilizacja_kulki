import time
from lib.comm.robot_comm import RobotComm


class RobotContext:
    def __init__(self, port, baudrate):
        self.comm = RobotComm(port, baudrate)
        self.running = True
        self.stop_flag = False
        self.automatic_mode = False
        self.speed = 0
        self.sensors = {"sonar": None, "ir": None}


from lib.commands.command import Command
from lib.commands.robot_commands.beem_sonar import BeemSonar
from lib.commands.robot_commands.infrared_sensor import InfraredSensor
from lib.commands.robot_commands.move_robot import MoveRobot
from lib.commands.robot_commands.rotate_robot import RotateRobot
from lib.commands.robot_commands.set_robot_velocity import SetRobotVelocity
from lib.commands.robot_commands.stop_robot import StopRobot
from lib.managers.robot_context import RobotContext


class RobotManager:
    def __init__(self):
        self.context = RobotContext()
        self.commands: dict[str, Command] = {}

        # Register commands
        for cmd in [MoveRobot(), RotateRobot(), SetRobotVelocity(), 
                    StopRobot(), BeemSonar(), InfraredSensor()]:
            self.commands[cmd.name()] = cmd
            
    def execute(self, cmd_name, *args):
        self.commands[cmd_name].execute(self.context, args)
        
            

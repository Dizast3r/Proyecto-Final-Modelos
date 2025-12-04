"""
COMMAND PATTERN - Para el movimiento del personaje
Define una interfaz común para todos los comandos de movimiento
"""

from abc import ABC, abstractmethod

class Command(ABC):
    """Interfaz base para todos los comandos"""
    
    @abstractmethod
    def execute(self, player):
        pass


class MoveLeftCommand(Command):
    """Comando para mover el personaje a la izquierda"""
    
    def execute(self, player):
        player.move_left()


class MoveRightCommand(Command):
    """Comando para mover el personaje a la derecha"""
    
    def execute(self, player):
        player.move_right()


class JumpCommand(Command):
    """Comando para hacer saltar al personaje"""
    
    def execute(self, player):
        player.jump()


class StopCommand(Command):
    """Comando para detener el movimiento horizontal"""
    
    def execute(self, player):
        player.stop()


class InputHandler:
    """Maneja la entrada del usuario y ejecuta comandos"""
    
    def __init__(self):
        self.move_left = MoveLeftCommand()
        self.move_right = MoveRightCommand()
        self.jump = JumpCommand()
        self.stop = StopCommand()
    
    def handle_input(self, keys, player):
        """Procesa las teclas presionadas y ejecuta comandos"""
        import pygame
        
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.move_left.execute(player)
        elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.move_right.execute(player)
        else:
            self.stop.execute(player)
        
        if keys[pygame.K_SPACE] or keys[pygame.K_UP] or keys[pygame.K_w]:
            self.jump.execute(player)
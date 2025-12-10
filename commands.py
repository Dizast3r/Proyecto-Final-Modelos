"""
Patron de Diseno Command:
Encapsula una solicitud (accion del jugador) como un objeto, permitiendo
parametrizar a los clientes con diferentes solicitudes, encolar o registrar
solicitudes y soportar operaciones que pueden deshacerse.
"""

from abc import ABC, abstractmethod

class Command(ABC):
    """
    Interfaz Command:
    Declara el metodo para ejecutar una operacion.
    Todas las acciones concretas del jugador deben implementar esta interfaz.
    """
    
    @abstractmethod
    def execute(self, player):
        """Metodo abstracto que ejecuta la accion sobre el receptor (player)."""
        pass


class MoveLeftCommand(Command):
    """
    Comando Concreto:
    Implementa la accion de mover hacia la izquierda delegando en el receptor.
    """
    
    def execute(self, player):
        player.move_left()


class MoveRightCommand(Command):
    """
    Comando Concreto:
    Implementa la accion de mover hacia la derecha delegando en el receptor.
    """
    
    def execute(self, player):
        player.move_right()


class JumpCommand(Command):
    """
    Comando Concreto:
    Implementa la accion de saltar delegando en el receptor.
    """
    
    def execute(self, player):
        player.jump()


class StopCommand(Command):
    """
    Comando Concreto:
    Implementa la accion de detener el movimiento horizontal.
    """
    
    def execute(self, player):
        player.stop()


class InputHandler:
    """
    Invoker / Cliente:
    Mapea las entradas del usuario (teclas) a comandos especificos y solicita
    su ejecucion. Desacopla la logica de entrada de la logica de negocio.
    """
    
    def __init__(self):
        self.move_left = MoveLeftCommand()
        self.move_right = MoveRightCommand()
        self.jump = JumpCommand()
        self.stop = StopCommand()
    
    def handle_input(self, keys, player):
        """
        Determina que comando ejecutar en funcion de las teclas presionadas
        y ejecuta el comando correspondiente pasando el receptor (player).
        """
        import pygame
        
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.move_left.execute(player)
        elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.move_right.execute(player)
        else:
            self.stop.execute(player)
        
        if keys[pygame.K_SPACE] or keys[pygame.K_UP] or keys[pygame.K_w]:
            self.jump.execute(player)
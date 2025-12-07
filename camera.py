"""
Sistema de cámara - Maneja el seguimiento del jugador
"""


class Camera:
    """Maneja la cámara que sigue al jugador"""
    
    def __init__(self, screen_width, world_width):
        self.x = 0
        self.screen_width = screen_width
        self.world_width = world_width
    
    def update(self, player_x, player_width):
        """Actualiza la posición de la cámara siguiendo al jugador"""
        # Centrar cámara en el jugador
        self.x = player_x - self.screen_width // 2
        
        # Limitar la cámara para que no salga de los bordes del mundo
        if self.x < 0:
            self.x = 0
        elif self.x > self.world_width - self.screen_width:
            self.x = self.world_width - self.screen_width
    
    def get_x(self):
        """Retorna la posición X de la cámara"""
        return self.x
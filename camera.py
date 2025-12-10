"""
Sistema de Camara.
Gestiona el viewport del juego, siguiendo al jugador horizontalmente(scrolling).
"""


class Camera:
    """Implementa una camara 2D con seguimiento horizontal."""
    
    def __init__(self, screen_width, world_width):
        self.x = 0
        self.screen_width = screen_width
        self.world_width = world_width
    
    def update(self, player_x, player_width):
        """Calcula la posicion de la camara para mantener al jugador centrado."""
        # Centrar camara en el jugador
        self.x = player_x - self.screen_width // 2
        
        # Limitar la camara para que no salga de los bordes del mundo
        if self.x < 0:
            self.x = 0
        elif self.x > self.world_width - self.screen_width:
            self.x = self.world_width - self.screen_width
    
    def get_x(self):
        """Retorna el offset actual en X."""
        return self.x

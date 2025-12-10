"""
Renderizador de UI.
Maneja el dibujado de la interfaz de usuario superpuesta (HUD).
"""

import pygame


class UIRenderer:
    """Clase encargada de dibujar elementos de UI (vidas, nombre del mundo)."""
    
    def __init__(self, screen):
        self.screen = screen
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
    
    def draw_ui(self, world_name, player_lives):
        """Metodo principal para renderizar el HUD."""
        self._draw_world_name(world_name)
        self._draw_lives(player_lives)
    
    def _draw_world_name(self, world_name):
        """Renderiza el nombre del nivel actual."""
        world_text = self.font.render(world_name, True, (0, 0, 0))
        self.screen.blit(world_text, (10, 10))
    
    def _draw_lives(self, lives):
        """Renderiza el contador de vidas."""
        lives_text = self.small_font.render(f"Vidas: {lives}", True, (255, 0, 0))
        self.screen.blit(lives_text, (10, 50))

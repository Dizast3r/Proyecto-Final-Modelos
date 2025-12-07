"""
Renderizador de UI - Maneja el dibujado de la interfaz de usuario
"""

import pygame


class UIRenderer:
    """Renderiza la interfaz de usuario del juego"""
    
    def __init__(self, screen):
        self.screen = screen
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
    
    def draw_ui(self, world_name, player_lives):
        """Dibuja todos los elementos de UI"""
        self._draw_world_name(world_name)
        self._draw_lives(player_lives)
        self._draw_instructions()
    
    def _draw_world_name(self, world_name):
        """Dibuja el nombre del mundo"""
        world_text = self.font.render(world_name, True, (0, 0, 0))
        self.screen.blit(world_text, (10, 10))
    
    def _draw_lives(self, lives):
        """Dibuja las vidas del jugador"""
        lives_text = self.small_font.render(f"Vidas: {lives}", True, (255, 0, 0))
        self.screen.blit(lives_text, (10, 50))
    
    def _draw_instructions(self):
        """Dibuja las instrucciones del juego"""
        instructions = [
            "Flechas/WASD: Mover",
            "Espacio/Arriba: Saltar",
            "ESC: Salir",
            "1/2/3: Cambiar mundo"
        ]
        y_offset = 80
        for instruction in instructions:
            text = self.small_font.render(instruction, True, (0, 0, 0))
            self.screen.blit(text, (10, y_offset))
            y_offset += 25
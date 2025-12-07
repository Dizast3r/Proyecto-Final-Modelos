"""
Sistema de Menús del Juego
Maneja todos los estados de UI: menú principal, completar nivel, game over, etc.
"""

import pygame
from enum import Enum
from typing import Optional, Callable


class GameState(Enum):
    """Estados del juego"""
    MAIN_MENU = "main_menu"
    PLAYING = "playing"
    LEVEL_COMPLETE = "level_complete"
    GAME_COMPLETE = "game_complete"
    GAME_OVER = "game_over"


class Button:
    """Clase para botones interactivos"""
    
    def __init__(self, x: int, y: int, width: int, height: int, 
                 text: str, color: tuple, hover_color: tuple, 
                 text_color: tuple = (255, 255, 255)):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.text_color = text_color
        self.is_hovered = False
    
    def draw(self, screen: pygame.Surface, font: pygame.font.Font):
        """Dibuja el botón"""
        # Color según hover
        current_color = self.hover_color if self.is_hovered else self.color
        
        # Dibujar botón con sombra
        shadow_rect = self.rect.copy()
        shadow_rect.x += 4
        shadow_rect.y += 4
        pygame.draw.rect(screen, (0, 0, 0), shadow_rect, border_radius=10)
        
        # Botón principal
        pygame.draw.rect(screen, current_color, self.rect, border_radius=10)
        
        # Borde
        border_color = (255, 255, 255) if self.is_hovered else (200, 200, 200)
        pygame.draw.rect(screen, border_color, self.rect, 3, border_radius=10)
        
        # Texto
        text_surface = font.render(self.text, True, self.text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)
    
    def check_hover(self, mouse_pos: tuple):
        """Verifica si el mouse está sobre el botón"""
        self.is_hovered = self.rect.collidepoint(mouse_pos)
    
    def is_clicked(self, mouse_pos: tuple, mouse_clicked: bool) -> bool:
        """Verifica si el botón fue clickeado"""
        return self.rect.collidepoint(mouse_pos) and mouse_clicked


class MenuManager:
    """Gestor central de menús"""
    
    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self.screen_width = screen.get_width()
        self.screen_height = screen.get_height()
        
        # Fuentes
        self.title_font = pygame.font.Font(None, 80)
        self.subtitle_font = pygame.font.Font(None, 50)
        self.button_font = pygame.font.Font(None, 40)
        self.text_font = pygame.font.Font(None, 30)
        
        # Estado actual
        self.current_state = GameState.MAIN_MENU
        
        # Callbacks (se asignan desde Game)
        self.on_start_game: Optional[Callable] = None
        self.on_next_level: Optional[Callable] = None
        self.on_restart_game: Optional[Callable] = None
        self.on_quit: Optional[Callable] = None
        
        # Crear botones para cada menú
        self._create_buttons()
    
    def _create_buttons(self):
        """Crea todos los botones de los menús"""
        center_x = self.screen_width // 2
        
        # === MAIN MENU ===
        self.main_menu_buttons = {
            'play': Button(
                center_x - 150, 300, 300, 70,
                "JUGAR", (34, 139, 34), (50, 205, 50)
            ),
            'quit': Button(
                center_x - 150, 400, 300, 70,
                "SALIR", (178, 34, 34), (220, 20, 60)
            )
        }
        
        # === LEVEL COMPLETE MENU ===
        self.level_complete_buttons = {
            'next': Button(
                center_x - 150, 320, 300, 70,
                "SIGUIENTE MUNDO", (34, 139, 34), (50, 205, 50)
            ),
            'quit': Button(
                center_x - 150, 420, 300, 70,
                "SALIR", (178, 34, 34), (220, 20, 60)
            )
        }
        
        # === GAME COMPLETE MENU ===
        self.game_complete_buttons = {
            'new_game': Button(
                center_x - 150, 320, 300, 70,
                "NUEVO JUEGO", (34, 139, 34), (50, 205, 50)
            ),
            'quit': Button(
                center_x - 150, 420, 300, 70,
                "SALIR", (178, 34, 34), (220, 20, 60)
            )
        }
        
        # === GAME OVER MENU ===
        self.game_over_buttons = {
            'retry': Button(
                center_x - 150, 320, 300, 70,
                "REINTENTAR", (255, 165, 0), (255, 200, 50)
            ),
            'quit': Button(
                center_x - 150, 420, 300, 70,
                "SALIR", (178, 34, 34), (220, 20, 60)
            )
        }
    
    def draw_background_overlay(self, alpha: int = 180):
        """Dibuja un overlay semi-transparente"""
        overlay = pygame.Surface((self.screen_width, self.screen_height))
        overlay.set_alpha(alpha)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))
    
    def draw_title(self, text: str, y: int, color: tuple = (255, 215, 0)):
        """Dibuja un título centrado"""
        title_surface = self.title_font.render(text, True, color)
        title_rect = title_surface.get_rect(center=(self.screen_width // 2, y))
        
        # Sombra
        shadow_surface = self.title_font.render(text, True, (0, 0, 0))
        shadow_rect = shadow_surface.get_rect(center=(self.screen_width // 2 + 3, y + 3))
        self.screen.blit(shadow_surface, shadow_rect)
        
        # Título
        self.screen.blit(title_surface, title_rect)
    
    def draw_subtitle(self, text: str, y: int, color: tuple = (255, 255, 255)):
        """Dibuja un subtítulo centrado"""
        subtitle_surface = self.subtitle_font.render(text, True, color)
        subtitle_rect = subtitle_surface.get_rect(center=(self.screen_width // 2, y))
        self.screen.blit(subtitle_surface, subtitle_rect)
    
    # ========================================================================
    # MAIN MENU
    # ========================================================================
    
    def draw_main_menu(self):
        """Dibuja el menú principal"""
        # Fondo degradado
        for i in range(self.screen_height):
            color_value = int(135 - (i / self.screen_height) * 100)
            pygame.draw.line(
                self.screen, 
                (color_value, color_value + 50, color_value + 100),
                (0, i), (self.screen_width, i)
            )
        
        # Título
        self.draw_title("SUPER KIRBY BRO", 120)
        
        # Subtítulo
        subtitle_text = self.text_font.render(
            "Proyecto Final - Patrones de Diseño", 
            True, (200, 200, 200)
        )
        subtitle_rect = subtitle_text.get_rect(center=(self.screen_width // 2, 200))
        self.screen.blit(subtitle_text, subtitle_rect)
        
        # Botones
        mouse_pos = pygame.mouse.get_pos()
        for button in self.main_menu_buttons.values():
            button.check_hover(mouse_pos)
            button.draw(self.screen, self.button_font)
        
        # Instrucciones
        instructions = [
            "Controles: ← → / A D - Mover",
            "Espacio / ↑ / W - Saltar",
            "ESC - Pausar"
        ]
        y_offset = 520
        for instruction in instructions:
            text = self.text_font.render(instruction, True, (200, 200, 200))
            text_rect = text.get_rect(center=(self.screen_width // 2, y_offset))
            self.screen.blit(text, text_rect)
            y_offset += 30
    
    def handle_main_menu_click(self, mouse_pos: tuple, mouse_clicked: bool):
        """Maneja clicks en el menú principal"""
        if self.main_menu_buttons['play'].is_clicked(mouse_pos, mouse_clicked):
            if self.on_start_game:
                self.on_start_game()
                self.current_state = GameState.PLAYING
        
        elif self.main_menu_buttons['quit'].is_clicked(mouse_pos, mouse_clicked):
            if self.on_quit:
                self.on_quit()
    
    # ========================================================================
    # LEVEL COMPLETE MENU
    # ========================================================================
    
    def draw_level_complete_menu(self, world_name: str):
        """Dibuja el menú de nivel completado"""
        self.draw_background_overlay(200)
        
        # Panel central
        panel_width = 600
        panel_height = 400
        panel_x = (self.screen_width - panel_width) // 2
        panel_y = (self.screen_height - panel_height) // 2
        
        # Sombra del panel
        shadow_rect = pygame.Rect(panel_x + 5, panel_y + 5, panel_width, panel_height)
        pygame.draw.rect(self.screen, (0, 0, 0), shadow_rect, border_radius=20)
        
        # Panel principal
        panel_rect = pygame.Rect(panel_x, panel_y, panel_width, panel_height)
        pygame.draw.rect(self.screen, (34, 139, 34), panel_rect, border_radius=20)
        pygame.draw.rect(self.screen, (255, 215, 0), panel_rect, 5, border_radius=20)
        
        # Título
        self.draw_title("¡FELICIDADES!", panel_y + 60)
        
        # Subtítulo
        subtitle_text = f"Completaste: {world_name}"
        self.draw_subtitle(subtitle_text, panel_y + 150, (255, 255, 255))
        
        # Botones
        mouse_pos = pygame.mouse.get_pos()
        for button in self.level_complete_buttons.values():
            button.check_hover(mouse_pos)
            button.draw(self.screen, self.button_font)
    
    def handle_level_complete_click(self, mouse_pos: tuple, mouse_clicked: bool):
        """Maneja clicks en el menú de nivel completado"""
        if self.level_complete_buttons['next'].is_clicked(mouse_pos, mouse_clicked):
            if self.on_next_level:
                self.on_next_level()
                self.current_state = GameState.PLAYING
        
        elif self.level_complete_buttons['quit'].is_clicked(mouse_pos, mouse_clicked):
            if self.on_quit:
                self.on_quit()
    
    # ========================================================================
    # GAME COMPLETE MENU
    # ========================================================================
    
    def draw_game_complete_menu(self):
        """Dibuja el menú de juego completado"""
        self.draw_background_overlay(200)
        
        # Panel central más grande
        panel_width = 700
        panel_height = 450
        panel_x = (self.screen_width - panel_width) // 2
        panel_y = (self.screen_height - panel_height) // 2
        
        # Sombra del panel
        shadow_rect = pygame.Rect(panel_x + 5, panel_y + 5, panel_width, panel_height)
        pygame.draw.rect(self.screen, (0, 0, 0), shadow_rect, border_radius=20)
        
        # Panel principal (dorado)
        panel_rect = pygame.Rect(panel_x, panel_y, panel_width, panel_height)
        pygame.draw.rect(self.screen, (184, 134, 11), panel_rect, border_radius=20)
        pygame.draw.rect(self.screen, (255, 215, 0), panel_rect, 5, border_radius=20)
        
        # Título
        self.draw_title("¡VICTORIA!", panel_y + 50)
        
        # Mensajes
        messages = [
            "¡Completaste todos los mundos!",
            "Eres un verdadero héroe",
            "🏆 JUEGO COMPLETADO 🏆"
        ]
        y_offset = panel_y + 140
        for msg in messages:
            text = self.subtitle_font.render(msg, True, (255, 255, 255))
            text_rect = text.get_rect(center=(self.screen_width // 2, y_offset))
            self.screen.blit(text, text_rect)
            y_offset += 45
        
        # Botones
        mouse_pos = pygame.mouse.get_pos()
        for button in self.game_complete_buttons.values():
            button.check_hover(mouse_pos)
            button.draw(self.screen, self.button_font)
    
    def handle_game_complete_click(self, mouse_pos: tuple, mouse_clicked: bool):
        """Maneja clicks en el menú de juego completado"""
        if self.game_complete_buttons['new_game'].is_clicked(mouse_pos, mouse_clicked):
            if self.on_restart_game:
                self.on_restart_game()
                self.current_state = GameState.PLAYING
        
        elif self.game_complete_buttons['quit'].is_clicked(mouse_pos, mouse_clicked):
            if self.on_quit:
                self.on_quit()
    
    # ========================================================================
    # GAME OVER MENU
    # ========================================================================
    
    def draw_game_over_menu(self):
        """Dibuja el menú de game over"""
        self.draw_background_overlay(200)
        
        # Panel central
        panel_width = 600
        panel_height = 400
        panel_x = (self.screen_width - panel_width) // 2
        panel_y = (self.screen_height - panel_height) // 2
        
        # Sombra del panel
        shadow_rect = pygame.Rect(panel_x + 5, panel_y + 5, panel_width, panel_height)
        pygame.draw.rect(self.screen, (0, 0, 0), shadow_rect, border_radius=20)
        
        # Panel principal (rojo oscuro)
        panel_rect = pygame.Rect(panel_x, panel_y, panel_width, panel_height)
        pygame.draw.rect(self.screen, (139, 0, 0), panel_rect, border_radius=20)
        pygame.draw.rect(self.screen, (220, 20, 60), panel_rect, 5, border_radius=20)
        
        # Título
        self.draw_title("GAME OVER", panel_y + 60, (255, 69, 0))
        
        # Mensaje
        message = "¡Sigue intentando!"
        self.draw_subtitle(message, panel_y + 150, (255, 255, 255))
        
        # Botones
        mouse_pos = pygame.mouse.get_pos()
        for button in self.game_over_buttons.values():
            button.check_hover(mouse_pos)
            button.draw(self.screen, self.button_font)
    
    def handle_game_over_click(self, mouse_pos: tuple, mouse_clicked: bool):
        """Maneja clicks en el menú de game over"""
        if self.game_over_buttons['retry'].is_clicked(mouse_pos, mouse_clicked):
            if self.on_restart_game:
                self.on_restart_game()
                self.current_state = GameState.PLAYING
        
        elif self.game_over_buttons['quit'].is_clicked(mouse_pos, mouse_clicked):
            if self.on_quit:
                self.on_quit()
    
    # ========================================================================
    # MÉTODO PRINCIPAL DE RENDERIZADO
    # ========================================================================
    
    def draw_current_menu(self, world_name: str = ""):
        """Dibuja el menú actual según el estado"""
        if self.current_state == GameState.MAIN_MENU:
            self.draw_main_menu()
        elif self.current_state == GameState.LEVEL_COMPLETE:
            self.draw_level_complete_menu(world_name)
        elif self.current_state == GameState.GAME_COMPLETE:
            self.draw_game_complete_menu()
        elif self.current_state == GameState.GAME_OVER:
            self.draw_game_over_menu()
    
    def handle_click(self, mouse_pos: tuple, mouse_clicked: bool):
        """Maneja clicks según el estado actual"""
        if self.current_state == GameState.MAIN_MENU:
            self.handle_main_menu_click(mouse_pos, mouse_clicked)
        elif self.current_state == GameState.LEVEL_COMPLETE:
            self.handle_level_complete_click(mouse_pos, mouse_clicked)
        elif self.current_state == GameState.GAME_COMPLETE:
            self.handle_game_complete_click(mouse_pos, mouse_clicked)
        elif self.current_state == GameState.GAME_OVER:
            self.handle_game_over_click(mouse_pos, mouse_clicked)
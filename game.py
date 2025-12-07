"""
Clase Game refactorizada - Ahora es una fachada simple que coordina componentes
"""

import pygame
from config import GameConfig
from entities import Player
from commands import InputHandler
from memento import CheckpointManager
from game_events import (
    GameEventManager, 
    ConsoleLogger, 
    GameOverChecker, 
    CheckpointSaver,
    GameEvent,
    GameEventType
)
from collision_manager import CollisionManager
from camera import Camera
from ui_renderer import UIRenderer
from world_loader import WorldLoader
from audio_manager import play_world_music


class Game:
    """
    Clase principal del juego - REFACTORIZADA
    Ahora actúa como Facade que coordina componentes especializados
    """
    
    def __init__(self, width=None, height=None, world_width=None):
        # Configuración
        self.width = width or GameConfig.DEFAULT_WIDTH
        self.height = height or GameConfig.DEFAULT_HEIGHT
        self.world_width = world_width or GameConfig.DEFAULT_WORLD_WIDTH
        
        # Inicializar Pygame
        pygame.init()
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption(GameConfig.WINDOW_TITLE)
        self.clock = pygame.time.Clock()
        self.running = True
        
        # Sistema de eventos (Observer Pattern)
        self.event_manager = GameEventManager()
        
        # Sistemas del juego
        self.input_handler = InputHandler()
        self.checkpoint_manager = CheckpointManager()
        self.player = Player(100, 100)
        self.camera = Camera(self.width, self.world_width)
        self.ui_renderer = UIRenderer(self.screen)
        self.world_loader = WorldLoader()
        self.collision_manager = CollisionManager(
            self.event_manager, 
            self.checkpoint_manager
        )
        
        # Registrar observadores
        self._setup_observers()
        
        print("🎮 Juego inicializado con Observer Pattern")
    
    def _setup_observers(self):
        """Configura los observadores del juego"""
        # Logger de consola
        console_logger = ConsoleLogger()
        self.event_manager.subscribe(console_logger)
        
        # Verificador de Game Over
        game_over_checker = GameOverChecker(self)
        self.event_manager.subscribe(game_over_checker)
        
        # Guardador de checkpoints
        self.checkpoint_saver = CheckpointSaver(self.checkpoint_manager)
        self.checkpoint_saver.set_game(self)  # Asignar referencia al juego
        self.event_manager.subscribe(self.checkpoint_saver)
    
    def load_world(self, world_data):
        """Carga un mundo - Delega al WorldLoader"""
        self.world_loader.load_world(world_data)
        
        # Reproducir música del mundo
        if self.world_loader.music_file:
            play_world_music(self.world_loader.music_file)
        
        # Resetear jugador y sistemas
        self.player = Player(100, 100)
        self.checkpoint_manager.clear_checkpoints()
        
        # Notificar evento de mundo cargado
        event = GameEvent(
            GameEventType.WORLD_LOADED,
            {'world_name': self.world_loader.world_name}
        )
        self.event_manager.notify(event)
    
    def update(self):
        """Actualiza la lógica del juego"""
        # Actualizar jugador
        platform_data = self.world_loader.get_platform_data()
        self.player.update(platform_data, self.world_width)
        
        # Actualizar enemigos
        for enemy in self.world_loader.enemies:
            enemy.update(
                platform_data,
                self.world_loader.spikes,
                self.world_loader.checkpoints,
                self.world_loader.goal,
                self.world_width
            )
        
        # Eliminar enemigos muertos
        self.world_loader.enemies = [
            e for e in self.world_loader.enemies 
            if not e.should_be_removed()
        ]
        
        # Eliminar PowerUps recolectados
        self.world_loader.powerups = [
            p for p in self.world_loader.powerups 
            if not p.collected
        ]
        
        # Verificar colisiones
        self.collision_manager.check_all_collisions(
            self.player,
            self.world_loader.checkpoints,
            self.world_loader.goal,
            self.world_loader.enemies,
            self.world_loader.powerups,
            self.world_loader.spikes,
            self.world_loader.world_name
        )
        
        # Actualizar cámara
        self.camera.update(self.player.x, self.player.width)
    
    def draw(self):
        """Dibuja todos los elementos del juego"""
        # Fondo (cielo)
        sky_color = self.world_loader.colors.get('sky', (135, 206, 235))
        self.screen.fill(sky_color)
        
        camera_x = self.camera.get_x()
        
        # Dibujar plataformas
        for platform in self.world_loader.platforms:
            platform.draw(self.screen, camera_x)
        
        # Dibujar espinas
        for spike in self.world_loader.spikes:
            spike.draw(self.screen, camera_x)
        
        # Dibujar PowerUps
        for powerup in self.world_loader.powerups:
            powerup.draw(self.screen, camera_x)
        
        # Dibujar checkpoints
        for checkpoint in self.world_loader.checkpoints:
            checkpoint.draw(self.screen, camera_x)
        
        # Dibujar enemigos
        for enemy in self.world_loader.enemies:
            enemy.draw(self.screen, camera_x)
        
        # Dibujar goal
        if self.world_loader.goal:
            self.world_loader.goal.draw(self.screen, camera_x)
        
        # Dibujar jugador
        self.player.draw(self.screen, camera_x)
        
        # Dibujar UI
        self.ui_renderer.draw_ui(
            self.world_loader.world_name,
            self.player.lives
        )
    
    def run(self):
        """Loop principal del juego"""
        while self.running:
            # Eventos
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.running = False
            
            # Input (Command Pattern)
            keys = pygame.key.get_pressed()
            self.input_handler.handle_input(keys, self.player)
            
            # Actualizar
            self.update()
            
            # Dibujar
            self.draw()
            
            # Actualizar pantalla
            pygame.display.flip()
            self.clock.tick(GameConfig.FPS)
        
        pygame.quit()
"""
Clase Game refactorizada - CON REGENERACIÓN DE MUNDOS
✅ NUEVO: Los mundos se regeneran en cada "Nuevo Juego"
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
    LevelCompleteChecker,
    CheckpointSaver,
    GameEvent,
    GameEventType
)
from collision_manager import CollisionManager
from camera import Camera
from ui_renderer import UIRenderer
from world_loader import WorldLoader
from audio_manager import play_world_music
from menu_system import MenuManager, GameState


class Game:
    """
    Clase principal del juego
    ✅ MODIFICADO: Ahora guarda los generadores y regenera mundos
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

        # ✨ Sistema de menús
        self.menu_manager = MenuManager(self.screen)
        self.setup_menu_callbacks()
        
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

        # ✅ NUEVO: Guardar generadores en vez de mundos pre-generados
        self.world_generators = []  # Lista de generadores
        self.world_sequence = []  # Mundos actuales generados
        self.current_world_index = -1
        
        # Registrar observadores
        self._setup_observers()
        
        print("🎮 Juego inicializado con Observer Pattern")
    
    def setup_menu_callbacks(self):
        """Configura los callbacks de los menús"""
        self.menu_manager.on_start_game = self.start_new_game
        self.menu_manager.on_next_level = self.load_next_world
        self.menu_manager.on_restart_game = self.restart_from_beginning
        self.menu_manager.on_quit = self.quit_game
    
    def _setup_observers(self):
        """Configura los observadores del juego"""
        console_logger = ConsoleLogger()
        self.event_manager.subscribe(console_logger)
        
        game_over_checker = GameOverChecker(self)
        self.event_manager.subscribe(game_over_checker)

        level_complete_checker = LevelCompleteChecker(self)
        self.event_manager.subscribe(level_complete_checker)
        
        self.checkpoint_saver = CheckpointSaver(self.checkpoint_manager)
        self.checkpoint_saver.set_game(self)
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
    
    def set_world_generators(self, generators: list):
        """
        ✅ Establece los GENERADORES de mundos (no los mundos)
        
        Args:
            generators: Lista de instancias de WorldGenerator
                       (ej: [GrassWorldGenerator(), DesertWorldGenerator(), ...])
        """
        self.world_generators = generators
        print(f"✅ {len(generators)} generadores configurados")
    
    def _regenerate_worlds(self):
        """
        ✅ NUEVO: Regenera todos los mundos usando los generadores
        """
        if not self.world_generators:
            print("❌ No hay generadores configurados, usando mundos existentes")
            return
        
        print("\n🔨 Regenerando mundos...")
        self.world_sequence = []
        
        for i, generator in enumerate(self.world_generators):
            print(f"   Generando mundo {i+1}/{len(self.world_generators)}...")
            world_data = generator.generate_world(self.world_width, self.height)
            self.world_sequence.append(world_data)
        
        print(f"✅ {len(self.world_sequence)} mundos regenerados\n")
    
    def start_new_game(self):
        """
        ✅ MODIFICADO: Regenera mundos antes de iniciar
        """
        print("\n🎮 Iniciando nuevo juego...")
        
        # ✅ Regenerar mundos si hay generadores
        if self.world_generators:
            self._regenerate_worlds()
        
        self.current_world_index = 0
        self.load_current_world()
    
    def load_next_world(self):
        """Carga el siguiente mundo en la secuencia"""
        if self.current_world_index < len(self.world_sequence) - 1:
            self.current_world_index += 1
            self.load_current_world()
            print(f"➡️ Avanzando a mundo {self.current_world_index + 1}")
        else:
            print("⚠️ No hay más mundos disponibles")
    
    def load_current_world(self):
        """Carga el mundo actual según current_world_index"""
        if 0 <= self.current_world_index < len(self.world_sequence):
            world_data = self.world_sequence[self.current_world_index]
            self.load_world(world_data)
        else:
            print("⚠️ Índice de mundo inválido")
    
    def restart_from_beginning(self):
        """
        ✅ MODIFICADO: Regenera mundos antes de reiniciar
        """
        print("\n🔄 Reiniciando juego...")
        
        # ✅ Regenerar mundos si hay generadores
        if self.world_generators:
            self._regenerate_worlds()
        
        # Resetear jugador
        self.player = Player(100, 100)
        
        # Cargar primer mundo
        self.current_world_index = 0
        self.load_current_world()
    
    def quit_game(self):
        """Cierra el juego"""
        print("👋 Saliendo del juego...")
        self.running = False
    
    def update(self):
        """Actualiza la lógica del juego"""

        # Solo actualizar si estamos jugando
        if self.menu_manager.current_state != GameState.PLAYING:
            return
        
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

        # Si estamos en menú principal, solo dibujar menú
        if self.menu_manager.current_state == GameState.MAIN_MENU:
            self.menu_manager.draw_current_menu()
            return
        

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

        # Dibujar menú encima si no estamos en PLAYING
        if self.menu_manager.current_state != GameState.PLAYING:
            self.menu_manager.draw_current_menu(self.world_loader.world_name)
    
    def run(self):
        """Loop principal del juego"""
        mouse_clicked = False
        
        while self.running:
            mouse_clicked = False
            
            # Eventos
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        # ESC en menú principal = salir
                        if self.menu_manager.current_state == GameState.MAIN_MENU:
                            self.running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # Click izquierdo
                        mouse_clicked = True
            
            # Manejar input según estado
            if self.menu_manager.current_state == GameState.PLAYING:
                # Input del juego (Command Pattern)
                keys = pygame.key.get_pressed()
                self.input_handler.handle_input(keys, self.player)
                
                # Actualizar
                self.update()
            else:
                # Input de menús
                mouse_pos = pygame.mouse.get_pos()
                self.menu_manager.handle_click(mouse_pos, mouse_clicked)
            
            # Dibujar
            self.draw()
            
            # Actualizar pantalla
            pygame.display.flip()
            self.clock.tick(GameConfig.FPS)
        
        pygame.quit()
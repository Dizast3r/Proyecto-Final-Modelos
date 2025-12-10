"""
Clase Game:
Controlador principal del juego que orquesta los subsistemas y el bucle principal.
Integra multiples patrones de diseno como Observer, Command y Memento para
delegar responsabilidades.
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
    Clase principal que maneja el ciclo de vida del juego.
    
    Patrones integrados:
    - Observer: A traves de GameEventManager para notificar eventos.
    - Command: A traves de InputHandler para procesar entradas.
    - Memento: A traves de CheckpointManager para guardar estado.
    - State: A traves de MenuManager para gestionar estados del juego.
    """
    
    def __init__(self, width=None, height=None, world_width=None):
        # Configuracion
        self.width = width or GameConfig.DEFAULT_WIDTH
        self.height = height or GameConfig.DEFAULT_HEIGHT
        self.world_width = world_width or GameConfig.DEFAULT_WORLD_WIDTH
        
        # Inicializar Pygame
        pygame.init()
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption(GameConfig.WINDOW_TITLE)
        self.clock = pygame.time.Clock()
        self.running = True

        # Sistema de menus (State Pattern para UI)
        self.menu_manager = MenuManager(self.screen)
        self.setup_menu_callbacks()
        
        # Sistema de eventos (Observer Pattern - Subject)
        self.event_manager = GameEventManager()
        
        # Inicializacion de subsistemas
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

        # Configuracion de generacion de mundos
        self.world_generators = []
        self.world_sequence = []
        self.current_world_index = -1
        
        # Registro de observadores
        self._setup_observers()
        
        print("Sistema iniciado correctamente")
    
    def setup_menu_callbacks(self):
        """Asigna las funciones de callback para las interacciones del menu."""
        self.menu_manager.on_start_game = self.start_new_game
        self.menu_manager.on_next_level = self.load_next_world
        self.menu_manager.on_restart_game = self.restart_from_beginning
        self.menu_manager.on_quit = self.quit_game
    
    def _setup_observers(self):
        """
        Configura e inicializa los observadores del sistema de eventos.
        Se suscriben al EventManager para reaccionar a cambios de estado.
        """
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
        """
        Carga los datos de un nivel especifico delegando en WorldLoader.
        Reinicia el estado del jugador y notifica el evento de carga.
        """
        self.world_loader.load_world(world_data)
        
        if self.world_loader.music_file:
            play_world_music(self.world_loader.music_file)
        
        self.player = Player(100, 100)
        self.checkpoint_manager.clear_checkpoints()
        
        event = GameEvent(
            GameEventType.WORLD_LOADED,
            {'world_name': self.world_loader.world_name}
        )
        self.event_manager.notify(event)
    
    def set_world_generators(self, generators: list):
        """Configura la lista de generadores de mundos a utilizar."""
        self.world_generators = generators
        print(f"Generadores configurados: {len(generators)}")
    
    def _regenerate_worlds(self):
        """
        Ejecuta el Template Method de cada generador para crear nuevas
        instancias de los niveles.
        """
        if not self.world_generators:
            print("No hay generadores configurados. Usando mundos existentes.")
            return
        
        print("\nGenerando mundos...")
        self.world_sequence = []
        
        for i, generator in enumerate(self.world_generators):
            print(f"Procesando generador {i+1}/{len(self.world_generators)}...")
            world_data = generator.generate_world(self.world_width, self.height)
            self.world_sequence.append(world_data)
        
        print("Generacion completada.")
    
    def start_new_game(self):
        """Inicia una nueva sesion de juego regenerando los niveles."""
        print("\nIniciando nuevo juego...")
        
        if self.world_generators:
            self._regenerate_worlds()
        
        self.current_world_index = 0
        self.load_current_world()
    
    def load_next_world(self):
        """Avanza al siguiente nivel en la secuencia si existe."""
        if self.current_world_index < len(self.world_sequence) - 1:
            self.current_world_index += 1
            self.load_current_world()
        else:
            print("No hay mas niveles disponibles.")
    
    def load_current_world(self):
        """Carga el nivel actual basado en el indice de secuencia."""
        if 0 <= self.current_world_index < len(self.world_sequence):
            world_data = self.world_sequence[self.current_world_index]
            self.load_world(world_data)
        else:
            print("Indice de mundo invalido.")
    
    def restart_from_beginning(self):
        """Reinicia el juego completamente desde el primer nivel."""
        print("\nReiniciando sistema...")
        
        if self.world_generators:
            self._regenerate_worlds()
        
        self.player = Player(100, 100)
        self.current_world_index = 0
        self.load_current_world()
    
    def quit_game(self):
        """Finaliza la ejecucion del juego."""
        self.running = False
    
    def update(self):
        """
        Logica principal de actualizacion por frame.
        Solo actualiza entidades si el estado es PLAYING.
        """
        if self.menu_manager.current_state != GameState.PLAYING:
            return
        
        platform_data = self.world_loader.get_platform_data()
        self.player.update(platform_data, self.world_width)
        
        for enemy in self.world_loader.enemies:
            enemy.update(
                platform_data,
                self.world_loader.spikes,
                self.world_loader.checkpoints,
                self.world_loader.goal,
                self.world_width
            )
        
        self.world_loader.enemies = [
            e for e in self.world_loader.enemies 
            if not e.should_be_removed()
        ]
        
        self.world_loader.powerups = [
            p for p in self.world_loader.powerups 
            if not p.collected
        ]
        
        self.collision_manager.check_all_collisions(
            self.player,
            self.world_loader.checkpoints,
            self.world_loader.goal,
            self.world_loader.enemies,
            self.world_loader.powerups,
            self.world_loader.spikes,
            self.world_loader.world_name
        )
        
        self.camera.update(self.player.x, self.player.width)
    
    def draw(self):
        """Renderiza el estado actual del juego o el menu correspondiente."""
        if self.menu_manager.current_state == GameState.MAIN_MENU:
            self.menu_manager.draw_current_menu()
            return
        
        # Renderizado del mundo
        sky_color = self.world_loader.colors.get('sky', (135, 206, 235))
        self.screen.fill(sky_color)
        
        camera_x = self.camera.get_x()
        
        for platform in self.world_loader.platforms:
            platform.draw(self.screen, camera_x)
        
        for spike in self.world_loader.spikes:
            spike.draw(self.screen, camera_x)
        
        for powerup in self.world_loader.powerups:
            powerup.draw(self.screen, camera_x)
        
        for checkpoint in self.world_loader.checkpoints:
            checkpoint.draw(self.screen, camera_x)
        
        for enemy in self.world_loader.enemies:
            enemy.draw(self.screen, camera_x)
        
        if self.world_loader.goal:
            self.world_loader.goal.draw(self.screen, camera_x)
        
        self.player.draw(self.screen, camera_x)
        
        self.ui_renderer.draw_ui(
            self.world_loader.world_name,
            self.player.lives
        )

        if self.menu_manager.current_state != GameState.PLAYING:
            self.menu_manager.draw_current_menu(self.world_loader.world_name)
    
    def run(self):
        """Bucle principal (Game Loop)."""
        mouse_clicked = False
        
        while self.running:
            mouse_clicked = False
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        if self.menu_manager.current_state == GameState.MAIN_MENU:
                            self.running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        mouse_clicked = True
            
            if self.menu_manager.current_state == GameState.PLAYING:
                keys = pygame.key.get_pressed()
                self.input_handler.handle_input(keys, self.player)
                self.update()
            else:
                mouse_pos = pygame.mouse.get_pos()
                self.menu_manager.handle_click(mouse_pos, mouse_clicked)
            
            self.draw()
            
            pygame.display.flip()
            self.clock.tick(GameConfig.FPS)
        
        pygame.quit()

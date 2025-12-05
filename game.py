"""
Clases principales del juego
"""

import pygame
from memento import PlayerMemento, CheckpointManager
from commands import InputHandler
from abc import ABC, abstractmethod

DEFAULT_SPEED = 5
DEFAULT_JUMP_POWER = 15
DEFAULT_GRAVITY = 0.8
DEFAULT_LIVES = 3
MAX_SPEED = 30
MAX_JUMP_POWER = 28

class Player:
    """Clase del jugador que puede guardar y restaurar su estado"""
    
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 40
        self.height = 60
        self.velocity_x = 0
        self.velocity_y = 0
        self.speed = DEFAULT_SPEED
        self.jump_power = DEFAULT_JUMP_POWER
        self.gravity = DEFAULT_GRAVITY
        self.on_ground = False
        self.lives = DEFAULT_LIVES
        
        # Aquí puedes cargar tu imagen del personaje
        # self.image = pygame.image.load('player.png')
        # Por ahora usamos un rectángulo
        self.image = None
    
    def move_left(self):
        """Movimiento a la izquierda"""
        self.velocity_x = -self.speed
    
    def move_right(self):
        """Movimiento a la derecha"""
        self.velocity_x = self.speed
    
    def stop(self):
        """Detener movimiento horizontal"""
        self.velocity_x = 0
    
    def jump(self):
        """Saltar solo si está en el suelo"""
        if self.on_ground:
            self.velocity_y = -self.jump_power
            self.on_ground = False
    
    def update(self, platforms):
        """Actualiza la posición del jugador"""
        # Aplicar gravedad
        self.velocity_y += self.gravity
        
        # Limitar velocidad de caída
        if self.velocity_y > 20:
            self.velocity_y = 20
        
        # Movimiento horizontal
        self.x += self.velocity_x
        
        # Movimiento vertical
        self.y += self.velocity_y
        
        # Colisiones con plataformas
        self.on_ground = False
        player_rect = pygame.Rect(self.x, self.y, self.width, self.height)
        
        for platform in platforms:
            platform_rect = pygame.Rect(platform['x'], platform['y'], 
                                       platform['width'], platform['height'])
            
            if player_rect.colliderect(platform_rect):
                # Colisión desde arriba (aterrizar)
                if self.velocity_y > 0:
                    self.y = platform['y'] - self.height
                    self.velocity_y = 0
                    self.on_ground = True
                # Colisión desde abajo
                elif self.velocity_y < 0:
                    self.y = platform['y'] + platform['height']
                    self.velocity_y = 0
    
    def draw(self, screen):
        """Dibuja el jugador"""
        if self.image:
            screen.blit(self.image, (self.x, self.y))
        else:
            # Dibujar rectángulo temporal (aquí irá tu sprite)
            pygame.draw.rect(screen, (255, 0, 0), 
                           (self.x, self.y, self.width, self.height))
            # Cara simple
            pygame.draw.circle(screen, (255, 255, 255), 
                             (int(self.x + 15), int(self.y + 20)), 3)
            pygame.draw.circle(screen, (255, 255, 255), 
                             (int(self.x + 25), int(self.y + 20)), 3)
    
    def create_memento(self):
        """Crea un memento con el estado actual"""
        return PlayerMemento(self.x, self.y, DEFAULT_SPEED, DEFAULT_JUMP_POWER) #Si tenia mejoras no no, se perdieron
    
    def restore_from_memento(self, memento):
        """Restaura el estado desde un memento"""
        if memento:
            state = memento.get_state()
            self.x = state['x']
            self.y = state['y']
            self.velocity_x = state['velocity_x']
            self.velocity_y = state['velocity_y']
            self.speed = state['speed']
            self.jump_power = state['jump_power']
    
    def get_rect(self):
        """Retorna el rectángulo de colisión"""
        return pygame.Rect(self.x, self.y, self.width, self.height)
    
    def die(self):
        """El jugador muere"""
        self.lives -= 1
        return self.lives > 0
    
    def get_life(self):
        self.lives += 1

    def increase_speed(self, speed_increase):
        new_speed = self.speed + speed_increase
        if new_speed <= MAX_SPEED:
            self.speed = new_speed
    
    def increse_jump_power(self, jump_power_increase):
        new_jump_power = self.jump_power + jump_power_increase
        if new_jump_power <= MAX_JUMP_POWER:
            self.jump_power = new_jump_power
        


class Platform:
    """Clase para las plataformas"""
    
    def __init__(self, x, y, width, height, color):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = color
    
    def draw(self, screen):
        """Dibuja la plataforma"""
        pygame.draw.rect(screen, self.color, 
                        (self.x, self.y, self.width, self.height))
        # Borde para efecto 3D
        pygame.draw.rect(screen, 
                        tuple(max(0, c - 30) for c in self.color),
                        (self.x, self.y, self.width, self.height), 3)


class Spike:
    """Clase para las espinas/trampas"""
    
    def __init__(self, x, y, width, height, color):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = color
    
    def draw(self, screen):
        """Dibuja la espina como un triángulo"""
        points = [
            (self.x + self.width // 2, self.y),  # Punta superior
            (self.x, self.y + self.height),      # Esquina inferior izquierda
            (self.x + self.width, self.y + self.height)  # Esquina inferior derecha
        ]
        pygame.draw.polygon(screen, self.color, points)
        pygame.draw.polygon(screen, (0, 0, 0), points, 2)
    
    def get_rect(self):
        """Retorna el rectángulo de colisión"""
        return pygame.Rect(self.x, self.y, self.width, self.height)


class Checkpoint:
    """Clase para los checkpoints"""
    
    def __init__(self, x, y, checkpoint_id):
        self.x = x
        self.y = y
        self.width = 40
        self.height = 60
        self.checkpoint_id = checkpoint_id
        self.activated = False
        self.color = (255, 215, 0)  # Dorado
    
    def draw(self, screen):
        """Dibuja el checkpoint"""
        if self.activated:
            color = (0, 255, 0)  # Verde cuando está activado
        else:
            color = self.color
        
        # Bandera
        pygame.draw.rect(screen, (100, 100, 100), 
                        (self.x, self.y, 5, self.height))
        pygame.draw.polygon(screen, color, [
            (self.x + 5, self.y),
            (self.x + self.width, self.y + 15),
            (self.x + 5, self.y + 30)
        ])
    
    def get_rect(self):
        """Retorna el rectángulo de colisión"""
        return pygame.Rect(self.x, self.y, self.width, self.height)
    
    def activate(self):
        """Activa el checkpoint"""
        self.activated = True

class PowerUP(ABC):
    def __init__(self, x, y, width, height, color):
        self.x = x
        self.y = y
        self.width = width
        self.height = height

    @abstractmethod
    def draw(self, screen):
        pass
    
    @abstractmethod
    def power(player):
        pass

DEFAULT_SPEED_INCREASE = 3
class PowerSpeedIncrease(PowerUP):
    def draw(self, screen):
        pass

    def power(player):
        player.speed_increase(DEFAULT_SPEED_INCREASE)

DEFAULT_JUMP_POWER_INCREASE = 2
class PowerJumpPowerIncrease(PowerUP):
    def draw(self, screen):
        pass

    def power(player):
        player.increase_jump_power(DEFAULT_JUMP_POWER_INCREASE)

class PowerExtraLife(PowerUP):
    def draw(self, screen):
        pass

    def power(player):
        player.get_life()
        

class Game:
    """Clase principal del juego"""
    
    def __init__(self, width=1600, height=600):
        pygame.init()
        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Mario Jump Game - Patrones de Diseño")
        self.clock = pygame.time.Clock()
        self.running = True
        
        # Inicializar sistemas
        self.input_handler = InputHandler()
        self.checkpoint_manager = CheckpointManager()
        
        # Inicializar jugador
        self.player = Player(100, 100)
        
        # Variables del mundo actual
        self.current_world = None
        self.platforms = []
        self.spikes = []
        self.checkpoints = []
        self.colors = {}
        self.world_name = ""
        
        # Fuente para texto
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
    
    def load_world(self, world_data):
        """Carga un mundo generado"""
        self.colors = world_data['colors']
        self.world_name = world_data['name']
        
        # Crear plataformas
        self.platforms = []
        for p in world_data['platforms']:
            platform = Platform(p['x'], p['y'], p['width'], p['height'], 
                              self.colors['platform'])
            self.platforms.append(platform)
        
        # Crear espinas
        self.spikes = []
        for s in world_data['spikes']:
            spike = Spike(s['x'], s['y'], s['width'], s['height'],
                         self.colors['hazard'])
            self.spikes.append(spike)
        
        # Crear checkpoints
        self.checkpoints = []
        for i, c in enumerate(world_data['checkpoints']):
            checkpoint = Checkpoint(c['x'], c['y'], i)
            self.checkpoints.append(checkpoint)
        
        # Resetear jugador
        self.player = Player(100, 100)
        self.checkpoint_manager.clear_checkpoints()
    
    def check_collisions(self):
        """Verifica colisiones con espinas y checkpoints"""
        player_rect = self.player.get_rect()

        # Colisión con checkpoints
        for checkpoint in self.checkpoints:
            if player_rect.colliderect(checkpoint.get_rect()):
                if not checkpoint.activated:
                    checkpoint.activate()
                    memento = self.player.create_memento()
                    self.checkpoint_manager.save_checkpoint(
                        checkpoint.checkpoint_id, memento)
        
        # Colisión con espinas
        for spike in self.spikes:
            if player_rect.colliderect(spike.get_rect()):
                if self.player.die():
                    # Restaurar desde último checkpoint
                    memento = self.checkpoint_manager.get_last_checkpoint()
                    if memento:
                        self.player.restore_from_memento(memento)
                    else:
                        self.player.x = 100
                        self.player.y = 100
                        self.player.velocity_x = 0
                        self.player.velocity_y = 0
                else:
                    # Game Over
                    print("Game Over!")
                    self.running = False

    def draw(self):
        """Dibuja todos los elementos del juego"""
        # Fondo (cielo)
        self.screen.fill(self.colors.get('sky', (135, 206, 235)))
        
        # Dibujar plataformas
        for platform in self.platforms:
            platform.draw(self.screen)
        
        # Dibujar espinas
        for spike in self.spikes:
            spike.draw(self.screen)
        
        # Dibujar checkpoints
        for checkpoint in self.checkpoints:
            checkpoint.draw(self.screen)
        
        # Dibujar jugador
        self.player.draw(self.screen)
        
        # Dibujar UI
        self.draw_ui()
    
    def draw_ui(self):
        """Dibuja la interfaz de usuario"""
        # Nombre del mundo
        world_text = self.font.render(self.world_name, True, (0, 0, 0))
        self.screen.blit(world_text, (10, 10))
        
        # Vidas
        lives_text = self.small_font.render(f"Vidas: {self.player.lives}", 
                                           True, (255, 0, 0))
        self.screen.blit(lives_text, (10, 50))
        
        # Instrucciones
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
    
    def update(self):
        """Actualiza la lógica del juego"""
        platform_data = [{'x': p.x, 'y': p.y, 'width': p.width, 
                         'height': p.height} for p in self.platforms]
        self.player.update(platform_data)
        self.check_collisions()
    
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
            
            # Input
            keys = pygame.key.get_pressed()
            self.input_handler.handle_input(keys, self.player)
            
            # Actualizar
            self.update()
            
            # Dibujar
            self.draw()
            
            # Actualizar pantalla
            pygame.display.flip()
            self.clock.tick(60)
        
        pygame.quit()
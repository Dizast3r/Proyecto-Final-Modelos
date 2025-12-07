"""
Clases principales del juego
"""

import pygame
from memento import PlayerMemento, CheckpointManager
from commands import InputHandler
from abc import ABC, abstractmethod

DEFAULT_SPEED = 5
DEFAULT_JUMP_POWER = 18
DEFAULT_GRAVITY = 0.8
DEFAULT_LIVES = 3
MAX_SPEED = 30
MAX_JUMP_POWER = 28

SPRITE_PLAYER_PATH = 'Assets/PlayerSprites/'
SPRITE_PREFIX = 'Sprite'
SPRITE_EXTENSION = '.png'
SPRITE_COUNT = 9
ANIMATION_PLAYER_SPEED = 0.30

PLAYER_WIDTH = 40
PLAYER_HEIGHT = 60

ENEMY_WIDTH = 40
ENEMY_HEIGHT = 50

POWERUP_WIDTH = ENEMY_WIDTH
POWERUP_HEIGHT = ENEMY_HEIGHT


SPRITE_ENEMY_PATH = 'Assets/EnemySprites/'
ENEMY_SPRITE_COUNT = 3
ENEMY_SPRITE_PREFIX = 'Sprite'
ENEMY_SPRITE_EXTENSION = '.png'
ENEMY_SPRITE_DEATH = 'SpriteDeath.png'
ANIMATION_ENEMY_SPEED = 10

POWERUP_SPRITE_PATH = 'Assets/PowerUpSprites/'
POWERUP_SPRITE_EXTENSION = '.png'

POWERUP_SPRITE_SPEED_NAME = 'SpriteSpeed'
POWERUP_SPRITE_JUMP_NAME  = 'SpriteJump'
POWERUP_SPRITE_LIFE_NAME  = 'SpriteLife'

class Player:
    """Clase del jugador que puede guardar y restaurar su estado"""
    
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = PLAYER_WIDTH
        self.height = PLAYER_HEIGHT
        self.velocity_x = 0
        self.velocity_y = 0
        self.speed = DEFAULT_SPEED
        self.jump_power = DEFAULT_JUMP_POWER
        self.gravity = DEFAULT_GRAVITY
        self.on_ground = False
        self.lives = DEFAULT_LIVES
        
        # Cargar sprites
        self.sprites = []
        for i in range(1, SPRITE_COUNT + 1):
            try:
                sprite_file = f'{SPRITE_PLAYER_PATH}{SPRITE_PREFIX}{i}{SPRITE_EXTENSION}'
                img = pygame.image.load(sprite_file)
                img = pygame.transform.scale(img, (self.width, self.height))
                self.sprites.append(img)
            except pygame.error as e:
                print(f"Error cargando {sprite_file}: {e}")

        # Sprite idle (quieto) - primer sprite
        self.idle_sprite = self.sprites[0] if self.sprites else None
        
        # Control de animación
        self.current_sprite = 0
        self.animation_speed = ANIMATION_PLAYER_SPEED
        self.animation_counter = 0
        
        # Dirección (para flip horizontal)
        self.facing_right = True
        
        # Imagen actual
        self.image = self.idle_sprite
    
    def move_left(self):
        """Movimiento a la izquierda"""
        self.velocity_x = -self.speed
        self.facing_right = False
    
    def move_right(self):
        """Movimiento a la derecha"""
        self.velocity_x = self.speed
        self.facing_right = True
    
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

        # Actualizar animación
        if self.sprites:
            if self.velocity_x != 0:  # Solo animar cuando se mueve
                self.animation_counter += self.animation_speed
                if self.animation_counter >= 1:
                    self.animation_counter = 0
                    self.current_sprite = (self.current_sprite + 1) % len(self.sprites)
                    self.image = self.sprites[self.current_sprite]
            else:  # Quieto - mostrar sprite idle
                self.image = self.idle_sprite
                self.current_sprite = 0
                self.animation_counter = 0
    
    def draw(self, screen, camera_x):
        """Dibuja el jugador"""
        screen_x = self.x - camera_x

        if self.image:
            img = self.image
            if not self.facing_right:  # Voltear si mira a la izquierda
                img = pygame.transform.flip(self.image, True, False)
            screen.blit(img, (screen_x, self.y))
        else:
            # Dibujar rectángulo temporal (aquí irá tu sprite)
            pygame.draw.rect(screen, (255, 0, 0), 
                           (screen_x, self.y, self.width, self.height))
            # Cara simple
            pygame.draw.circle(screen, (255, 255, 255), 
                             (int(screen_x + 15), int(self.y + 20)), 3)
            pygame.draw.circle(screen, (255, 255, 255), 
                             (int(screen_x + 25), int(self.y + 20)), 3)
            
    
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
        """Retorna el rectángulo de colisión (ligeramente más pequeño que el sprite)"""
        padding_x = 6   # margen lateral
        padding_top = 4 # margen superior ligero
        return pygame.Rect(
            self.x + padding_x,
            self.y + padding_top,
            self.width - 2 * padding_x,
            self.height - padding_top
        )

    
    def die(self):
        """El jugador muere"""
        if self.lives >= 1:
            self.lives -= 1
        return self.lives > 0
    
    def get_life(self):
        self.lives += 1

    def increase_speed(self, speed_increase):
        new_speed = self.speed + speed_increase
        if new_speed <= MAX_SPEED:
            self.speed = new_speed
        else:
            self.speed = MAX_SPEED
    
    def increase_jump_power(self, jump_power_increase):
        new_jump_power = self.jump_power + jump_power_increase
        if new_jump_power <= MAX_JUMP_POWER:
            self.jump_power = new_jump_power
        else: self.speed = MAX_SPEED
        
class Enemy:
    """Clase para enemigos con movimiento autónomo y comportamiento con sprites"""
    
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = ENEMY_WIDTH
        self.height = ENEMY_HEIGHT
        
        # Física
        self.velocity_x = -2  # Velocidad lenta, negativa = izquierda
        self.velocity_y = 0
        self.gravity = 0.8
        self.on_ground = False
        
        # Estado
        self.alive = True
        self.death_timer = 0
        self.death_duration = 120  # 2 segundos a 60 FPS
        
        # Cargar sprites
        self.sprites = []
        for i in range(1, ENEMY_SPRITE_COUNT + 1):
            try:
                sprite_file = f'{SPRITE_ENEMY_PATH}{ENEMY_SPRITE_PREFIX}{i}{ENEMY_SPRITE_EXTENSION}'
                img = pygame.image.load(sprite_file)
                img = pygame.transform.scale(img, (self.width, self.height))
                self.sprites.append(img)
            except pygame.error as e:
                print(f"Error cargando {sprite_file}: {e}")
        
        # Sprite de muerte
        self.death_sprite = None
        try:
            death_file = f'{SPRITE_ENEMY_PATH}{ENEMY_SPRITE_DEATH}'
            self.death_sprite = pygame.image.load(death_file)
            self.death_sprite = pygame.transform.scale(self.death_sprite, (self.width, self.height))
        except pygame.error as e:
            print(f"Error cargando sprite de muerte: {e}")
        
        # Sprite idle - primer sprite
        self.idle_sprite = self.sprites[0] if self.sprites else None
        
        # Control de animación ping-pong: 1,2,3,2,1,2,3...
        self.current_sprite = 0
        self.animation_speed = ANIMATION_ENEMY_SPEED
        self.animation_counter = 0
        self.sprite_sequence = [0, 1, 2, 1]  # Índices para ping-pong
        self.sequence_index = 0
        
        # Dirección (para flip horizontal)
        self.facing_right = False  # Empieza mirando izquierda
        
        # Imagen actual
        self.image = self.idle_sprite
    
    def update_animation(self):
        """Actualiza la animación del enemigo (ping-pong: 1,2,3,2,1)"""
        if not self.alive:
            # Si está muerto, usar sprite de muerte
            self.image = self.death_sprite if self.death_sprite else self.idle_sprite
            return
        
        if not self.sprites:
            return
        
        # Contador de frames
        self.animation_counter += 1
        
        if self.animation_counter >= self.animation_speed:
            self.animation_counter = 0
            
            # Avanzar en la secuencia ping-pong
            self.sequence_index = (self.sequence_index + 1) % len(self.sprite_sequence)
            self.current_sprite = self.sprite_sequence[self.sequence_index]
            
            # Obtener sprite base
            base_sprite = self.sprites[self.current_sprite]
            
            # Aplicar flip según dirección
            if self.facing_right:
                self.image = base_sprite
            else:
                self.image = pygame.transform.flip(base_sprite, True, False)
    
    def change_direction(self):
        """Cambia la dirección del enemigo"""
        self.velocity_x *= -1
        self.facing_right = not self.facing_right
    
    def check_obstacles(self, spikes, checkpoints, goal):
        """Verifica si debe cambiar de dirección por obstáculos"""
        if not self.alive:
            return
        
        # Crear rectángulo de detección adelante
        detection_distance = 50
        if not self.facing_right:  # Mirando izquierda
            detection_rect = pygame.Rect(
                self.x - detection_distance,
                self.y,
                detection_distance,
                self.height
            )
        else:  # Mirando derecha
            detection_rect = pygame.Rect(
                self.x + self.width,
                self.y,
                detection_distance,
                self.height
            )
        
        # Detectar espinas
        for spike in spikes:
            if detection_rect.colliderect(spike.get_rect()):
                self.change_direction()
                return
        
        # Detectar checkpoints
        for checkpoint in checkpoints:
            if detection_rect.colliderect(checkpoint.get_rect()):
                self.change_direction()
                return
        
        # Detectar meta
        if goal:
            if detection_rect.colliderect(goal.get_rect()):
                self.change_direction()
                return
    
    def update(self, platforms, spikes, checkpoints, goal):
        """Actualiza la posición y estado del enemigo"""
        if not self.alive:
            # Si está muerto, contar timer
            self.death_timer += 1
            self.update_animation()
            return
        
        # Actualizar animación
        self.update_animation()
        
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
        enemy_rect = pygame.Rect(self.x, self.y, self.width, self.height)
        
        for platform in platforms:
            platform_rect = pygame.Rect(
                platform['x'], platform['y'],
                platform['width'], platform['height']
            )
            
            if enemy_rect.colliderect(platform_rect):
                # Colisión desde arriba (aterrizar)
                if self.velocity_y > 0:
                    self.y = platform['y'] - self.height
                    self.velocity_y = 0
                    self.on_ground = True
                # Colisión desde abajo
                elif self.velocity_y < 0:
                    self.y = platform['y'] + platform['height']
                    self.velocity_y = 0
        
        # Verificar obstáculos adelante
        self.check_obstacles(spikes, checkpoints, goal)
    
    def draw(self, screen, camera_x):
        """Dibuja el enemigo"""
        screen_x = self.x - camera_x
        
        if self.image:
            screen.blit(self.image, (screen_x, self.y))
        else:
            # Fallback: dibujar rectángulo
            if self.alive:
                color = (255, 100, 0)  # Naranja
            else:
                color = (100, 100, 100)  # Gris
            pygame.draw.rect(screen, color, 
                           (screen_x, self.y, self.width, self.height))
            
            # Ojos simples
            if self.alive:
                eye_y = int(self.y + 15)
                if not self.facing_right:  # Izquierda
                    pygame.draw.circle(screen, (0, 0, 0),
                                     (int(screen_x + 12), eye_y), 3)
                else:  # Derecha
                    pygame.draw.circle(screen, (0, 0, 0),
                                     (int(screen_x + 28), eye_y), 3)
    
    def get_rect(self):
        """Rectángulo de colisión del enemigo (más estrecho que el sprite)"""
        padding_x = 6  # margen lateral
        return pygame.Rect(
            self.x + padding_x,
            self.y,
            self.width - 2 * padding_x,
            self.height
        )

    
    def die(self):
        """Mata al enemigo"""
        if self.alive:
            self.alive = False
            self.death_timer = 0
            self.velocity_x = 0
            self.velocity_y = 0
    
    def should_be_removed(self):
        """Verifica si el enemigo debe ser eliminado (después de 2 segundos muerto)"""
        return not self.alive and self.death_timer >= self.death_duration



class Platform:
    """Clase para las plataformas"""
    
    def __init__(self, x, y, width, height, color):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = color
    
    def draw(self, screen, camera_x):
        """Dibuja la plataforma"""
        screen_x = self.x - camera_x  # ← NUEVA LÍNEA
    
        pygame.draw.rect(screen, self.color,
                    (screen_x, self.y, self.width, self.height))
        # Borde para efecto 3D
        pygame.draw.rect(screen,
                    tuple(max(0, c - 30) for c in self.color),
                    (screen_x, self.y, self.width, self.height), 3)


class Spike:
    """Clase para las espinas/trampas"""
    
    def __init__(self, x, y, width, height, color):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = color
    
    def draw(self, screen, camera_x):  # ← Añadir parámetro
        """Dibuja la espina como un triángulo"""
        screen_x = self.x - camera_x  # ← NUEVA LÍNEA
        
        points = [
            (screen_x + self.width // 2, self.y),  # ← Usar screen_x
            (screen_x, self.y + self.height),  # ← Usar screen_x
            (screen_x + self.width, self.y + self.height)  # ← Usar screen_x
        ]
        
        pygame.draw.polygon(screen, self.color, points)
        pygame.draw.polygon(screen, (0, 0, 0), points, 2)
    
    def get_rect(self):
        """Retorna el rectángulo de colisión (solo parte superior del triángulo)"""
        hit_height = int(self.height * 0.6)  # solo el 60% superior es letal
        hit_y = self.y                      # desde la punta hacia abajo
        return pygame.Rect(self.x, hit_y, self.width, hit_height)



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
    
    def draw(self, screen, camera_x):  # ← Añadir parámetro
        """Dibuja el checkpoint"""
        screen_x = self.x - camera_x  # ← NUEVA LÍNEA
        
        if self.activated:
            color = (0, 255, 0)  # Verde cuando está activado
        else:
            color = self.color
        
        # Bandera
        pygame.draw.rect(screen, (100, 100, 100),
                    (screen_x, self.y, 5, self.height))  # ← Usar screen_x
        pygame.draw.polygon(screen, color, [
            (screen_x + 5, self.y),  # ← Usar screen_x
            (screen_x + self.width, self.y + 15),  # ← Usar screen_x
            (screen_x + 5, self.y + 30)  # ← Usar screen_x
        ])
    
    def get_rect(self):
        """Retorna el rectángulo de colisión"""
        return pygame.Rect(self.x, self.y, self.width, self.height)
    
    def activate(self):
        """Activa el checkpoint"""
        self.activated = True
    
class Goal:
    """Clase para la meta del nivel"""
    
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 60
        self.height = 250
        self.reached = False
        
        # Colores para el diseño
        self.base_color = (100, 100, 100)      # Gris para base
        self.pole_color = (255, 255, 255)      # Blanco para palo
        self.ball_color = (0, 0, 0)            # Negro para bola
    
    def draw(self, screen, camera_x):
        """Dibuja la meta: base cuadrada + palo blanco + bola negra"""
        screen_x = self.x - camera_x
        
        # Color cambia si ya se alcanzó
        if self.reached:
            base_color = (50, 255, 50)    # Verde brillante
            pole_color = (200, 255, 200)  # Blanco verdoso
            ball_color = (0, 200, 0)      # Verde oscuro
        else:
            base_color = self.base_color
            pole_color = self.pole_color
            ball_color = self.ball_color
        
        # 1. BASE CUADRADA (soporte)
        base_width = 40
        base_height = 15
        base_x = screen_x + (self.width - base_width) // 2  # Centrada
        base_y = self.y + self.height - base_height
        
        pygame.draw.rect(screen, base_color, 
                        (base_x, base_y, base_width, base_height))
        # Borde de la base
        pygame.draw.rect(screen, (50, 50, 50), 
                        (base_x, base_y, base_width, base_height), 2)
        
        # 2. PALO BLANCO ALTO
        pole_width = 8
        pole_height = self.height - base_height - 12  # Espacio para la bola
        pole_x = screen_x + (self.width - pole_width) // 2  # Centrado
        pole_y = self.y + 12  # Desde arriba (después de la bola)
        
        pygame.draw.rect(screen, pole_color, 
                        (pole_x, pole_y, pole_width, pole_height))
        # Borde del palo
        pygame.draw.rect(screen, (200, 200, 200), 
                        (pole_x, pole_y, pole_width, pole_height), 1)
        
        # 3. BOLA NEGRA EN EL TOPE
        ball_radius = 10
        ball_center_x = int(screen_x + self.width // 2)
        ball_center_y = int(self.y + ball_radius)
        
        pygame.draw.circle(screen, ball_color, 
                          (ball_center_x, ball_center_y), ball_radius)
        # Brillo en la bola (efecto 3D)
        highlight_offset = 3
        pygame.draw.circle(screen, (255, 255, 255), 
                          (ball_center_x - highlight_offset, 
                           ball_center_y - highlight_offset), 3)
    
    def get_rect(self):
        """Retorna el rectángulo de colisión"""
        return pygame.Rect(self.x, self.y, self.width, self.height)
    
    def activate(self):
        """Marca la meta como alcanzada"""
        self.reached = True


class PowerUP(ABC):
    def __init__(self, x, y, sprite_name):
        self.x = x
        self.y = y
        self.width = POWERUP_WIDTH
        self.height = POWERUP_HEIGHT
        
        self.collected = False
        self.image = None

        # Cargar sprite único, al estilo Player/Enemy
        sprite_file = f"{POWERUP_SPRITE_PATH}{sprite_name}{POWERUP_SPRITE_EXTENSION}"
        try:
            img = pygame.image.load(sprite_file)
            img = pygame.transform.scale(img, (self.width, self.height))
            self.image = img
        except pygame.error as e:
            print(f"Error cargando PowerUp {sprite_file}: {e}")
            self.image = None

    @abstractmethod
    def draw(self, screen, camera_x):
        """Dibuja el PowerUp (coordenadas con cámara)"""
        pass
    
    @abstractmethod
    def power(self, player):
        """Aplica el efecto concreto al jugador"""
        pass

    # Helper común para las subclases
    def _draw_base(self, screen, camera_x):
        if self.collected:
            return
        
        screen_x = self.x - camera_x
        if self.image:
            screen.blit(self.image, (screen_x, self.y))
        else:
            # Fallback: rectángulo amarillo si falla el sprite
            pygame.draw.rect(
                screen, (255, 255, 0),
                (screen_x, self.y, self.width, self.height)
            )


DEFAULT_SPEED_INCREASE = 3

class PowerSpeedIncrease(PowerUP):
    def __init__(self, x, y):
        super().__init__(
            x, y,
            POWERUP_SPRITE_SPEED_NAME
        )

    def draw(self, screen, camera_x):
        self._draw_base(screen, camera_x)

    def power(self, player):
        """Incrementa la velocidad del jugador"""
        player.increase_speed(DEFAULT_SPEED_INCREASE)


DEFAULT_JUMP_POWER_INCREASE = 2

class PowerJumpPowerIncrease(PowerUP):
    def __init__(self, x, y):
        super().__init__(
            x, y,
            POWERUP_SPRITE_JUMP_NAME
        )

    def draw(self, screen, camera_x):
        self._draw_base(screen, camera_x)

    def power(self, player):
        """Incrementa la potencia de salto del jugador"""
        player.increase_jump_power(DEFAULT_JUMP_POWER_INCREASE)


class PowerExtraLife(PowerUP):
    def __init__(self, x, y):
        super().__init__(
            x, y,
            POWERUP_SPRITE_LIFE_NAME
        )

    def draw(self, screen, camera_x):
        self._draw_base(screen, camera_x)

    def power(self, player):
        """Otorga una vida extra"""
        player.get_life()
        


class Game:
    """Clase principal del juego"""
    
    def __init__(self, width=1600, height=600, world_width = 3000):
        pygame.init()
        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((width, height))
        self.goal = None
        pygame.display.set_caption("Super Kirby Bro - Proyecto Final")
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
        self.enemies = []
        self.powerups = []
        self.checkpoints = []
        self.colors = {}
        self.world_name = ""

        # NUEVO: Sistema de cámara
        self.camera_x = 0
        self.world_width = world_width
        
        # Fuente para texto
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)

    def update_camera(self):
        """Actualiza la posición de la cámara siguiendo al jugador (centrado)"""
        # Centrar cámara en el jugador
        self.camera_x = self.player.x - self.width // 2
        
        # Limitar la cámara para que no salga de los bordes del mundo
        if self.camera_x < 0:
            self.camera_x = 0
        elif self.camera_x > self.world_width - self.width:
            self.camera_x = self.world_width - self.width
        
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
        
        # Crear goal (sin tipo)
        if world_data['goal']:
            goal_data = world_data['goal']
            self.goal = Goal(goal_data['x'], goal_data['y'])
        else:
            self.goal = None
        
        self.enemies = []
        for e in world_data.get('enemies', []):
            enemy = Enemy(e['x'], e['y'])
            self.enemies.append(enemy)


        self.powerups = []
        for p in world_data.get('powerups', []):
            p_type = p.get('type', 'speed')  # 'speed', 'jump', 'life'
            x = p['x']
            y = p['y']

            if p_type == 'speed':
                pu = PowerSpeedIncrease(x, y)
            elif p_type == 'jump':
                pu = PowerJumpPowerIncrease(x, y)
            elif p_type == 'life':
                pu = PowerExtraLife(x, y)
            else:
                # fallback genérico por si llega un tipo raro
                pu = PowerSpeedIncrease(x, y)

            self.powerups.append(pu)
        
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
        
        if self.goal and not self.goal.reached:
            if player_rect.colliderect(self.goal.get_rect()):
                self.goal.activate()
                print(f"\n🎉 ¡META ALCANZADA! Completaste {self.world_name}")

        for powerup in self.powerups:
            if getattr(powerup, 'collected', False):
                continue

            padding = 4  # margen pequeño
            px = powerup.x + padding
            py = powerup.y + padding
            pw = powerup.width - 2 * padding
            ph = powerup.height - 2 * padding

            powerup_rect = pygame.Rect(px, py, pw, ph)

            if player_rect.colliderect(powerup_rect):
                powerup.power(self.player)
                powerup.collected = True


        for enemy in self.enemies:
            if not enemy.alive:
                continue  # Ignorar enemigos muertos
            
            enemy_rect = enemy.get_rect()
            
            if player_rect.colliderect(enemy_rect):
                # Determinar tipo de colisión
                player_bottom = self.player.y + self.player.height
                enemy_top = enemy.y
                
                # Si el jugador viene desde arriba (aplastando)
                if self.player.velocity_y > 0 and player_bottom < enemy_top + 15:
                    # Jugador aplasta al enemigo
                    enemy.die()
                    # Pequeño rebote del jugador
                    self.player.velocity_y = -10
                    print("💥 ¡Enemigo aplastado!")
                else:
                    # Colisión frontal - el enemigo mata al jugador
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
                    elif self.running:
                        # Game Over
                        print("Game Over!")
                        self.running = False
        
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
                elif self.running:
                    # Game Over
                    print("Game Over!")
                    self.running = False

    def draw(self):
        """Dibuja todos los elementos del juego"""
        # Fondo (cielo)
        self.screen.fill(self.colors.get('sky', (135, 206, 235)))
        
        # Dibujar plataformas CON cámara
        for platform in self.platforms:
            platform.draw(self.screen, self.camera_x)
        
        # Dibujar espinas CON cámara
        for spike in self.spikes:
            spike.draw(self.screen, self.camera_x)

        for powerup in self.powerups:
            powerup.draw(self.screen, self.camera_x)
        
        # Dibujar checkpoints CON cámara
        for checkpoint in self.checkpoints:
            checkpoint.draw(self.screen, self.camera_x)
        
        for enemy in self.enemies:
            enemy.draw(self.screen, self.camera_x)
        
        # Dibujar goal CON cámara
        if self.goal:
            self.goal.draw(self.screen, self.camera_x)
        
        # Dibujar jugador CON cámara
        self.player.draw(self.screen, self.camera_x)
        
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
        for enemy in self.enemies:
            enemy.update(platform_data, self.spikes, self.checkpoints, self.goal)
        
        #Eliminar enemigos muertos (después de 2 segundos)
        self.enemies = [enemy for enemy in self.enemies if not enemy.should_be_removed()]
        self.powerups = [p for p in self.powerups if not getattr(p, 'collected', False)]
        self.check_collisions()
        self.update_camera()
    
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
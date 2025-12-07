"""
Clases principales del juego
"""

import pygame
from memento import *
from Powerups_Enemies import *
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
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        
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
    
    def update(self, platforms, world_width):
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
        self.rect.x = self.x
        self.rect.y = self.y
        
        for platform in platforms:
            platform_rect = pygame.Rect(platform['x'], platform['y'], 
                                       platform['width'], platform['height'])
            
            if self.rect.colliderect(platform_rect):
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
        # Límites de mundo
        if self.x < 0:
            self.x = 0
            self.velocity_x = 0
        elif self.x + self.width > world_width:
            self.x = world_width - self.width
            self.velocity_x = 0
    
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
        else: self.jump_power = MAX_JUMP_POWER
        
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

class Game:
    """Clase principal del juego - MODIFICADA para Flyweight"""
    
    def __init__(self, width=1600, height=600, world_width=3000):
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
        self.enemies = []  # Ahora contiene EnemyContext
        self.powerups = []  # Ahora contiene PowerUpContext
        self.checkpoints = []
        self.colors = {}
        self.world_name = ""

        # Sistema de cámara
        self.camera_x = 0
        self.world_width = world_width
        
        # Fuente para texto
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        
        print("🎮 Juego inicializado con Patrón Flyweight")

    def load_world(self, world_data):
        """Carga un mundo generado - MODIFICADO para Flyweight"""
        self.colors = world_data['colors']
        self.world_name = world_data['name']
        
        # Crear plataformas (sin cambios)
        self.platforms = []
        for p in world_data['platforms']:
            platform = Platform(p['x'], p['y'], p['width'], p['height'], 
                            self.colors['platform'])
            self.platforms.append(platform)
        
        # Crear espinas (sin cambios)
        self.spikes = []
        for s in world_data['spikes']:
            spike = Spike(s['x'], s['y'], s['width'], s['height'],
                        self.colors['hazard'])
            self.spikes.append(spike)
        
        # Crear checkpoints (sin cambios)
        self.checkpoints = []
        for i, c in enumerate(world_data['checkpoints']):
            checkpoint = Checkpoint(c['x'], c['y'], i)
            self.checkpoints.append(checkpoint)
        
        # Crear goal (sin cambios)
        if world_data['goal']:
            goal_data = world_data['goal']
            self.goal = Goal(goal_data['x'], goal_data['y'])
        else:
            self.goal = None
        
        # ✨ FLYWEIGHT: Crear enemigos usando EnemyContext
        self.enemies = []
        for e in world_data.get('enemies', []):
            enemy = EnemyContext(e['x'], e['y'], e.get('width', 40), e.get('height', 50))
            self.enemies.append(enemy)
        
        print(f"   ✅ {len(self.enemies)} enemigos creados (Flyweight compartido)")

        # ✨ FLYWEIGHT: Crear PowerUps usando PowerUpContext
        self.powerups = []
        for p in world_data.get('powerups', []):
            p_type = p.get('type', 'speed')  # 'speed', 'jump', 'life'
            powerup = PowerUpContext(
                p['x'], p['y'], 
                p_type,
                p.get('width', 40),
                p.get('height', 50)
            )
            self.powerups.append(powerup)
        
        print(f"   ✅ {len(self.powerups)} PowerUps creados (Flyweight compartido)")
        
        # Mostrar estadísticas de Flyweight
        cache_info = SpriteFlyweightFactory.get_cache_info()
        print(f"   📊 Flyweights en caché: {cache_info['total_flyweights']}")
        
        # Resetear jugador
        self.player = Player(100, 100)
        self.checkpoint_manager.clear_checkpoints()

    
    def check_collisions(self):
        """Verifica colisiones - MODIFICADO para Flyweight"""
        player_rect = self.player.get_rect()

        # Colisión con checkpoints (sin cambios)
        for checkpoint in self.checkpoints:
            if player_rect.colliderect(checkpoint.get_rect()):
                if not checkpoint.activated:
                    checkpoint.activate()
                    memento = self.player.create_memento()
                    self.checkpoint_manager.save_checkpoint(
                        checkpoint.checkpoint_id, memento)
        
        # Colisión con goal (sin cambios)
        if self.goal and not self.goal.reached:
            if player_rect.colliderect(self.goal.get_rect()):
                self.goal.activate()
                print(f"\n🎉 ¡META ALCANZADA! Completaste {self.world_name}")

        # ✨ FLYWEIGHT: Colisión con PowerUps
        for powerup in self.powerups:
            if powerup.collected:
                continue

            powerup_rect = powerup.get_rect()

            if player_rect.colliderect(powerup_rect):
                powerup.apply_power(self.player)  # Aplica el efecto

        # ✨ FLYWEIGHT: Colisión con enemigos
        for enemy in self.enemies:
            if not enemy.alive:
                continue
            
            enemy_rect = enemy.get_rect()
            
            if player_rect.colliderect(enemy_rect):
                # Determinar tipo de colisión
                player_bottom = self.player.y + self.player.height
                enemy_top = enemy_rect.y
                
                # Si el jugador viene desde arriba (aplastando)
                if self.player.velocity_y > 0 and player_bottom < enemy_top + 15:
                    enemy.die()
                    self.player.velocity_y = -10
                    print("💥 ¡Enemigo aplastado!")
                else:
                    # Colisión frontal - el enemigo mata al jugador
                    if self.player.die():
                        memento = self.checkpoint_manager.get_last_checkpoint()
                        if memento:
                            self.player.restore_from_memento(memento)
                        else:
                            self.player.x = 100
                            self.player.y = 100
                            self.player.velocity_x = 0
                            self.player.velocity_y = 0
                    elif self.running:
                        print("Game Over!")
                        self.running = False
        
        # Colisión con espinas (sin cambios)
        for spike in self.spikes:
            if player_rect.colliderect(spike.get_rect()):
                if self.player.die():
                    memento = self.checkpoint_manager.get_last_checkpoint()
                    if memento:
                        self.player.restore_from_memento(memento)
                    else:
                        self.player.x = 100
                        self.player.y = 100
                        self.player.velocity_x = 0
                        self.player.velocity_y = 0
                elif self.running:
                    print("Game Over!")
                    self.running = False

    def draw(self):
        """Dibuja todos los elementos - Los Context se encargan de usar Flyweight"""
        # Fondo (cielo)
        self.screen.fill(self.colors.get('sky', (135, 206, 235)))
        
        # Dibujar plataformas (sin cambios)
        for platform in self.platforms:
            platform.draw(self.screen, self.camera_x)
        
        # Dibujar espinas (sin cambios)
        for spike in self.spikes:
            spike.draw(self.screen, self.camera_x)

        # ✨ FLYWEIGHT: PowerUps usan automáticamente el Flyweight compartido
        for powerup in self.powerups:
            powerup.draw(self.screen, self.camera_x)
        
        # Dibujar checkpoints (sin cambios)
        for checkpoint in self.checkpoints:
            checkpoint.draw(self.screen, self.camera_x)
        
        # ✨ FLYWEIGHT: Enemigos usan automáticamente el Flyweight compartido
        for enemy in self.enemies:
            enemy.draw(self.screen, self.camera_x)
        
        # Dibujar goal (sin cambios)
        if self.goal:
            self.goal.draw(self.screen, self.camera_x)
        
        # Dibujar jugador (sin cambios)
        self.player.draw(self.screen, self.camera_x)
        
        # Dibujar UI (sin cambios)
        self.draw_ui()
    
    def update(self):
        """Actualiza la lógica - MODIFICADO para Flyweight"""
        platform_data = [{'x': p.x, 'y': p.y, 'width': p.width, 
                         'height': p.height} for p in self.platforms]
        
        self.player.update(platform_data, self.world_width)
        
        # ✨ FLYWEIGHT: Actualizar enemigos (EnemyContext)
        for enemy in self.enemies:
            enemy.update(platform_data, self.spikes, self.checkpoints, self.goal)
        
        # Eliminar enemigos muertos
        self.enemies = [enemy for enemy in self.enemies if not enemy.should_be_removed()]
        
        # Eliminar PowerUps recolectados
        self.powerups = [p for p in self.powerups if not p.collected]
        
        self.check_collisions()
        self.update_camera()
    
    def update_camera(self):
        """Actualiza la posición de la cámara siguiendo al jugador (centrado)"""
        # Centrar cámara en el jugador
        self.camera_x = self.player.x - self.width // 2
        
        # Limitar la cámara para que no salga de los bordes del mundo
        if self.camera_x < 0:
            self.camera_x = 0
        elif self.camera_x > self.world_width - self.width:
            self.camera_x = self.world_width - self.width
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
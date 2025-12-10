"""
Entidades del juego.
Define las clases core para los objetos interactivos del juego (Jugador,
Plataformas, Trampas, etc).
Implementacion de patrones:
- Memento: La clase Player actua como Originator, capaz de guardar y restaurar su estado.
"""

import pygame
from config import PlayerConfig
from memento import PlayerMemento


class Player:
    """
    Clase Player (Originator):
    Representa al personaje principal. Implementa metodos para crear y restaurar
    Mementos, permitiendo el sistema de checkpoints sin exponer su estructura interna.
    """
    
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = PlayerConfig.WIDTH
        self.height = PlayerConfig.HEIGHT
        self.velocity_x = 0
        self.velocity_y = 0
        self.speed = PlayerConfig.DEFAULT_SPEED
        self.jump_power = PlayerConfig.DEFAULT_JUMP_POWER
        self.gravity = PlayerConfig.DEFAULT_GRAVITY
        self.on_ground = False
        self.lives = PlayerConfig.DEFAULT_LIVES
        
        # Cargar sprites
        self.sprites = []
        for i in range(1, PlayerConfig.SPRITE_COUNT + 1):
            try:
                sprite_file = f'{PlayerConfig.SPRITE_PATH}{PlayerConfig.SPRITE_PREFIX}{i}{PlayerConfig.SPRITE_EXTENSION}'
                img = pygame.image.load(sprite_file)
                img = pygame.transform.scale(img, (self.width, self.height))
                self.sprites.append(img)
            except pygame.error as e:
                print(f"Error cargando {sprite_file}: {e}")

        # Sprite idle (quieto) - primer sprite
        self.idle_sprite = self.sprites[0] if self.sprites else None
        
        # Control de animacion
        self.current_sprite = 0
        self.animation_speed = PlayerConfig.ANIMATION_SPEED
        self.animation_counter = 0

        # Player Rect
        self.padding_x = 6
        self.padding_top = 4
        self.rect = pygame.Rect(
            self.x + self.padding_x,
            self.y + self.padding_top,
            self.width - 2 * self.padding_x,
            self.height - self.padding_top
        )
        
        # Direccion (para flip horizontal)
        self.facing_right = True
        
        # Imagen actual
        self.image = self.idle_sprite

        # Guardar spawn Inicial
        self._initial_spawn_memento = self.create_memento()
    
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
        """Saltar solo si esta en el suelo"""
        if self.on_ground:
            self.velocity_y = -self.jump_power
            self.on_ground = False
    
    def update(self, platforms, world_width):
        """Actualiza la posicion del jugador"""
        # Aplicar gravedad
        self.velocity_y += self.gravity
        
        # Limitar velocidad de caida
        if self.velocity_y > 20:
            self.velocity_y = 20
        
        # Movimiento horizontal
        self.x += self.velocity_x
        
        # Movimiento vertical
        self.y += self.velocity_y

        self._update_rect()
        
        # Colisiones con plataformas
        self.on_ground = False
        player_rect = self.get_rect()
        
        for platform in platforms:
            platform_rect = pygame.Rect(platform['x'], platform['y'], 
                                       platform['width'], platform['height'])
            
            if player_rect.colliderect(platform_rect):
                # Colision desde arriba (aterrizar)
                if self.velocity_y > 0:
                    self.y = platform['y'] - self.height
                    self.velocity_y = 0
                    self.on_ground = True
                # Colision desde abajo
                elif self.velocity_y < 0:
                    self.y = platform['y'] + platform['height']
                    self.velocity_y = 0

        # Actualizar animacion
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
        
        # Limites de mundo
        if self.x < 0:
            self.x = 0
            self.velocity_x = 0
        elif self.x + self.width > world_width:
            self.x = world_width - self.width
            self.velocity_x = 0
    
    def _update_rect(self):
        self.rect.x = self.x + self.padding_x
        self.rect.y = self.y + self.padding_top
    
    def draw(self, screen, camera_x):
        """Dibuja el jugador"""
        screen_x = self.x - camera_x

        if self.image:
            img = self.image
            if not self.facing_right:  # Voltear si mira a la izquierda
                img = pygame.transform.flip(self.image, True, False)
            screen.blit(img, (screen_x, self.y))
        else:
            # Dibujar rectangulo temporal
            pygame.draw.rect(screen, (255, 0, 0), 
                           (screen_x, self.y, self.width, self.height))
            # Cara simple
            pygame.draw.circle(screen, (255, 255, 255), 
                             (int(screen_x + 15), int(self.y + 20)), 3)
            pygame.draw.circle(screen, (255, 255, 255), 
                             (int(screen_x + 25), int(self.y + 20)), 3)
    
    def create_memento(self):
        """
        Crea un objeto Memento con el estado actual del jugador.
        """
        return PlayerMemento(self.x, self.y, PlayerConfig.DEFAULT_SPEED, PlayerConfig.DEFAULT_JUMP_POWER)
    
    def restore_from_memento(self, memento):
        """
        Restaura el estado del jugador usando un objeto Memento dado.
        """
        if memento:
            state = memento.get_state()
            self.x = state['x']
            self.y = state['y']
            self.velocity_x = state['velocity_x']
            self.velocity_y = state['velocity_y']
            self.speed = state['speed']
            self.jump_power = state['jump_power']

    def reset_to_initial_spawn(self):
        """        
        Este metodo usa el memento guardado en __init__ para restaurar
        completamente el jugador a su estado original.
        """
        self.restore_from_memento(self._initial_spawn_memento)
    
    def get_rect(self):
        return self.rect
    
    def die(self):
        """El jugador muere"""
        if self.lives >= 1:
            self.lives -= 1
        return self.lives > 0
    
    def get_life(self):
        """Gana una vida"""
        self.lives += 1

    def increase_speed(self, speed_increase):
        """Aumenta la velocidad"""
        new_speed = self.speed + speed_increase
        if new_speed <= PlayerConfig.MAX_SPEED:
            self.speed = new_speed
        else:
            self.speed = PlayerConfig.MAX_SPEED
    
    def increase_jump_power(self, jump_power_increase):
        """Aumenta el poder de salto"""
        new_jump_power = self.jump_power + jump_power_increase
        if new_jump_power <= PlayerConfig.MAX_JUMP_POWER:
            self.jump_power = new_jump_power
        else:
            self.jump_power = PlayerConfig.MAX_JUMP_POWER


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
        screen_x = self.x - camera_x
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
    
    def draw(self, screen, camera_x):
        """Dibuja la espina como un triangulo"""
        screen_x = self.x - camera_x
        
        points = [
            (screen_x + self.width // 2, self.y),
            (screen_x, self.y + self.height),
            (screen_x + self.width, self.y + self.height)
        ]
        
        pygame.draw.polygon(screen, self.color, points)
        pygame.draw.polygon(screen, (0, 0, 0), points, 2)
    
    def get_rect(self):
        """Retorna el rectangulo de colision (solo parte superior del triangulo)"""
        hit_height = int(self.height * 0.6)
        hit_y = self.y
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
    
    def draw(self, screen, camera_x):
        """Dibuja el checkpoint"""
        screen_x = self.x - camera_x
        
        if self.activated:
            color = (0, 255, 0)  # Verde cuando esta activado
        else:
            color = self.color
        
        # Bandera
        pygame.draw.rect(screen, (100, 100, 100),
                    (screen_x, self.y, 5, self.height))
        pygame.draw.polygon(screen, color, [
            (screen_x + 5, self.y),
            (screen_x + self.width, self.y + 15),
            (screen_x + 5, self.y + 30)
        ])
    
    def get_rect(self):
        """Retorna el rectangulo de colision"""
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
        self.base_color = (100, 100, 100)
        self.pole_color = (255, 255, 255)
        self.ball_color = (0, 0, 0)
    
    def draw(self, screen, camera_x):
        """Dibuja la meta: base cuadrada + palo blanco + bola negra"""
        screen_x = self.x - camera_x
        
        # Color cambia si ya se alcanzo
        if self.reached:
            base_color = (50, 255, 50)
            pole_color = (200, 255, 200)
            ball_color = (0, 200, 0)
        else:
            base_color = self.base_color
            pole_color = self.pole_color
            ball_color = self.ball_color
        
        # 1. BASE CUADRADA
        base_width = 40
        base_height = 15
        base_x = screen_x + (self.width - base_width) // 2
        base_y = self.y + self.height - base_height
        
        pygame.draw.rect(screen, base_color, 
                        (base_x, base_y, base_width, base_height))
        pygame.draw.rect(screen, (50, 50, 50), 
                        (base_x, base_y, base_width, base_height), 2)
        
        # 2. PALO BLANCO
        pole_width = 8
        pole_height = self.height - base_height - 12
        pole_x = screen_x + (self.width - pole_width) // 2
        pole_y = self.y + 12
        
        pygame.draw.rect(screen, pole_color, 
                        (pole_x, pole_y, pole_width, pole_height))
        pygame.draw.rect(screen, (200, 200, 200), 
                        (pole_x, pole_y, pole_width, pole_height), 1)
        
        # 3. BOLA NEGRA
        ball_radius = 10
        ball_center_x = int(screen_x + self.width // 2)
        ball_center_y = int(self.y + ball_radius)
        
        pygame.draw.circle(screen, ball_color, 
                          (ball_center_x, ball_center_y), ball_radius)
        pygame.draw.circle(screen, (255, 255, 255), 
                          (ball_center_x - 3, ball_center_y - 3), 3)
    
    def get_rect(self):
        """Retorna el rectangulo de colision"""
        return pygame.Rect(self.x, self.y, self.width, self.height)
    
    def activate(self):
        """Marca la meta como alcanzada"""
        self.reached = True

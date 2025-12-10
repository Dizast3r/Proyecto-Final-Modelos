"""
FLYWEIGHT PATTERN - Para compartir sprites entre múltiples instancias
Optimiza memoria almacenando sprites una sola vez y compartiéndolos
"""

import pygame
from typing import Dict, List, Optional
from abc import ABC, abstractmethod

class SpriteFlyweight:
    """
    Flyweight: Contiene el estado intrínseco (compartido) - los sprites cargados
    Este objeto es inmutable y se comparte entre múltiples instancias
    """
    
    def __init__(self, sprite_type: str, sprites: List[pygame.Surface], 
                 death_sprite: Optional[pygame.Surface] = None):
        """
        Args:
            sprite_type: Tipo de sprite ('enemy', 'powerup_speed', etc.)
            sprites: Lista de sprites de animación
            death_sprite: Sprite opcional de muerte (para enemigos)
        """
        self._sprite_type = sprite_type
        self._sprites = sprites  # Lista inmutable de sprites
        self._death_sprite = death_sprite
    
    @property
    def sprite_type(self) -> str:
        return self._sprite_type
    
    @property
    def sprites(self) -> List[pygame.Surface]:
        return self._sprites
    
    @property
    def death_sprite(self) -> Optional[pygame.Surface]:
        return self._death_sprite
    
    def get_sprite(self, index: int) -> pygame.Surface:
        """Obtiene un sprite específico de la animación"""
        if 0 <= index < len(self._sprites):
            return self._sprites[index]
        return self._sprites[0] if self._sprites else None
    
    def get_sprite_count(self) -> int:
        """Retorna el número de sprites en la animación"""
        return len(self._sprites)


class SpriteFlyweightFactory:
    """
    Factory: Gestiona la creación y caché de Flyweights
    Asegura que solo exista una instancia de cada tipo de sprite
    """
    
    _flyweights: Dict[str, SpriteFlyweight] = {}
    
    @classmethod
    def get_flyweight(cls, sprite_type: str, width: int, height: int) -> SpriteFlyweight:
        """
        Obtiene o crea un Flyweight para el tipo de sprite solicitado
        
        Args:
            sprite_type: 'enemy', 'powerup_speed', 'powerup_jump', 'powerup_life'
            width: Ancho del sprite
            height: Alto del sprite
        
        Returns:
            SpriteFlyweight compartido
        """
        # Clave única para este tipo y tamaño
        key = f"{sprite_type}_{width}x{height}"
        
        # Si ya existe, retornarlo (compartido)
        if key in cls._flyweights:
            return cls._flyweights[key]
        
        # Si no existe, crearlo y cachearlo
        flyweight = cls._create_flyweight(sprite_type, width, height)
        cls._flyweights[key] = flyweight
        
        print(f"✨ Flyweight creado: {key} (Total en caché: {len(cls._flyweights)})")
        
        return flyweight
    
    @classmethod
    def _create_flyweight(cls, sprite_type: str, width: int, height: int) -> SpriteFlyweight:
        """Crea un nuevo Flyweight cargando los sprites del disco"""
        
        if sprite_type == 'enemy':
            return cls._load_enemy_sprites(width, height)
        elif sprite_type.startswith('powerup_'):
            powerup_subtype = sprite_type.split('_')[1]  # 'speed', 'jump', 'life'
            return cls._load_powerup_sprite(powerup_subtype, width, height)
        else:
            raise ValueError(f"Tipo de sprite desconocido: {sprite_type}")
    
    @classmethod
    def _load_enemy_sprites(cls, width: int, height: int) -> SpriteFlyweight:
        """Carga los sprites del enemigo"""
        SPRITE_ENEMY_PATH = 'Assets/EnemySprites/'
        ENEMY_SPRITE_COUNT = 3
        ENEMY_SPRITE_PREFIX = 'Sprite'
        ENEMY_SPRITE_EXTENSION = '.png'
        ENEMY_SPRITE_DEATH = 'SpriteDeath.png'
        
        sprites = []
        
        # Cargar sprites de animación
        for i in range(1, ENEMY_SPRITE_COUNT + 1):
            try:
                sprite_file = f'{SPRITE_ENEMY_PATH}{ENEMY_SPRITE_PREFIX}{i}{ENEMY_SPRITE_EXTENSION}'
                img = pygame.image.load(sprite_file)
                img = pygame.transform.scale(img, (width, height))
                sprites.append(img)
            except pygame.error as e:
                print(f"⚠️ Error cargando {sprite_file}: {e}")
                # Crear sprite placeholder
                placeholder = cls._create_placeholder(width, height, (255, 100, 0))
                sprites.append(placeholder)
        
        # Cargar sprite de muerte
        death_sprite = None
        try:
            death_file = f'{SPRITE_ENEMY_PATH}{ENEMY_SPRITE_DEATH}'
            death_sprite = pygame.image.load(death_file)
            death_sprite = pygame.transform.scale(death_sprite, (width, height))
        except pygame.error as e:
            print(f"⚠️ Error cargando sprite de muerte: {e}")
            death_sprite = cls._create_placeholder(width, height, (100, 100, 100))
        
        return SpriteFlyweight('enemy', sprites, death_sprite)
    
    @classmethod
    def _load_powerup_sprite(cls, powerup_type: str, width: int, height: int) -> SpriteFlyweight:
        """Carga el sprite de un PowerUp"""
        POWERUP_SPRITE_PATH = 'Assets/PowerUpSprites/'
        POWERUP_SPRITE_EXTENSION = '.png'
        
        sprite_names = {
            'speed': 'SpriteSpeed',
            'jump': 'SpriteJump',
            'life': 'SpriteLife'
        }
        
        sprite_name = sprite_names.get(powerup_type, 'SpriteSpeed')
        sprite_file = f"{POWERUP_SPRITE_PATH}{sprite_name}{POWERUP_SPRITE_EXTENSION}"
        
        try:
            img = pygame.image.load(sprite_file)
            img = pygame.transform.scale(img, (width, height))
            sprites = [img]  # PowerUps solo tienen 1 sprite
        except pygame.error as e:
            print(f"⚠️ Error cargando {sprite_file}: {e}")
            # Colores por tipo
            colors = {'speed': (0, 255, 255), 'jump': (255, 0, 255), 'life': (255, 255, 0)}
            color = colors.get(powerup_type, (255, 255, 0))
            sprites = [cls._create_placeholder(width, height, color)]
        
        return SpriteFlyweight(f'powerup_{powerup_type}', sprites)
    
    @classmethod
    def _create_placeholder(cls, width: int, height: int, color: tuple) -> pygame.Surface:
        """Crea un sprite placeholder cuando falla la carga"""
        surface = pygame.Surface((width, height))
        surface.fill(color)
        # Borde negro
        pygame.draw.rect(surface, (0, 0, 0), (0, 0, width, height), 2)
        return surface
    
    @classmethod
    def clear_cache(cls):
        """Limpia la caché de Flyweights (útil para liberar memoria)"""
        cls._flyweights.clear()
        print("🗑️ Caché de Flyweights limpiada")
    
    @classmethod
    def get_cache_info(cls) -> Dict[str, int]:
        """Retorna información sobre la caché"""
        return {
            'total_flyweights': len(cls._flyweights),
            'types': list(cls._flyweights.keys())
        }
# ============================================================================
# CLASES CONTEXTO - Estado extrínseco (único por instancia)
# ============================================================================

"""
EnemyContext
"""
class EnemyContext:
    """
    Contexto del Enemy con sistema simple de detección de atasco
    """
    
    def __init__(self, x: int, y: int, width: int = 40, height: int = 50):
        # Estado extrínseco
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        
        # Padding para el rectángulo
        self.padding_x = 6
        self.padding_top = 12
        
        # Rectángulo ÚNICO
        self.rect = pygame.Rect(
            self.x + self.padding_x,
            self.y + self.padding_top,
            self.width - 2 * self.padding_x,
            self.height - self.padding_top
        )
        
        # Física
        self.velocity_x = -2
        self.velocity_y = 0
        self.gravity = 0.8
        self.on_ground = False
        
        # Estado
        self.alive = True
        self.death_timer = 0
        self.death_duration = 120
        
        # ✅ Sistema SIMPLE: contar cambios de dirección
        self.direction_changes = 0  # Cambios en la ventana actual
        self.direction_change_timer = 0  # Timer de ventana (60 frames = 1 segundo)
        self.ignore_spikes_timer = 0  # Timer para ignorar espinas (300 frames = 5 segundos)
        
        # Animación
        self.current_sprite_index = 0
        self.animation_counter = 0
        self.animation_speed = 10
        self.sprite_sequence = [0, 1, 2, 1]
        self.sequence_index = 0
        self.facing_right = False
        
        # FLYWEIGHT: Compartido
        from Powerups_Enemies import SpriteFlyweightFactory
        self._sprite_flyweight = SpriteFlyweightFactory.get_flyweight(
            'enemy', width, height
        )
    
    def update_animation(self):
        """Actualiza el índice de animación"""
        if not self.alive:
            return
        
        self.animation_counter += 1
        
        if self.animation_counter >= self.animation_speed:
            self.animation_counter = 0
            self.sequence_index = (self.sequence_index + 1) % len(self.sprite_sequence)
            self.current_sprite_index = self.sprite_sequence[self.sequence_index]
    
    def get_current_sprite(self) -> pygame.Surface:
        """Obtiene el sprite actual a dibujar"""
        if not self.alive:
            return self._sprite_flyweight.death_sprite
        
        base_sprite = self._sprite_flyweight.get_sprite(self.current_sprite_index)
        
        if self.facing_right:
            return base_sprite
        else:
            return pygame.transform.flip(base_sprite, True, False)
    
    def draw(self, screen: pygame.Surface, camera_x: int):
        """Dibuja el enemigo"""
        screen_x = self.x - camera_x
        sprite = self.get_current_sprite()
        
        if sprite:
            screen.blit(sprite, (screen_x, self.y))
        else:
            color = (255, 100, 0) if self.alive else (100, 100, 100)
            pygame.draw.rect(screen, color, (screen_x, self.y, self.width, self.height))
    
    def change_direction(self):
        """
        ✅ MODIFICADO: Registra cambios de dirección
        """
        self.velocity_x *= -1
        self.facing_right = not self.facing_right
        
        # Incrementar contador de cambios
        self.direction_changes += 1
        
        # Si cambió más de 5 veces en la ventana → IGNORAR espinas por 5 segundos
        if self.direction_changes > 5:
            self.ignore_spikes_timer = 300  # 300 frames = 5 segundos a 60 FPS
            self.direction_changes = 0
            self.direction_change_timer = 0
    
    def update(self, platforms, spikes, checkpoints, goal, world_width):
        """
        Actualiza lógica del enemigo
        """
        if not self.alive:
            self.death_timer += 1
            self.update_animation()
            return
        
        # ✅ Actualizar timers
        if self.ignore_spikes_timer > 0:
            self.ignore_spikes_timer -= 1
        
        # Timer de ventana de cambios de dirección
        self.direction_change_timer += 1
        if self.direction_change_timer >= 60:  # 1 segundo
            # Resetear ventana
            self.direction_changes = 0
            self.direction_change_timer = 0
        
        # Limitar al mundo
        if self.x < 0:
            self.x = 0
            self.change_direction()
        elif self.x + self.width > world_width:
            self.x = world_width - self.width
            self.change_direction()
        
        # Física
        self.velocity_y += self.gravity
        if self.velocity_y > 20:
            self.velocity_y = 20
        
        self.x += self.velocity_x
        self.y += self.velocity_y
        
        # Actualizar rectángulo
        self.rect.x = self.x + self.padding_x
        self.rect.y = self.y + self.padding_top
        
        # Colisiones con plataformas
        self.on_ground = False
        
        for platform in platforms:
            platform_rect = pygame.Rect(
                platform['x'], platform['y'],
                platform['width'], platform['height']
            )
            
            if self.rect.colliderect(platform_rect):
                if self.velocity_y > 0:
                    self.y = platform['y'] - self.height
                    self.velocity_y = 0
                    self.on_ground = True
                    self.rect.x = self.x + self.padding_x
                    self.rect.y = self.y + self.padding_top
                elif self.velocity_y < 0:
                    self.y = platform['y'] + platform['height']
                    self.velocity_y = 0
                    self.rect.x = self.x + self.padding_x
                    self.rect.y = self.y + self.padding_top
        
        self.update_animation()
        
        # Detectar obstáculos
        self._check_obstacles(spikes, checkpoints, goal)
    
    def _check_obstacles(self, spikes, checkpoints, goal):
        """
        ✅ SIMPLIFICADO: Solo ignora espinas si ignore_spikes_timer > 0
        """
        if not self.alive:
            return
        
        detection_distance = 30
        if not self.facing_right:
            detection_rect = pygame.Rect(
                self.rect.x - detection_distance,
                self.rect.y,
                detection_distance,
                self.rect.height
            )
        else:
            detection_rect = pygame.Rect(
                self.rect.x + self.rect.width,
                self.rect.y,
                detection_distance,
                self.rect.height
            )
        
        # ✅ SIEMPRE verificar checkpoints y goal
        for checkpoint in checkpoints:
            if detection_rect.colliderect(checkpoint.get_rect()):
                self.change_direction()
                return
        
        if goal and detection_rect.colliderect(goal.get_rect()):
            self.change_direction()
            return
        
        # ✅ Solo verificar espinas si NO está ignorándolas
        if self.ignore_spikes_timer <= 0:
            for spike in spikes:
                if detection_rect.colliderect(spike.get_rect()):
                    self.change_direction()
                    return
    
    def get_rect(self) -> pygame.Rect:
        """Retorna el rectángulo de colisión"""
        return self.rect
    
    def die(self):
        """Mata al enemigo"""
        if self.alive:
            self.alive = False
            self.death_timer = 0
            self.velocity_x = 0
            self.velocity_y = 0
    
    def should_be_removed(self) -> bool:
        """Verifica si debe eliminarse"""
        return not self.alive and self.death_timer >= self.death_duration



class PowerUpContext:
    """
    Contexto del PowerUp: Estado extrínseco único de cada instancia
    Comparte el Flyweight con todos los PowerUps del mismo tipo
    """
    
    def __init__(self, x: int, y: int, powerup_type: str, 
                 width: int = 40, height: int = 50):
        # Estado extrínseco
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.powerup_type = powerup_type
        self.collected = False

        # ✨ STRATEGY PATTERN: Inyección de dependencia
        # Cada PowerUp tiene su estrategia específica
        self._strategy = PowerUpStrategyFactory.create_strategy(powerup_type)

        
        # FLYWEIGHT: Compartido entre todos los PowerUps del mismo tipo
        self._sprite_flyweight = SpriteFlyweightFactory.get_flyweight(
            f'powerup_{powerup_type}', width, height
        )
    
    def get_sprite(self) -> pygame.Surface:
        """Obtiene el sprite del Flyweight"""
        return self._sprite_flyweight.get_sprite(0)  # PowerUps tienen 1 solo sprite
    
    def draw(self, screen: pygame.Surface, camera_x: int):
        """Dibuja el PowerUp"""
        if self.collected:
            return
        
        screen_x = self.x - camera_x
        sprite = self.get_sprite()
        
        if sprite:
            screen.blit(sprite, (screen_x, self.y))
        else:
            # Fallback
            pygame.draw.rect(screen, (255, 255, 0),
                           (screen_x, self.y, self.width, self.height))
    
    def get_rect(self) -> pygame.Rect:
        """Rectángulo de colisión con padding"""
        padding = 4
        return pygame.Rect(
            self.x + padding, self.y + padding,
            self.width - 2 * padding, self.height - 2 * padding
        )
    
    def apply_power(self, player):
        """
        Aplica el efecto al jugador usando Strategy Pattern
        """
        # ✨ Delegación a la estrategia
        self._strategy.apply(player)
        
        # Marcar como recolectado
        self.collected = True

"""
STRATEGY PATTERN - Estrategias para diferentes tipos de PowerUps
Cada estrategia encapsula el comportamiento de un tipo de PowerUp específico
"""

class PowerUpStrategy(ABC):
    """
    Interfaz Strategy - Define el contrato para todas las estrategias de PowerUp
    """
    
    @abstractmethod
    def apply(self, player):
        """
        Aplica el efecto del PowerUp al jugador
        
        Args:
            player: Instancia del jugador que recibe el efecto
        """
        pass
    
    @abstractmethod
    def get_type_name(self) -> str:
        """Retorna el nombre del tipo de PowerUp para eventos"""
        pass


class SpeedBoostStrategy(PowerUpStrategy):
    """
    Estrategia para PowerUp de velocidad
    Aumenta la velocidad de movimiento del jugador
    """
    
    def __init__(self, speed_increase: int = 3):
        """
        Args:
            speed_increase: Cantidad de velocidad a aumentar (default: 3)
        """
        self.speed_increase = speed_increase
    
    def apply(self, player):
        """Aumenta la velocidad del jugador"""
        player.increase_speed(self.speed_increase)
    
    def get_type_name(self) -> str:
        return 'speed'


class JumpBoostStrategy(PowerUpStrategy):
    """
    Estrategia para PowerUp de salto
    Aumenta la potencia de salto del jugador
    """
    
    def __init__(self, jump_increase: int = 2):
        """
        Args:
            jump_increase: Cantidad de potencia de salto a aumentar (default: 2)
        """
        self.jump_increase = jump_increase
    
    def apply(self, player):
        """Aumenta la potencia de salto del jugador"""
        player.increase_jump_power(self.jump_increase)
    
    def get_type_name(self) -> str:
        return 'jump'


class LifeBoostStrategy(PowerUpStrategy):
    """
    Estrategia para PowerUp de vida extra
    Otorga una vida adicional al jugador
    """
    
    def apply(self, player):
        """Otorga una vida extra al jugador"""
        player.get_life()
    
    def get_type_name(self) -> str:
        return 'life'


class PowerUpStrategyFactory:
    """
    Factory para crear estrategias de PowerUp
    Centraliza la lógica de creación y permite configuración
    """
    
    # Registro de estrategias disponibles
    _strategies = {
        'speed': SpeedBoostStrategy,
        'jump': JumpBoostStrategy,
        'life': LifeBoostStrategy
    }
    
    @classmethod
    def create_strategy(cls, powerup_type: str, **kwargs) -> PowerUpStrategy:
        """
        Crea una estrategia basada en el tipo de PowerUp
        
        Args:
            powerup_type: Tipo de PowerUp ('speed', 'jump', 'life')
            **kwargs: Parámetros opcionales para la estrategia
                     (ej: speed_increase=5, jump_increase=3)
        
        Returns:
            Instancia de la estrategia correspondiente
        
        Raises:
            ValueError: Si el tipo de PowerUp no está registrado
        """
        if powerup_type not in cls._strategies:
            raise ValueError(
                f"PowerUp tipo '{powerup_type}' no reconocido. "
                f"Tipos disponibles: {list(cls._strategies.keys())}"
            )
        
        strategy_class = cls._strategies[powerup_type]
        return strategy_class(**kwargs)
    
    @classmethod
    def register_strategy(cls, powerup_type: str, strategy_class):
        """
        Registra una nueva estrategia (para extensibilidad futura) 
        Args:
            powerup_type: Identificador del tipo de PowerUp
            strategy_class: Clase de estrategia que implementa PowerUpStrategy
        """
        cls._strategies[powerup_type] = strategy_class
        print(f"✅ Estrategia '{powerup_type}' registrada")
    
    @classmethod
    def get_available_types(cls) -> list:
        """Retorna lista de tipos de PowerUp disponibles"""
        return list(cls._strategies.keys())
"""
Configuración y constantes del juego
"""

# Configuración del jugador
class PlayerConfig:
    DEFAULT_SPEED = 5
    DEFAULT_JUMP_POWER = 18
    DEFAULT_GRAVITY = 0.8
    DEFAULT_LIVES = 3
    MAX_SPEED = 30
    MAX_JUMP_POWER = 28
    WIDTH = 40
    HEIGHT = 60
    
    # Sprites
    SPRITE_PATH = 'Assets/PlayerSprites/'
    SPRITE_PREFIX = 'Sprite'
    SPRITE_EXTENSION = '.png'
    SPRITE_COUNT = 9
    ANIMATION_SPEED = 0.30


# Configuración de enemigos
class EnemyConfig:
    WIDTH = 40
    HEIGHT = 50
    SPRITE_PATH = 'Assets/EnemySprites/'
    SPRITE_COUNT = 3
    SPRITE_PREFIX = 'Sprite'
    SPRITE_EXTENSION = '.png'
    SPRITE_DEATH = 'SpriteDeath.png'
    ANIMATION_SPEED = 10


# Configuración de PowerUps
class PowerUpConfig:
    WIDTH = 40
    HEIGHT = 50
    SPRITE_PATH = 'Assets/PowerUpSprites/'
    SPRITE_EXTENSION = '.png'
    SPRITE_SPEED_NAME = 'SpriteSpeed'
    SPRITE_JUMP_NAME = 'SpriteJump'
    SPRITE_LIFE_NAME = 'SpriteLife'


# Configuración del juego
class GameConfig:
    DEFAULT_WIDTH = 1600
    DEFAULT_HEIGHT = 600
    DEFAULT_WORLD_WIDTH = 3000
    FPS = 60
    WINDOW_TITLE = "Super Kirby Bro - Proyecto Final"
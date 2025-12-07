from abc import ABC, abstractmethod


# =============================================================================
# CONFIGURACIÓN CENTRALIZADA
# =============================================================================

class PowerUpConfig:
    """Configuración centralizada de PowerUps"""
    
    # Dimensiones
    WIDTH = 40
    HEIGHT = 40
    
    # Rutas de sprites
    SPRITE_PATH = 'Assets/PowerUpSprites/'
    SPRITE_EXTENSION = '.png'
    
    # Efectos por defecto
    SPEED_INCREASE = 3
    JUMP_INCREASE = 2
    LIFE_AMOUNT = 1
    
    # Sprites por tipo
    SPRITES = {
        'speed': 'SpriteSpeed',
        'jump': 'SpriteJump',
        'life': 'SpriteLife',
    }
    
    # Colores de fallback (si falta sprite)
    FALLBACK_COLORS = {
        'speed': (0, 255, 255),    # Cyan
        'jump': (255, 255, 0),     # Amarillo
        'life': (255, 0, 255),     # Magenta
        'invincible': (255, 215, 0),  # Dorado
        'shield': (0, 191, 255),   # Azul cielo
        'magnet': (138, 43, 226)   # Violeta
    }


# =============================================================================
# PATRÓN STRATEGY - Estrategias de Efectos
# =============================================================================

class PowerUpStrategy(ABC):
    """Interfaz para estrategias de PowerUps"""
    
    @abstractmethod
    def apply(self, player) -> None:
        """Aplica el efecto al jugador"""
        pass
    
    @abstractmethod
    def get_description(self) -> str:
        """Retorna descripción del efecto"""
        pass
    
    @abstractmethod
    def get_type(self) -> str:
        """Retorna el tipo de PowerUp"""
        pass


# -----------------------------------------------------------------------------
# Estrategias Concretas
# -----------------------------------------------------------------------------

class SpeedBoostStrategy(PowerUpStrategy):
    """Estrategia: Aumenta velocidad"""
    
    def __init__(self, amount: int = PowerUpConfig.SPEED_INCREASE):
        self.amount = amount
    
    def apply(self, player) -> None:
        player.increase_speed(self.amount)
    
    def get_description(self) -> str:
        return f"Speed +{self.amount}"
    
    def get_type(self) -> str:
        return 'speed'


class JumpBoostStrategy(PowerUpStrategy):
    """Estrategia: Aumenta potencia de salto"""
    
    def __init__(self, amount: int = PowerUpConfig.JUMP_INCREASE):
        self.amount = amount
    
    def apply(self, player) -> None:
        player.increase_jump_power(self.amount)
    
    def get_description(self) -> str:
        return f"Jump +{self.amount}"
    
    def get_type(self) -> str:
        return 'jump'


class ExtraLifeStrategy(PowerUpStrategy):
    """Estrategia: Otorga vida extra"""
    
    def __init__(self, amount: int = PowerUpConfig.LIFE_AMOUNT):
        self.amount = amount
    
    def apply(self, player) -> None:
        for _ in range(self.amount):
            player.get_life()
    
    def get_description(self) -> str:
        return f"+{self.amount} Life"
    
    def get_type(self) -> str:
        return 'life'
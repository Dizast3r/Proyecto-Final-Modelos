"""
Cargador de Mundos (World Loader).
Responsable de interpretar los datos crudos generados por los algoritmos (DTOs)
y convertirlos en instancias de entidades de juego utilizables.
Actua como una Factoria o Builder que ensambla el nivel final.
"""

from entities import Platform, Spike, Checkpoint, Goal
from Powerups_Enemies import EnemyContext, PowerUpContext


class WorldLoader:
    """
    Clase encargada de la instanciacion de objetos del nivel.
    Convierte diccionarios de configuracion en objetos PyGame/Entidades.
    """
    
    def __init__(self):
        self.platforms = []
        self.spikes = []
        self.checkpoints = []
        self.enemies = []
        self.powerups = []
        self.goal = None
        self.colors = {}
        self.world_name = ""
        self.music_file = None
    
    def load_world(self, world_data):
        """
        Procesa el diccionario de datos del mundo y puebla las listas de entidades.
        
        Args:
            world_data (dict): Diccionario con la configuracion del nivel generada.
        """
        self.colors = world_data['colors']
        self.world_name = world_data['name']
        self.music_file = world_data['music']
        
        # Crear plataformas
        self.platforms = self._create_platforms(world_data['platforms'])
        
        # Crear espinas
        self.spikes = self._create_spikes(world_data['spikes'])
        
        # Crear checkpoints
        self.checkpoints = self._create_checkpoints(world_data['checkpoints'])
        
        # Crear goal
        self.goal = self._create_goal(world_data['goal'])
        
        # Crear enemigos (Flyweight)
        self.enemies = self._create_enemies(world_data.get('enemies', []))
        
        # Crear PowerUps (Flyweight)
        self.powerups = self._create_powerups(world_data.get('powerups', []))
        
        print(f"Mundo cargado: {self.world_name}")
    
    def _create_platforms(self, platform_data):
        """Instancia objetos Platform desde datos crudos."""
        platforms = []
        for p in platform_data:
            platform = Platform(
                p['x'], p['y'], p['width'], p['height'],
                self.colors['platform']
            )
            platforms.append(platform)
        return platforms
    
    def _create_spikes(self, spike_data):
        """Instancia objetos Spike desde datos crudos."""
        spikes = []
        for s in spike_data:
            spike = Spike(
                s['x'], s['y'], s['width'], s['height'],
                self.colors['hazard']
            )
            spikes.append(spike)
        return spikes
    
    def _create_checkpoints(self, checkpoint_data):
        """Instancia objetos Checkpoint desde datos crudos."""
        checkpoints = []
        for i, c in enumerate(checkpoint_data):
            checkpoint = Checkpoint(c['x'], c['y'], i)
            checkpoints.append(checkpoint)
        return checkpoints
    
    def _create_goal(self, goal_data):
        """Instancia el objeto Goal si existe en los datos."""
        if goal_data:
            return Goal(goal_data['x'], goal_data['y'])
        return None
    
    def _create_enemies(self, enemy_data):
        """
        Instancia contextos de enemigos.
        Utiliza el patron Flyweight implicitamente al usar EnemyContext.
        """
        enemies = []
        for e in enemy_data:
            enemy = EnemyContext(
                e['x'], e['y'],
                e.get('width', 40),
                e.get('height', 50)
            )
            enemies.append(enemy)
        return enemies
    
    def _create_powerups(self, powerup_data):
        """
        Instancia contextos de PowerUps.
        Utiliza el patron Flyweight implicitamente al usar PowerUpContext.
        """
        powerups = []
        for p in powerup_data:
            powerup_type = p.get('type', 'speed')
            powerup = PowerUpContext(
                p['x'], p['y'],
                powerup_type,
                p.get('width', 40),
                p.get('height', 50)
            )
            powerups.append(powerup)
        return powerups
    
    def get_platform_data(self):
        """Retorna una lista simplificada de plataformas para calculos de fisica."""
        return [
            {
                'x': p.x,
                'y': p.y,
                'width': p.width,
                'height': p.height
            }
            for p in self.platforms
        ]

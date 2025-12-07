"""
Cargador de mundos - Separa la lógica de carga de mundos
"""

from entities import Platform, Spike, Checkpoint, Goal
from Powerups_Enemies import EnemyContext, PowerUpContext


class WorldLoader:
    """Carga y convierte datos de mundo en entidades del juego"""
    
    def __init__(self):
        self.platforms = []
        self.spikes = []
        self.checkpoints = []
        self.enemies = []
        self.powerups = []
        self.goal = None
        self.colors = {}
        self.world_name = ""
    
    def load_world(self, world_data):
        """Carga un mundo generado"""
        self.colors = world_data['colors']
        self.world_name = world_data['name']
        
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
        
        print(f"\n🌍 Mundo cargado: {self.world_name}")
        print(f"   ✅ {len(self.platforms)} plataformas")
        print(f"   ✅ {len(self.spikes)} espinas")
        print(f"   ✅ {len(self.checkpoints)} checkpoints")
        print(f"   ✅ {len(self.enemies)} enemigos")
        print(f"   ✅ {len(self.powerups)} PowerUps")
    
    def _create_platforms(self, platform_data):
        """Crea las plataformas del mundo"""
        platforms = []
        for p in platform_data:
            platform = Platform(
                p['x'], p['y'], p['width'], p['height'],
                self.colors['platform']
            )
            platforms.append(platform)
        return platforms
    
    def _create_spikes(self, spike_data):
        """Crea las espinas del mundo"""
        spikes = []
        for s in spike_data:
            spike = Spike(
                s['x'], s['y'], s['width'], s['height'],
                self.colors['hazard']
            )
            spikes.append(spike)
        return spikes
    
    def _create_checkpoints(self, checkpoint_data):
        """Crea los checkpoints del mundo"""
        checkpoints = []
        for i, c in enumerate(checkpoint_data):
            checkpoint = Checkpoint(c['x'], c['y'], i)
            checkpoints.append(checkpoint)
        return checkpoints
    
    def _create_goal(self, goal_data):
        """Crea la meta del mundo"""
        if goal_data:
            return Goal(goal_data['x'], goal_data['y'])
        return None
    
    def _create_enemies(self, enemy_data):
        """Crea los enemigos usando Flyweight"""
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
        """Crea los PowerUps usando Flyweight"""
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
        """Retorna datos de plataformas para física"""
        return [
            {
                'x': p.x,
                'y': p.y,
                'width': p.width,
                'height': p.height
            }
            for p in self.platforms
        ]
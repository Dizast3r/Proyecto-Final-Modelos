# -*- coding: utf-8 -*-
"""
TEMPLATE METHOD PATTERN - Para generar diferentes tipos de mundos
REFACTORIZADO: Aplicando principios SOLID y eliminando duplicación

Mejoras implementadas:
- Eliminación de duplicación de código (DRY)
- Separación de responsabilidades (SRP)
- Clases auxiliares para validaciones
- Configuración por mundo usando dataclasses
- Métodos más cortos y legibles
- Constantes con nombres descriptivos
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Dict, Tuple, Optional
import random


# ============================================================================
# CONSTANTES GLOBALES
# ============================================================================

class WorldConstants:
    """Constantes compartidas para generación de mundos"""
    # Checkpoints
    SPACE_BETWEEN_CHECKPOINTS = 800
    NUMBER_OF_CHECKPOINTS_PER_LEVEL = 3
    CHECKPOINT_SAFE_RADIUS = 250
    
    # Física de saltos
    MAX_JUMP_DISTANCE = 250
    MAX_JUMP_HEIGHT = 130
    
    # Espaciado
    MIN_VERTICAL_SPACING = 80
    MIN_HORIZONTAL_SPACING = 100
    
    # Enemigos
    ENEMY_SPAWN_CHANCE = 0.8
    ENEMY_SPAWN_CHANCE_GROUND = 0.8
    ENEMY_WIDTH = 40
    ENEMY_HEIGHT = 50
    
    # PowerUps
    POWERUP_MIN_DISTANCE_CHECKPOINT = 150
    POWERUP_MIN_DISTANCE_GOAL = 250
    POWERUP_MIN_DISTANCE_ENEMY = 120
    POWERUP_MIN_DISTANCE_SPIKE_X = 150
    POWERUP_MIN_DISTANCE_SPIKE_Y = 120
    POWERUP_MIN_DISTANCE_POWERUP = 200
    POWERUP_SAFE_ZONE = 600
    POWERUP_WIDTH = 35
    POWERUP_HEIGHT = 35
    
    # Música
    WORLD_MUSIC_PATH = 'Assets/WorldMusic/'


# ============================================================================
# CONFIGURACIONES POR TIPO DE MUNDO
# ============================================================================

@dataclass
class PlatformConfig:
    """Configuración para generación de plataformas"""
    starting_platforms: List[Dict[str, int]]
    num_segments: int
    platforms_per_segment: Tuple[int, int]  # (min, max)
    height_range: Tuple[int, int]  # (min, max) altura desde suelo
    width_range: Tuple[int, int]  # (min, max) ancho
    platform_height: int
    margin_left_pct: float
    margin_right_pct: float
    horizontal_spacing: int
    generation_start: int
    generation_end_offset: int


@dataclass
class HazardConfig:
    """Configuración para generación de hazards/espinas"""
    safe_zone: int
    generation_end_offset: int
    num_zones: int
    individual_spike_probability: float
    danger_zone_count: int
    danger_zone_spike_count: int  # Espinas por zona de peligro
    platform_spike_range: Tuple[int, int]  # (min, max)
    spike_width: int
    spike_height: int


@dataclass
class PowerUpConfig:
    """Configuración para distribución de PowerUps"""
    probabilities: Dict[str, float]


@dataclass
class WorldConfig:
    """Configuración completa de un mundo"""
    name: str
    colors: Dict[str, Tuple[int, int, int]]
    platform_config: PlatformConfig
    hazard_config: HazardConfig
    powerup_config: PowerUpConfig
    music_file: str


# ============================================================================
# CLASES AUXILIARES - SEPARACIÓN DE RESPONSABILIDADES (SRP)
# ============================================================================

class GeometryValidator:
    """Validaciones geométricas puras"""
    
    @staticmethod
    def rectangles_overlap(x1: int, y1: int, w1: int, h1: int,
                          x2: int, y2: int, w2: int, h2: int) -> bool:
        """Verifica si dos rectángulos se superponen"""
        return not (x1 + w1 < x2 or x2 + w2 < x1 or y1 + h1 < y2 or y2 + h2 < y1)
    
    @staticmethod
    def calculate_distance(x1: int, y1: int, x2: int, y2: int) -> float:
        """Calcula distancia euclidiana entre dos puntos"""
        return ((x1 - x2) ** 2 + (y1 - y2) ** 2) ** 0.5


class CheckpointValidator:
    """Validaciones relacionadas con checkpoints"""
    
    def __init__(self, checkpoints: List[Dict], radius: int = None):
        self.checkpoints = checkpoints
        self.default_radius = radius or WorldConstants.CHECKPOINT_SAFE_RADIUS
    
    def is_near_checkpoint(self, x: int, y: int, radius: int = None) -> bool:
        """Verifica si una posición está cerca de algún checkpoint"""
        radius = radius or self.default_radius
        
        for checkpoint in self.checkpoints:
            distance = GeometryValidator.calculate_distance(
                x, y, checkpoint['x'], checkpoint['y']
            )
            if distance < radius:
                return True
        return False


class PhysicsValidator:
    """Validaciones de física del juego"""
    
    @staticmethod
    def is_platform_reachable(from_x: int, from_y: int, to_x: int, to_y: int,
                             to_width: int) -> bool:
        """Verifica si una plataforma es alcanzable desde otra posición"""
        # Distancia horizontal
        horizontal_dist = abs(to_x - from_x)
        if horizontal_dist > WorldConstants.MAX_JUMP_DISTANCE:
            return False
        
        # Diferencia de altura (negativo = subir, positivo = bajar)
        vertical_dist = from_y - to_y
        
        # Si está más alto, verificar que no exceda altura de salto
        if vertical_dist < 0 and abs(vertical_dist) > WorldConstants.MAX_JUMP_HEIGHT:
            return False
        
        return True
    
    @staticmethod
    def is_on_surface(spike_x: int, spike_y: int, spike_height: int,
                     platforms: List[Dict], ground_y: int) -> bool:
        """Verifica si una espina está sobre una superficie (suelo o plataforma)"""
        spike_bottom = spike_y + spike_height
        
        # Verificar si está en el suelo
        if abs(spike_bottom - ground_y) < 5:
            return True
        
        # Verificar si está sobre alguna plataforma
        for platform in platforms:
            if abs(spike_bottom - platform['y']) < 5:
                if spike_x >= platform['x'] and spike_x <= platform['x'] + platform['width']:
                    return True
        
        return False


class CollisionValidator:
    """Validaciones de colisión para colocación de objetos"""
    
    def __init__(self, geometry: GeometryValidator, checkpoint_validator: CheckpointValidator):
        self.geometry = geometry
        self.checkpoint_validator = checkpoint_validator
    
    def validate_position(self, x: int, y: int, width: int, height: int,
                         existing_objects: List[Dict],
                         min_spacing: int = None) -> bool:
        """
        Validación unificada de posición para cualquier objeto
        
        Returns:
            True si la posición es válida, False si hay conflictos
        """
        # 1. Verificar checkpoints
        if self.checkpoint_validator.is_near_checkpoint(x, y):
            return False
        
        # 2. Verificar overlap con objetos existentes
        for obj in existing_objects:
            if self.geometry.rectangles_overlap(
                x, y, width, height,
                obj['x'], obj['y'], obj['width'], obj['height']
            ):
                return False
        
        # 3. Verificar espaciado mínimo si se especifica
        if min_spacing:
            for obj in existing_objects:
                distance = GeometryValidator.calculate_distance(
                    x, y, obj['x'], obj['y']
                )
                if distance < min_spacing:
                    return False
        
        return True

# ============================================================================
# FACTORY + REGISTRY PATTERN - Para selección de PowerUps
# ============================================================================

class PowerUpTypeRegistry:
    """
    Registry simple de tipos de PowerUp disponibles.
    NO es Singleton - cada generador puede tener su propio registry si lo necesita.
    """
    
    def __init__(self):
        self._available_types = set()
    
    def register(self, powerup_type: str):
        """Registra un tipo de PowerUp como disponible"""
        self._available_types.add(powerup_type)
    
    def is_registered(self, powerup_type: str) -> bool:
        """Verifica si un tipo está registrado"""
        return powerup_type in self._available_types
    
    def get_all_types(self) -> List[str]:
        """Retorna todos los tipos registrados"""
        return list(self._available_types)


class PowerUpSelector:
    """
    Factory para seleccionar tipos de PowerUp basándose en probabilidades.
    Usa el Registry para validar que los tipos existan.
    """
    
    def __init__(self, registry: PowerUpTypeRegistry):
        self._registry = registry
    
    def select_from_probabilities(self, probabilities: Dict[str, float]) -> str:
        """
        Selecciona un tipo de PowerUp basándose en un diccionario de probabilidades.
        
        Args:
            probabilities: Dict con formato {'speed': 0.4, 'jump': 0.3, 'life': 0.3}
        
        Returns:
            El tipo seleccionado (ej: 'speed')
        
        Raises:
            ValueError: Si algún tipo no está registrado o las probabilidades no suman ~1.0
        """
        # Validación 1: Verificar que todos los tipos estén registrados
        for ptype in probabilities.keys():
            if not self._registry.is_registered(ptype):
                raise ValueError(
                    f"Tipo de PowerUp '{ptype}' no registrado. "
                    f"Tipos disponibles: {self._registry.get_all_types()}"
                )
        
        # Validación 2: Verificar que sumen aproximadamente 1.0
        total = sum(probabilities.values())
        if not (0.99 <= total <= 1.01):
            raise ValueError(
                f"Las probabilidades deben sumar 1.0, pero suman {total:.3f}"
            )
        
        # Selección usando random.choices
        types = list(probabilities.keys())
        weights = list(probabilities.values())
        
        return random.choices(types, weights=weights, k=1)[0]

# ============================================================================
# GENERADORES BASE - TEMPLATE METHOD PATTERN
# ============================================================================

class WorldGenerator(ABC):
    """Clase abstracta que define el template method para generar mundos"""
    
    def __init__(self):
        # Validadores compartidos
        self.geometry = GeometryValidator()
        self.physics = PhysicsValidator()
        self.checkpoint_validator = None  # Se inicializa en generate_world
        self.collision_validator = None
        self._powerup_registry = PowerUpTypeRegistry()
        self._initialize_powerup_registry()
        self._powerup_selector = PowerUpSelector(self._powerup_registry)

    def _initialize_powerup_registry(self):
        """Registra los tipos de PowerUp disponibles en el juego"""
        self._powerup_registry.register('speed')
        self._powerup_registry.register('jump')
        self._powerup_registry.register('life')
    
    def generate_world(self, width: int, height: int) -> Dict:
        """
        TEMPLATE METHOD - Define el esqueleto del algoritmo
        Este método NO debe ser override en subclases
        """
        # Obtener configuración del mundo específico
        config = self.get_world_config()
        
        # Inicializar estructura de datos
        world_data = {
            'platforms': [],
            'spikes': [],
            'checkpoints': [],
            'powerups': [],
            'enemies': [],
            'goal': None,
            'colors': config.colors,
            'name': config.name,
            'music': None
        }
        
        # 1. Generar checkpoints (común a todos)
        world_data['checkpoints'] = self._generate_checkpoints(width, height)
        
        # Inicializar validadores con checkpoints
        self.checkpoint_validator = CheckpointValidator(world_data['checkpoints'])
        self.collision_validator = CollisionValidator(
            self.geometry, self.checkpoint_validator
        )
        
        # 2. Generar elementos del mundo en orden
        world_data['platforms'] = self._generate_platforms_with_config(
            width, height, config.platform_config, world_data['checkpoints']
        )
        
        world_data['spikes'] = self._generate_hazards_with_config(
            width, height, config.hazard_config,
            world_data['platforms'], world_data['checkpoints']
        )
        
        world_data['goal'] = self._generate_goal(width, height)
        
        world_data['enemies'] = self._generate_enemies(
            width, height, world_data['platforms'],
            world_data['checkpoints'], world_data['goal']
        )
        
        world_data['powerups'] = self._generate_powerups_with_config(
            width, height, config.powerup_config,
            world_data['platforms'], world_data['checkpoints'],
            world_data['goal'], world_data['enemies'], world_data['spikes']
        )
        

        world_data['music'] = f"{WorldConstants.WORLD_MUSIC_PATH}{config.music_file}"
        
        return world_data
    
    # ========================================================================
    # MÉTODO ABSTRACTO - SUBCLASES DEBEN IMPLEMENTAR
    # ========================================================================
    
    @abstractmethod
    def get_world_config(self) -> WorldConfig:
        """
        Retorna la configuración completa del mundo
        Cada subclase define su configuración específica
        """
        pass
    
    # ========================================================================
    # MÉTODOS COMUNES - IMPLEMENTACIÓN BASE
    # ========================================================================
    
    def _generate_checkpoints(self, width: int, height: int) -> List[Dict]:
        """Genera checkpoints (implementación común)"""
        checkpoints = []
        for i in range(1, WorldConstants.NUMBER_OF_CHECKPOINTS_PER_LEVEL + 1):
            checkpoints.append({
                'x': i * WorldConstants.SPACE_BETWEEN_CHECKPOINTS,
                'y': height - 150
            })
        return checkpoints
    
    def _generate_goal(self, width: int, height: int) -> Dict:
        """Genera la meta al final del mundo"""
        return {
            'x': width - 120,
            'y': height - 300,
            'width': 60,
            'height': 250
        }
    
    # ========================================================================
    # GENERACIÓN DE PLATAFORMAS - REFACTORIZADO
    # ========================================================================
    
    def _generate_platforms_with_config(self, width: int, height: int,
                                       config: PlatformConfig,
                                       checkpoints: List[Dict]) -> List[Dict]:
        """Genera plataformas usando configuración específica"""
        platforms = []
        
        # 1. Suelo principal
        platforms.append(self._create_ground(width, height))
        
        # 2. Plataformas de inicio
        platforms.extend(self._create_starting_platforms(
            config.starting_platforms, checkpoints
        ))
        
        # 3. Plataformas distribuidas
        platforms.extend(self._create_distributed_platforms(
            width, height, config, checkpoints, platforms
        ))
        
        return platforms
    
    def _create_ground(self, width: int, height: int) -> Dict:
        """Crea el suelo principal"""
        return {
            'x': 0,
            'y': height - 50,
            'width': width,
            'height': 50
        }
    
    def _create_starting_platforms(self, starting_configs: List[Dict],
                                   checkpoints: List[Dict]) -> List[Dict]:
        """Crea plataformas iniciales predefinidas"""
        platforms = []
        
        for config in starting_configs:
            # Validar que sea alcanzable y no esté cerca de checkpoints
            if not self.checkpoint_validator.is_near_checkpoint(
                config['x'], config['y']
            ):
                platforms.append(config)
        
        return platforms
    
    def _create_distributed_platforms(self, width: int, height: int,
                                     config: PlatformConfig,
                                     checkpoints: List[Dict],
                                     existing_platforms: List[Dict]) -> List[Dict]:
        """Genera plataformas distribuidas en el nivel"""
        platforms = []
        
        start = config.generation_start
        end = width - config.generation_end_offset
        generation_width = end - start
        
        segment_width = generation_width // config.num_segments
        
        for segment in range(config.num_segments):
            segment_start = start + (segment * segment_width)
            segment_end = segment_start + segment_width
            
            num_platforms = random.randint(*config.platforms_per_segment)
            attempts = 0
            platforms_added = 0
            
            while platforms_added < num_platforms and attempts < 50:
                attempts += 1
                
                # Generar posición candidata
                platform = self._generate_random_platform(
                    segment_start, segment_end, height, config
                )
                
                # Validar posición
                all_platforms = existing_platforms + platforms
                
                if self._validate_platform_placement(
                    platform, all_platforms, checkpoints, config
                ):
                    platforms.append(platform)
                    platforms_added += 1
        
        return platforms
    
    def _generate_random_platform(self, segment_start: int, segment_end: int,
                                 height: int, config: PlatformConfig) -> Dict:
        """Genera una plataforma con posición aleatoria"""
        margin_left = int((segment_end - segment_start) * config.margin_left_pct)
        margin_right = int((segment_end - segment_start) * config.margin_right_pct)
        
        x = random.randint(
            segment_start + margin_left,
            segment_end - margin_right
        )
        
        y = random.randint(
            height - config.height_range[1],
            height - config.height_range[0]
        )
        
        width = random.randint(*config.width_range)
        
        return {
            'x': x,
            'y': y,
            'width': width,
            'height': config.platform_height
        }
    
    def _validate_platform_placement(self, platform: Dict,
                                    existing_platforms: List[Dict],
                                    checkpoints: List[Dict],
                                    config: PlatformConfig) -> bool:
        """Valida que una plataforma pueda colocarse"""
        # 1. Checkpoint
        if self.checkpoint_validator.is_near_checkpoint(platform['x'], platform['y']):
            return False
        
        # 2. Overlap
        for existing in existing_platforms:
            if self.geometry.rectangles_overlap(
                platform['x'], platform['y'], platform['width'], platform['height'],
                existing['x'], existing['y'], existing['width'], existing['height']
            ):
                return False
        
        # 3. Espaciado
        for existing in existing_platforms:
            h_dist = abs(platform['x'] - existing['x'])
            v_dist = abs(platform['y'] - existing['y'])
            
            if h_dist < config.horizontal_spacing and v_dist < WorldConstants.MIN_VERTICAL_SPACING:
                return False
            
            if v_dist < 40 and h_dist < WorldConstants.MIN_HORIZONTAL_SPACING:
                return False
        
        # 4. Alcanzabilidad
        return self._is_platform_reachable_from_any(platform, existing_platforms)
    
    def _is_platform_reachable_from_any(self, platform: Dict,
                                   existing_platforms: List[Dict]) -> bool:
        """Verifica si la plataforma es alcanzable desde alguna existente"""
        # CAMBIO 1: Filtrar solo plataformas cercanas (aumentar rango)
        nearby_platforms = [
            p for p in existing_platforms
            if abs(p['x'] - platform['x']) < 600  # Aumentado de 400 a 600
        ]
        
        # CAMBIO 2: Si no hay plataformas cercanas pero hay plataformas
        # en el nivel, verificar si está dentro de rango razonable
        if not nearby_platforms:
            if existing_platforms:
                # Buscar la plataforma más cercana horizontalmente
                closest = min(existing_platforms, key=lambda p: abs(p['x'] - platform['x']))
                horizontal_dist = abs(closest['x'] - platform['x'])
                
                # Si está dentro de 2x el salto máximo, es válida
                # (permite "cadenas" de plataformas)
                if horizontal_dist < WorldConstants.MAX_JUMP_DISTANCE * 2.5:
                    nearby_platforms = [closest]
                else:
                    # Muy lejos, pero aceptar de todos modos para evitar
                    # segmentos vacíos (se asume continuidad)
                    return True
            else:
                # Primer plataforma flotante, siempre válida
                return True
        
        # CAMBIO 3: Verificar alcanzabilidad física
        for existing in nearby_platforms:
            if self.physics.is_platform_reachable(
                existing['x'], existing['y'],
                platform['x'], platform['y'], platform['width']
            ):
                return True
        
        return False

    
    # ========================================================================
    # GENERACIÓN DE HAZARDS - REFACTORIZADO
    # ========================================================================
    
    def _generate_hazards_with_config(self, width: int, height: int,
                                     config: HazardConfig,
                                     platforms: List[Dict],
                                     checkpoints: List[Dict]) -> List[Dict]:
        """Genera espinas usando configuración específica"""
        spikes = []
        ground_y = height - 50
        
        start = config.safe_zone
        end = width - config.generation_end_offset
        generation_width = end - start
        zone_width = generation_width // config.num_zones
        
        # 1. Espinas individuales
        spikes.extend(self._generate_individual_spikes(
            start, end, config.num_zones, zone_width, ground_y,
            config.individual_spike_probability, config.spike_width,
            config.spike_height, platforms, checkpoints
        ))
        
        # 2. Zonas de peligro
        spikes.extend(self._generate_danger_zones(
            start, config.num_zones, zone_width, ground_y,
            config.danger_zone_count, config.danger_zone_spike_count,
            config.spike_width, config.spike_height, platforms, checkpoints, spikes
        ))
        
        # 3. Espinas en plataformas
        spikes.extend(self._generate_platform_spikes(
            platforms, config.platform_spike_range, config.spike_width,
            config.spike_height, checkpoints, spikes
        ))
        
        return spikes
    
    def _generate_individual_spikes(self, start: int, end: int, num_zones: int,
                                   zone_width: int, ground_y: int,
                                   probability: float, spike_width: int,
                                   spike_height: int, platforms: List[Dict],
                                   checkpoints: List[Dict]) -> List[Dict]:
        """Genera espinas individuales en el suelo"""
        spikes = []
        
        for zone in range(num_zones):
            zone_start = start + (zone * zone_width)
            zone_end = zone_start + zone_width
            
            if random.random() < probability:
                attempts = 0
                while attempts < 10:
                    attempts += 1
                    
                    spike = self._create_spike(
                        random.randint(zone_start + 40, zone_end - 40),
                        ground_y - spike_height,
                        spike_width, spike_height
                    )
                    
                    if self._validate_spike_placement(
                        spike, ground_y, platforms, checkpoints, spikes
                    ):
                        spikes.append(spike)
                        break
        
        return spikes
    
    def _generate_danger_zones(self, start: int, num_zones: int, zone_width: int,
                              ground_y: int, danger_zone_count: int,
                              spikes_per_zone: int, spike_width: int,
                              spike_height: int, platforms: List[Dict],
                              checkpoints: List[Dict],
                              existing_spikes: List[Dict]) -> List[Dict]:
        """Genera zonas de peligro con múltiples espinas juntas"""
        spikes = []
        
        if num_zones < 4:
            return spikes
        
        danger_zones = random.sample(
            range(2, num_zones - 1),
            min(danger_zone_count, num_zones - 3)
        )
        
        for danger_zone in danger_zones:
            zone_start = start + (danger_zone * zone_width)
            zone_center = zone_start + zone_width // 2
            
            if self.checkpoint_validator.is_near_checkpoint(
                zone_center, ground_y - spike_height, 200
            ):
                continue
            
            # Generar espinas en la zona
            for i in range(spikes_per_zone):
                spike = self._create_spike(
                    zone_start + (i * 50) + 40,
                    ground_y - spike_height,
                    spike_width, spike_height
                )
                
                all_spikes = existing_spikes + spikes
                
                if self._validate_spike_placement(
                    spike, ground_y, platforms, checkpoints, all_spikes
                ):
                    spikes.append(spike)
        
        return spikes
    
    def _generate_platform_spikes(self, platforms: List[Dict],
                                 spike_range: Tuple[int, int],
                                 spike_width: int, spike_height: int,
                                 checkpoints: List[Dict],
                                 existing_spikes: List[Dict]) -> List[Dict]:
        """Genera espinas sobre plataformas"""
        spikes = []
        
        # Filtrar plataformas elegibles
        eligible = [
            p for p in platforms
            if p['y'] < 500 and p['width'] >= 80 and
            not self.checkpoint_validator.is_near_checkpoint(
                p['x'] + p['width'] // 2, p['y'], 200
            )
        ]
        
        if not eligible:
            return spikes
        
        num_spikes = min(random.randint(*spike_range), len(eligible))
        selected = random.sample(eligible, num_spikes)
        
        for platform in selected:
            available_space = platform['width'] - 60
            if available_space < 40:
                continue
            
            offset = random.randint(20, int(available_space))
            
            spike = self._create_spike(
                platform['x'] + offset,
                platform['y'] - spike_height,
                spike_width, spike_height
            )
            
            # Validar overlap con otras espinas
            overlap = False
            for existing in existing_spikes + spikes:
                if self.geometry.rectangles_overlap(
                    spike['x'], spike['y'], spike['width'], spike['height'],
                    existing['x'], existing['y'], existing['width'], existing['height']
                ):
                    overlap = True
                    break
            
            if not overlap:
                spike['on_platform'] = True
                spikes.append(spike)
        
        return spikes
    
    def _create_spike(self, x: int, y: int, width: int, height: int) -> Dict:
        """Crea una espina con las dimensiones especificadas"""
        return {
            'x': x,
            'y': y,
            'width': width,
            'height': height
        }
    
    def _validate_spike_placement(self, spike: Dict, ground_y: int,
                                  platforms: List[Dict],
                                  checkpoints: List[Dict],
                                  existing_spikes: List[Dict]) -> bool:
        """Valida que una espina pueda colocarse"""
        # 1. Checkpoint
        if self.checkpoint_validator.is_near_checkpoint(
            spike['x'], spike['y'], 150
        ):
            return False
        
        # 2. Debe estar sobre superficie
        if not self.physics.is_on_surface(
            spike['x'], spike['y'], spike['height'], platforms, ground_y
        ):
            return False
        
        # 3. No overlap con otras espinas
        for existing in existing_spikes:
            if self.geometry.rectangles_overlap(
                spike['x'], spike['y'], spike['width'], spike['height'],
                existing['x'], existing['y'], existing['width'], existing['height']
            ):
                return False
        
        return True
    
    # ========================================================================
    # GENERACIÓN DE ENEMIGOS - COMÚN
    # ========================================================================
    
    def _generate_enemies(self, width: int, height: int,
                         platforms: List[Dict],
                         checkpoints: List[Dict],
                         goal: Dict) -> List[Dict]:
        """Genera enemigos sobre plataformas"""
        enemies = []
        safe_zone_x = 500
        
        for platform in platforms:
            # Validaciones básicas
            if platform['width'] < 80:
                continue
            
            if platform['x'] + platform['width'] <= safe_zone_x:
                continue
            
            is_ground = (platform['y'] >= height - 60)
            
            probability = (WorldConstants.ENEMY_SPAWN_CHANCE_GROUND if is_ground
                          else WorldConstants.ENEMY_SPAWN_CHANCE)
            
            if random.random() > probability:
                continue
            
            # Posición válida en la plataforma
            min_x = max(platform['x'] + 40, safe_zone_x + 40)
            max_x = platform['x'] + platform['width'] - 40
            
            if max_x <= min_x:
                continue
            
            enemy_x = random.randint(int(min_x), int(max_x))
            enemy_y = platform['y'] - 50
            
            # Validar distancias
            if self._validate_enemy_placement(
                enemy_x, enemy_y, checkpoints, goal, enemies
            ):
                enemies.append({
                    'x': enemy_x,
                    'y': enemy_y,
                    'width': WorldConstants.ENEMY_WIDTH,
                    'height': WorldConstants.ENEMY_HEIGHT
                })
        
        return enemies
    
    def _validate_enemy_placement(self, x: int, y: int,
                                  checkpoints: List[Dict],
                                  goal: Dict,
                                  existing_enemies: List[Dict]) -> bool:
        """Valida que un enemigo pueda colocarse"""
        # Checkpoints
        for checkpoint in checkpoints:
            if (abs(x - checkpoint['x']) < 200 and
                abs(y - checkpoint['y']) < 150):
                return False
        
        # Goal
        if goal and abs(x - goal['x']) < 300 and abs(y - goal['y']) < 150:
            return False
        
        # Otros enemigos
        for enemy in existing_enemies:
            if abs(x - enemy['x']) < 100:
                return False
        
        return True
    
    # ========================================================================
    # GENERACIÓN DE POWERUPS - REFACTORIZADO
    # ========================================================================
    
    def _generate_powerups_with_config(self, width: int, height: int,
                                      config: PowerUpConfig,
                                      platforms: List[Dict],
                                      checkpoints: List[Dict],
                                      goal: Dict,
                                      enemies: List[Dict],
                                      spikes: List[Dict]) -> List[Dict]:
        """Genera PowerUps usando configuración de probabilidades"""
        powerups = []
        num_powerups = (width // 1000) + random.randint(2, 4)
        
        attempts = 0
        max_attempts = num_powerups * 15
        
        while len(powerups) < num_powerups and attempts < max_attempts:
            attempts += 1
            
            # Generar posición
            x = random.randint(WorldConstants.POWERUP_SAFE_ZONE, width - 200)
            placement_type = random.choice(['on_platform', 'floating'])
            
            if placement_type == 'on_platform':
                platform = self._find_suitable_platform(x, platforms, height)
                if not platform:
                    continue
                x = platform['x'] + platform['width'] // 2
                y = platform['y'] - 40
            else:
                y = random.randint(height - 400, height - 150)
            
            # Validar posición
            if self._validate_powerup_placement(
                x, y, checkpoints, goal, enemies, spikes, powerups
            ):
                powerup_type = self._powerup_selector.select_from_probabilities(
                    config.probabilities
                )
                powerups.append({
                    'x': x,
                    'y': y,
                    'width': WorldConstants.POWERUP_WIDTH,
                    'height': WorldConstants.POWERUP_HEIGHT,
                    'type': powerup_type
                })
        
        return powerups
    
    def _find_suitable_platform(self, x: int, platforms: List[Dict],
                               height: int) -> Optional[Dict]:
        """Encuentra plataforma cercana adecuada para PowerUp"""
        suitable = None
        min_distance = float('inf')
        
        for platform in platforms:
            if platform['y'] >= height - 100:
                continue
            
            distance = abs(platform['x'] - x)
            if distance < min_distance and distance < 300:
                min_distance = distance
                suitable = platform
        
        return suitable
    
    def _validate_powerup_placement(self, x: int, y: int,
                                   checkpoints: List[Dict],
                                   goal: Dict,
                                   enemies: List[Dict],
                                   spikes: List[Dict],
                                   existing_powerups: List[Dict]) -> bool:
        """Valida que un PowerUp pueda colocarse"""
        # Checkpoints
        for checkpoint in checkpoints:
            if (abs(x - checkpoint['x']) < WorldConstants.POWERUP_MIN_DISTANCE_CHECKPOINT and
                abs(y - checkpoint['y']) < 100):
                return False
        
        # Goal
        if goal and (abs(x - goal['x']) < WorldConstants.POWERUP_MIN_DISTANCE_GOAL and
                    abs(y - goal['y']) < 150):
            return False
        
        # Enemigos
        for enemy in enemies:
            if abs(x - enemy['x']) < WorldConstants.POWERUP_MIN_DISTANCE_ENEMY:
                return False
        
        # Spikes
        for spike in spikes:
            if (abs(x - spike['x']) < WorldConstants.POWERUP_MIN_DISTANCE_SPIKE_X and
                abs(y - spike['y']) < WorldConstants.POWERUP_MIN_DISTANCE_SPIKE_Y):
                return False
        
        # Otros PowerUps
        for powerup in existing_powerups:
            if abs(x - powerup['x']) < WorldConstants.POWERUP_MIN_DISTANCE_POWERUP:
                return False
        
        return True
    


# ============================================================================
# GENERADORES CONCRETOS - CONFIGURACIÓN POR MUNDO
# ============================================================================

class GrassWorldGenerator(WorldGenerator):
    """Generador de mundo de pasto (nivel fácil)"""
    
    def get_world_config(self) -> WorldConfig:
        """Configuración del mundo de pasto - Nivel fácil"""
        return WorldConfig(
            name="Mundo de Pasto",
            colors={
                'sky': (135, 206, 235),
                'ground': (34, 139, 34),
                'platform': (101, 67, 33),
                'hazard': (255, 0, 0)
            },
            platform_config=PlatformConfig(
                starting_platforms=[
                    {'x': 150, 'y': 450, 'width': 150, 'height': 20},
                    {'x': 350, 'y': 380, 'width': 130, 'height': 20}
                ],
                num_segments=6,
                platforms_per_segment=(1, 3),
                height_range=(130, 280),
                width_range=(130, 180),
                platform_height=20,
                margin_left_pct=0.10,
                margin_right_pct=0.15,
                horizontal_spacing=200,
                generation_start=600,
                generation_end_offset=400
            ),
            hazard_config=HazardConfig(
                safe_zone=500,
                generation_end_offset=300,
                num_zones=10,
                individual_spike_probability=0.25,
                danger_zone_count=2,
                danger_zone_spike_count=2,
                platform_spike_range=(0, 2),
                spike_width=40,
                spike_height=30
            ),
            powerup_config=PowerUpConfig(
                probabilities={
                    'speed': 0.25,
                    'jump': 0.50,
                    'life': 0.25
                }
            ),
            music_file='grass_theme.mp3'
        )


class DesertWorldGenerator(WorldGenerator):
    """Generador de mundo desértico (nivel medio)"""
    
    def get_world_config(self) -> WorldConfig:
        """Configuración del mundo desértico - Nivel medio"""
        return WorldConfig(
            name="Mundo Desértico",
            colors={
                'sky': (255, 218, 185),
                'ground': (210, 180, 140),
                'platform': (139, 90, 43),
                'hazard': (255, 140, 0)
            },
            platform_config=PlatformConfig(
                starting_platforms=[
                    {'x': 180, 'y': 420, 'width': 120, 'height': 18},
                    {'x': 380, 'y': 360, 'width': 110, 'height': 18}
                ],
                num_segments=7,
                platforms_per_segment=(1, 2),
                height_range=(130, 300),
                width_range=(100, 140),
                platform_height=18,
                margin_left_pct=0.15,
                margin_right_pct=0.25,
                horizontal_spacing=220,
                generation_start=600,
                generation_end_offset=400
            ),
            hazard_config=HazardConfig(
                safe_zone=400,
                generation_end_offset=250,
                num_zones=12,
                individual_spike_probability=0.45,
                danger_zone_count=3,
                danger_zone_spike_count=2,
                platform_spike_range=(2, 3),
                spike_width=38,
                spike_height=32
            ),
            powerup_config=PowerUpConfig(
                probabilities={
                    'speed': 0.25,
                    'jump': 0.25,
                    'life': 0.50
                }
            ),
            music_file='desert_theme.mp3'
        )


class IceWorldGenerator(WorldGenerator):
    """Generador de mundo de hielo (nivel difícil)"""
    
    def get_world_config(self) -> WorldConfig:
        """Configuración del mundo de hielo - Nivel difícil"""
        return WorldConfig(
            name="Mundo de Hielo",
            colors={
                'sky': (176, 224, 230),
                'ground': (240, 248, 255),
                'platform': (175, 238, 238),
                'hazard': (70, 130, 180)
            },
            platform_config=PlatformConfig(
                starting_platforms=[
                    {'x': 220, 'y': 400, 'width': 85, 'height': 15},
                    {'x': 450, 'y': 320, 'width': 80, 'height': 15}
                ],
                num_segments=8,
                platforms_per_segment=(1, 2),  # Solo 1 por segmento
                height_range=(140, 350),
                width_range=(65, 95),
                platform_height=15,
                margin_left_pct=0.25,
                margin_right_pct=0.35,
                horizontal_spacing=270,
                generation_start=700,
                generation_end_offset=400
            ),
            hazard_config=HazardConfig(
                safe_zone=350,
                generation_end_offset=200,
                num_zones=16,
                individual_spike_probability=0.65,
                danger_zone_count=5,
                danger_zone_spike_count=2,
                platform_spike_range=(5, 7),
                spike_width=35,
                spike_height=35
            ),
            powerup_config=PowerUpConfig(
                probabilities={
                    'speed': 0.25,
                    'jump': 0.25,
                    'life': 0.50
                }
            ),
            music_file='ice_theme.mp3'
        )
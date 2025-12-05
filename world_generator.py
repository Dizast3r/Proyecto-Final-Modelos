"""
TEMPLATE METHOD PATTERN - Para generar diferentes tipos de mundos
Define el esqueleto del algoritmo de generación de mundos,
permitiendo que las subclases implementen pasos específicos
"""

from abc import ABC, abstractmethod
import random

SPACE_BETWEEN_CHECKPOINTS = 800
NUMBER_OF_CHECKPOINTS_PER_LEVEL = 3
WORLD_MUSIC_PATH = 'Assets/WorldMusic/'
MAX_JUMP_DISTANCE = 250  # Distancia horizontal máxima de salto para calculo en plataformas
MAX_JUMP_HEIGHT = 130    # Altura máxima de salto para calculo en plataformas
CHECKPOINT_SAFE_RADIUS = 250  # Radio de exclusión alrededor de checkpoints
MIN_VERTICAL_SPACING = 80  # Espacio mínimo vertical entre plataformas cercanas
MIN_HORIZONTAL_SPACING = 100  # Espacio mínimo horizontal si están en alturas similares

ENEMY_SPAWN_CHANCE = 0.35  # 35% probabilidad por plataforma
ENEMY_SPAWN_CHANCE_GROUND = 0.20  # 20% probabilidad en el suelo

POWERUP_MIN_DISTANCE_CHECKPOINT = 150
POWERUP_MIN_DISTANCE_GOAL = 250
POWERUP_MIN_DISTANCE_ENEMY = 120
POWERUP_MIN_DISTANCE_POWERUP = 200
POWERUP_SAFE_ZONE = 600


class WorldGenerator(ABC):
    """Clase abstracta que define el template method para generar mundos"""
    
    def generate_world(self, width, height):
        """TEMPLATE METHOD - Define el esqueleto del algoritmo"""
        world_data = {
            'platforms': [],
            'spikes': [],
            'checkpoints': [],
            'powerups': [],      
            'enemies': [],       
            'goal': None,        
            'colors': {},
            'name': '',
            'music': None        
        }
        
        world_data['colors'] = self.define_colors()
        world_data['name'] = self.get_world_name()
        world_data['checkpoints'] = self.generate_checkpoints(width, height)
        world_data['platforms'] = self.generate_platforms(width, height, world_data['checkpoints'])
        world_data['spikes'] = self.generate_hazards(width, height, world_data['platforms'], world_data['checkpoints'])
        world_data['goal'] = self.add_goal(width, height)
        world_data['enemies'] = self.add_enemies(width, height, world_data['platforms'], world_data['checkpoints'], world_data['goal'])
        
        # PowerUps AL FINAL
        world_data['powerups'] = self.add_powerups(
            width, 
            height, 
            world_data['platforms'],
            world_data['checkpoints'],
            world_data['goal'],
            world_data['enemies']
        )
        
        self.add_special_features(world_data, width, height)
        
        return world_data

    
    @abstractmethod
    def define_colors(self):
        """Define los colores del mundo"""
        pass
    
    @abstractmethod
    def get_world_name(self):
        """Retorna el nombre del mundo"""
        pass
    
    @abstractmethod
    def generate_platforms(self, width, height, checkpoints):
        """Genera las plataformas evitando checkpoints"""
        pass
    
    @abstractmethod
    def generate_hazards(self, width, height, platforms, checkpoints):
        """Genera espinas evitando checkpoints y validando superficies"""
        pass
    
    def generate_checkpoints(self, width, height):
        """Genera checkpoints (implementación por defecto)"""
        checkpoints = []
        for i in range(1, NUMBER_OF_CHECKPOINTS_PER_LEVEL + 1):
            checkpoints.append({
                'x': i * SPACE_BETWEEN_CHECKPOINTS, 
                'y': height - 150
            })
        return checkpoints
    
    @abstractmethod
    def get_powerup_type(self):
        """Retorna el tipo de PowerUp que este mundo puede generar"""
        pass
    
    def add_powerups(self, width, height, platforms, checkpoints, goal, enemies):
        """
        Genera PowerUps en posiciones válidas
        El tipo específico lo decide cada mundo con get_powerup_type()
        """
        powerups = []
        
        # 1. NÚMERO DE POWERUPS basado en tamaño del mundo
        num_powerups = (width // 1000) + random.randint(2, 4)
        
        attempts = 0
        max_attempts = num_powerups * 15
        
        while len(powerups) < num_powerups and attempts < max_attempts:
            attempts += 1
            
            # Posición X después de zona segura
            x = random.randint(POWERUP_SAFE_ZONE, width - 200)
            
            # Decidir si va sobre plataforma o flotando
            placement_type = random.choice(['on_platform', 'floating'])
            
            if placement_type == 'on_platform':
                # Buscar plataforma cercana a X
                suitable_platform = None
                min_distance = float('inf')
                
                for platform in platforms:
                    if platform['y'] < height - 100:  # No en el suelo
                        distance = abs(platform['x'] - x)
                        if distance < min_distance and distance < 300:
                            min_distance = distance
                            suitable_platform = platform
                
                if not suitable_platform:
                    continue
                
                # Colocar encima de la plataforma
                x = suitable_platform['x'] + suitable_platform['width'] // 2
                y = suitable_platform['y'] - 40
            else:
                # Flotando
                y = random.randint(height - 400, height - 150)
            
            # === VALIDACIÓN 1: No cerca de checkpoints ===
            too_close_checkpoint = False
            for checkpoint in checkpoints:
                dist_x = abs(x - checkpoint['x'])
                dist_y = abs(y - checkpoint['y'])
                if dist_x < POWERUP_MIN_DISTANCE_CHECKPOINT and dist_y < 100:
                    too_close_checkpoint = True
                    break
            
            if too_close_checkpoint:
                continue
            
            # === VALIDACIÓN 2: No cerca de goal ===
            if goal:
                dist_goal_x = abs(x - goal['x'])
                dist_goal_y = abs(y - goal['y'])
                if dist_goal_x < POWERUP_MIN_DISTANCE_GOAL and dist_goal_y < 150:
                    continue
            
            # === VALIDACIÓN 3: No cerca de enemigos ===
            too_close_enemy = False
            for enemy in enemies:
                dist = abs(x - enemy['x'])
                if dist < POWERUP_MIN_DISTANCE_ENEMY:
                    too_close_enemy = True
                    break
            
            if too_close_enemy:
                continue
            
            # === VALIDACIÓN 4: No cerca de otros powerups ===
            too_close_powerup = False
            for existing_powerup in powerups:
                dist = abs(x - existing_powerup['x'])
                if dist < POWERUP_MIN_DISTANCE_POWERUP:
                    too_close_powerup = True
                    break
            
            if too_close_powerup:
                continue
            
            # === VALIDACIONES PASADAS - Obtener tipo del mundo ===
            powerup_type = self.get_powerup_type()
            
            powerup = {
                'x': x,
                'y': y,
                'width': 35,
                'height': 35,
                'type': powerup_type
            }
            powerups.append(powerup)
        
        return powerups

    
    def add_enemies(self, width, height, platforms, checkpoints, goal):
        """Genera enemigos sobre plataformas (implementación común para todos)"""
        enemies = []
        
        # 1. ZONA SEGURA - No spawnear enemigos cerca del inicio
        safe_zone_x = 500
        
        # 2. REVISAR TODAS LAS PLATAFORMAS
        for platform in platforms:
            platform_x = platform['x']
            platform_y = platform['y']
            platform_width = platform['width']
            platform_height = platform['height']
            
            # === VALIDACIÓN 1: No en zona segura ===
            if platform_x < safe_zone_x:
                continue
            
            # === VALIDACIÓN 2: Plataforma suficientemente grande ===
            if platform_width < 80:
                continue
            
            # === VALIDACIÓN 3: Probabilidad según tipo de superficie ===
            is_ground = (platform_y >= height - 60)
            
            if is_ground:
                current_probability = ENEMY_SPAWN_CHANCE_GROUND  # ← USO DE CONSTANTE
            else:
                current_probability = ENEMY_SPAWN_CHANCE  # ← USO DE CONSTANTE
            
            # === VALIDACIÓN 4: Probabilidad de spawn ===
            if random.random() > current_probability:
                continue
            
            # === VALIDACIÓN 5: No cerca de checkpoints ===
            too_close_to_checkpoint = False
            checkpoint_safe_radius = 200
            
            for checkpoint in checkpoints:
                distance_x = abs(platform_x - checkpoint['x'])
                distance_y = abs(platform_y - checkpoint['y'])
                
                if distance_x < checkpoint_safe_radius and distance_y < 150:
                    too_close_to_checkpoint = True
                    break
            
            if too_close_to_checkpoint:
                continue
            
            # === VALIDACIÓN 6: No cerca de la meta ===
            if goal:
                goal_safe_radius = 300
                distance_to_goal_x = abs(platform_x - goal['x'])
                distance_to_goal_y = abs(platform_y - goal['y'])
                
                if distance_to_goal_x < goal_safe_radius and distance_to_goal_y < 150:
                    continue
            
            # === VALIDACIÓN 7: No muy cerca del borde de la plataforma ===
            margin = 40
            available_width = platform_width - (2 * margin)
            
            if available_width < 40:
                continue
            
            # Calcular posición del enemigo
            enemy_x = platform_x + margin + random.randint(0, int(available_width))
            enemy_y = platform_y - 50
            
            # === VALIDACIÓN 8: No superpuesto con otros enemigos ===
            too_close_to_other_enemy = False
            min_distance_between_enemies = 100
            
            for existing_enemy in enemies:
                distance = abs(enemy_x - existing_enemy['x'])
                if distance < min_distance_between_enemies:
                    too_close_to_other_enemy = True
                    break
            
            if too_close_to_other_enemy:
                continue
            
            # === TODAS LAS VALIDACIONES PASADAS ===
            enemy = {
                'x': enemy_x,
                'y': enemy_y,
                'width': 40,
                'height': 50
            }
            enemies.append(enemy)
        
        return enemies

    
    def add_goal(self, width, height):
        """Genera la meta al final del mundo"""
        goal = {
            'x': width - 120,
            'y': height - 300,
            'width': 60,
            'height': 250
        }
        return goal
    
    @abstractmethod
    def add_special_features(self, world_data, width, height):
        """Hook method - características únicas del mundo (música, física, etc)"""
        pass

    #Funciones Auxiliares
    def rectangles_overlap(self, x1, y1, w1, h1, x2, y2, w2, h2):
        """Verifica si dos rectángulos se superponen"""
        return not (x1 + w1 < x2 or x2 + w2 < x1 or y1 + h1 < y2 or y2 + h2 < y1)
    
    def is_near_checkpoint(self, x, y, checkpoints, radius=None):
        """Verifica si una posición está cerca de algún checkpoint"""
        if radius is None:
            radius = CHECKPOINT_SAFE_RADIUS
        
        for checkpoint in checkpoints:
            distance = ((x - checkpoint['x']) ** 2 + (y - checkpoint['y']) ** 2) ** 0.5
            if distance < radius:
                return True
        return False
    
    def is_platform_reachable(self, from_x, from_y, to_x, to_y, to_width):
        """Verifica si una plataforma es alcanzable desde otra posición"""
        # Distancia horizontal
        horizontal_dist = abs(to_x - from_x)
        if horizontal_dist > MAX_JUMP_DISTANCE:
            return False
        
        # Diferencia de altura (negativo = subir, positivo = bajar)
        vertical_dist = from_y - to_y
        
        # Si está más alto, verificar que no exceda altura de salto
        if vertical_dist < 0 and abs(vertical_dist) > MAX_JUMP_HEIGHT:
            return False
        
        return True
    
    def is_on_surface(self, spike_x, spike_y, spike_width, platforms, ground_y):
        """Verifica si una espina está sobre una superficie (suelo o plataforma)"""
        spike_bottom = spike_y + spike_width  # Asumiendo espinas cuadradas/triangulares
        
        # Verificar si está en el suelo
        if abs(spike_bottom - ground_y) < 5:
            return True
        
        # Verificar si está sobre alguna plataforma
        for platform in platforms:
            # La espina debe estar "sobre" la plataforma
            if abs(spike_bottom - platform['y']) < 5:
                # Y debe estar dentro del rango horizontal de la plataforma
                if spike_x >= platform['x'] and spike_x <= platform['x'] + platform['width']:
                    return True
        
        return False



class GrassWorldGenerator(WorldGenerator):
    """Generador de mundo de pasto (nivel fácil)"""

    def get_powerup_type(self):
        """Grass: PowerUps balanceados, énfasis en velocidad"""
        rand = random.random()
        if rand < 0.40:
            return 'speed'
        elif rand < 0.70:
            return 'jump'
        else:
            return 'life'

    
    def define_colors(self):
        """Colores verdes y naturales"""
        return {
            'sky': (135, 206, 235),      # Azul cielo
            'ground': (34, 139, 34),     # Verde
            'platform': (101, 67, 33),   # Marrón tierra
            'hazard': (255, 0, 0)        # Rojo peligro
        }
    
    def get_world_name(self):
        """Nombre del mundo"""
        return "Mundo de Pasto"
    
    def generate_platforms(self, width, height, checkpoints):
        """Genera plataformas con espaciamiento riguroso y sin amontonamiento"""
        platforms = []
        
        # 1. SUELO PRINCIPAL
        ground = {
            'x': 0,
            'y': height - 50,
            'width': width,
            'height': 50
        }
        platforms.append(ground)
        
        # 2. PLATAFORMAS DE INICIO - Bien espaciadas
        spawn_x = 100
        spawn_y = 100
        
        first_platform = {
            'x': 150,
            'y': height - 150,
            'width': 150,
            'height': 20
        }
        
        if self.is_platform_reachable(spawn_x, spawn_y, first_platform['x'], first_platform['y'], first_platform['width']):
            platforms.append(first_platform)
        
        second_platform = {
            'x': 350,
            'y': height - 220,  # Más espaciada verticalmente (220 vs 200)
            'width': 130,
            'height': 20
        }
        
        if self.is_platform_reachable(first_platform['x'], first_platform['y'], second_platform['x'], second_platform['y'], second_platform['width']):
            platforms.append(second_platform)
        
        # 3. PLATAFORMAS DISTRIBUIDAS - Con espaciamiento estricto
        start_generation = 600
        end_generation = width - 400
        generation_width = end_generation - start_generation
        
        num_segments = 6
        segment_width = generation_width // num_segments
        
        for segment in range(num_segments):
            segment_start = start_generation + (segment * segment_width)
            segment_end = segment_start + segment_width
            
            # NUEVO: Máximo 3 plataformas por segmento (antes 2-3)
            num_platforms = random.randint(1, 3)
            attempts_per_segment = 0
            platforms_added_in_segment = 0
            
            # Guardar plataformas de este segmento para validar espaciamiento
            segment_platforms = []
            
            while platforms_added_in_segment < num_platforms and attempts_per_segment < 20:
                attempts_per_segment += 1
                
                margin_left = int(segment_width * 0.10)
                margin_right = int(segment_width * 0.15)
                
                available_width = segment_width - margin_left - margin_right
                if available_width < 100:
                    break
                
                # Generar posición candidata
                x = random.randint(
                    segment_start + margin_left,
                    segment_end - margin_right
                )
                
                y = random.randint(
                    height - 280,
                    height - 130
                )
                
                platform_width = random.randint(130, 180)
                platform_height = 20
                
                # === VALIDACIÓN 1: No cerca de checkpoints ===
                if self.is_near_checkpoint(x, y, checkpoints):
                    continue
                
                # === VALIDACIÓN 2: No superpuesta con NINGUNA plataforma ===
                overlaps = False
                for existing_platform in platforms:
                    if self.rectangles_overlap(
                        x, y, platform_width, platform_height,
                        existing_platform['x'], existing_platform['y'],
                        existing_platform['width'], existing_platform['height']
                    ):
                        overlaps = True
                        break
                
                if overlaps:
                    continue
                
                # === VALIDACIÓN 3: Espaciamiento vertical y horizontal adecuado ===
                # Verificar con todas las plataformas existentes
                too_close = False
                
                for existing_platform in platforms:
                    # Calcular distancias
                    horizontal_distance = abs(x - existing_platform['x'])
                    vertical_distance = abs(y - existing_platform['y'])
                    
                    # Si están horizontalmente cercanas (en la misma "columna")
                    if horizontal_distance < 200:
                        # Deben estar bien separadas verticalmente
                        if vertical_distance < MIN_VERTICAL_SPACING:
                            too_close = True
                            break
                    
                    # Si están a altura similar (en la misma "fila")
                    if vertical_distance < 40:
                        # Deben estar bien separadas horizontalmente
                        if horizontal_distance < MIN_HORIZONTAL_SPACING:
                            too_close = True
                            break
                
                if too_close:
                    continue
                
                # === VALIDACIÓN 4: Alcanzable desde alguna plataforma o suelo ===
                is_reachable = False
                
                # Desde el suelo
                if self.is_platform_reachable(x, height - 50, x, y, platform_width):
                    is_reachable = True
                
                # Desde plataforma previa
                if not is_reachable:
                    for prev_platform in platforms:
                        # Solo considerar plataformas razonablemente cercanas
                        if prev_platform['x'] < x + 350:
                            if self.is_platform_reachable(
                                prev_platform['x'] + prev_platform['width'],
                                prev_platform['y'],
                                x,
                                y,
                                platform_width
                            ):
                                is_reachable = True
                                break
                
                # ALTERNATIVA: También verificar si es alcanzable desde plataformas a la derecha
                # (para casos donde saltas hacia atrás)
                if not is_reachable:
                    for prev_platform in platforms:
                        if prev_platform['x'] > x - 350 and prev_platform['x'] < x + segment_width:
                            if self.is_platform_reachable(
                                prev_platform['x'],
                                prev_platform['y'],
                                x,
                                y,
                                platform_width
                            ):
                                is_reachable = True
                                break
                
                if not is_reachable:
                    continue
                
                # === TODAS LAS VALIDACIONES PASADAS ===
                new_platform = {
                    'x': x,
                    'y': y,
                    'width': platform_width,
                    'height': platform_height
                }
                
                platforms.append(new_platform)
                segment_platforms.append(new_platform)
                platforms_added_in_segment += 1
        
        # 4. PLATAFORMAS FINALES - Validadas y espaciadas
        final_platform_1 = {
            'x': width - 400,
            'y': height - 170,
            'width': 150,
            'height': 20
        }
        
        # Validar checkpoint y espaciamiento
        if not self.is_near_checkpoint(final_platform_1['x'], final_platform_1['y'], checkpoints):
            # Validar espaciamiento con otras plataformas
            can_add = True
            for existing_platform in platforms:
                horizontal_distance = abs(final_platform_1['x'] - existing_platform['x'])
                vertical_distance = abs(final_platform_1['y'] - existing_platform['y'])
                
                if horizontal_distance < 200 and vertical_distance < MIN_VERTICAL_SPACING:
                    can_add = False
                    break
            
            if can_add:
                platforms.append(final_platform_1)
        
        final_platform_2 = {
            'x': width - 220,
            'y': height - 140,
            'width': 120,
            'height': 20
        }
        
        if not self.is_near_checkpoint(final_platform_2['x'], final_platform_2['y'], checkpoints):
            can_add = True
            for existing_platform in platforms:
                horizontal_distance = abs(final_platform_2['x'] - existing_platform['x'])
                vertical_distance = abs(final_platform_2['y'] - existing_platform['y'])
                
                if horizontal_distance < 200 and vertical_distance < MIN_VERTICAL_SPACING:
                    can_add = False
                    break
            
            if can_add:
                platforms.append(final_platform_2)
        
        return platforms


    
    def generate_hazards(self, width, height, platforms, checkpoints):
        """Genera espinas con validaciones rigurosas"""
        spikes = []
        ground_y = height - 50  # Altura del suelo
        
        # 1. ZONA SEGURA DE INICIO - Sin espinas
        safe_zone = 500
        
        # 2. ZONA DE GENERACIÓN
        start_generation = safe_zone
        end_generation = width - 300
        generation_width = end_generation - start_generation
        
        # 3. DIVIDIR EN ZONAS
        num_zones = 10
        zone_width = generation_width // num_zones
        
        # 4. ESPINAS INDIVIDUALES CON VALIDACIONES
        for zone in range(num_zones):
            zone_start = start_generation + (zone * zone_width)
            zone_end = zone_start + zone_width
            
            # 25% probabilidad base
            if random.random() < 0.25:
                attempts = 0
                spike_placed = False
                
                while not spike_placed and attempts < 5:
                    attempts += 1
                    
                    # Generar posición candidata
                    x = random.randint(zone_start + 40, zone_end - 40)
                    y = ground_y - 30  # En el suelo (altura de espina = 30)
                    spike_width = 40
                    spike_height = 30
                    
                    # === VALIDACIÓN 1: No cerca de checkpoints ===
                    if self.is_near_checkpoint(x, y, checkpoints, radius=150):
                        continue  # Demasiado cerca de checkpoint
                    
                    # === VALIDACIÓN 2: Debe estar sobre una superficie ===
                    if not self.is_on_surface(x, y, spike_height, platforms, ground_y):
                        continue  # No está sobre suelo ni plataforma
                    
                    # === VALIDACIÓN 3: No superpuesta con otra espina ===
                    overlaps = False
                    for existing_spike in spikes:
                        if self.rectangles_overlap(
                            x, y, spike_width, spike_height,
                            existing_spike['x'], existing_spike['y'],
                            existing_spike['width'], existing_spike['height']
                        ):
                            overlaps = True
                            break
                    
                    if overlaps:
                        continue  # Se superpone con otra espina
                    
                    # === TODAS LAS VALIDACIONES PASADAS ===
                    spikes.append({
                        'x': x,
                        'y': y,
                        'width': spike_width,
                        'height': spike_height
                    })
                    spike_placed = True
        
        # 5. ZONAS DE PELIGRO - Grupos en el suelo
        if num_zones >= 4:
            # 2 zonas de peligro
            danger_zones = random.sample(
                range(2, num_zones - 1),
                min(2, num_zones - 3)
            )
            
            for danger_zone in danger_zones:
                zone_start = start_generation + (danger_zone * zone_width)
                zone_center_x = zone_start + zone_width // 2
                zone_center_y = ground_y - 32
                
                if self.is_near_checkpoint(zone_center_x, zone_center_y, checkpoints, radius=200):
                    continue
                
                # CORREGIDO: MÁXIMO 2 espinas juntas (vs 2-3 antes)
                num_spikes_in_danger = 2  # ← FIJO en 2
                spikes_added = 0
                
                for i in range(num_spikes_in_danger):
                    x = zone_start + (spikes_added * 50) + 40
                    y = ground_y - 32
                    spike_width = 38
                    spike_height = 32
                    
                    if self.is_near_checkpoint(x, y, checkpoints, radius=150):
                        continue
                    
                    if not self.is_on_surface(x, y, spike_height, platforms, ground_y):
                        continue
                    
                    overlaps = False
                    for existing_spike in spikes:
                        if self.rectangles_overlap(
                            x, y, spike_width, spike_height,
                            existing_spike['x'], existing_spike['y'],
                            existing_spike['width'], existing_spike['height']
                        ):
                            overlaps = True
                            break
                    
                    if overlaps:
                        continue
                    
                    spikes.append({
                        'x': x,
                        'y': y,
                        'width': spike_width,
                        'height': spike_height
                    })
                    spikes_added += 1

        
        # 6. ESPINAS EN PLATAFORMAS (opcional para nivel fácil)
        # Seleccionar algunas plataformas al azar para poner espinas encima
        eligible_platforms = []
        
        for platform in platforms:
            # Solo plataformas que no sean el suelo y no estén cerca de checkpoints
            if platform['y'] < height - 100:  # No es el suelo
                if not self.is_near_checkpoint(platform['x'], platform['y'], checkpoints, radius=200):
                    eligible_platforms.append(platform)
        
        # En nivel fácil, solo 1-2 espinas en plataformas
        num_platform_spikes = min(random.randint(0, 2), len(eligible_platforms))
        
        if num_platform_spikes > 0:
            selected_platforms = random.sample(eligible_platforms, num_platform_spikes)
            
            for platform in selected_platforms:
                # Colocar espina en el centro de la plataforma
                spike_x = platform['x'] + platform['width'] // 2 - 20  # Centrada
                spike_y = platform['y'] - 30  # Encima de la plataforma
                spike_width = 40
                spike_height = 30
                
                # Validar que no se superpone con otras espinas
                overlaps = False
                for existing_spike in spikes:
                    if self.rectangles_overlap(
                        spike_x, spike_y, spike_width, spike_height,
                        existing_spike['x'], existing_spike['y'],
                        existing_spike['width'], existing_spike['height']
                    ):
                        overlaps = True
                        break
                
                if not overlaps:
                    spikes.append({
                        'x': spike_x,
                        'y': spike_y,
                        'width': spike_width,
                        'height': spike_height
                    })
        
        return spikes
    
    def add_special_features(self, world_data, width, height):
        """Añade música y características especiales del mundo de pasto"""
        # Música relajada para nivel fácil
        world_data['music'] = WORLD_MUSIC_PATH + 'grass_theme.mp3'



class DesertWorldGenerator(WorldGenerator):
    """Generador de mundo desértico (nivel medio)"""

    def get_powerup_type(self):
        """Desert: PowerUps de salto para superar obstáculos"""
        rand = random.random()
        if rand < 0.50:
            return 'jump'
        elif rand < 0.75:
            return 'speed'
        else:
            return 'life'

    
    def define_colors(self):
        """Colores cálidos y áridos del desierto"""
        return {
            'sky': (255, 218, 185),      # Naranja claro (atardecer)
            'ground': (210, 180, 140),   # Arena
            'platform': (139, 90, 43),   # Marrón oscuro (rocas)
            'hazard': (255, 140, 0)      # Naranja oscuro (cactus)
        }
    
    def get_world_name(self):
        """Nombre del mundo"""
        return "Mundo Desértico"
    
    def generate_platforms(self, width, height, checkpoints):
        """Genera plataformas más separadas y difíciles, con ALTURAS ALCANZABLES"""
        platforms = []
        
        # 1. SUELO PRINCIPAL
        ground = {
            'x': 0,
            'y': height - 50,
            'width': width,
            'height': 50
        }
        platforms.append(ground)
        
        # 2. PLATAFORMAS DE INICIO
        spawn_x = 100
        spawn_y = 100
        
        first_platform = {
            'x': 180,
            'y': height - 180,  # 180px altura - ALCANZABLE
            'width': 120,
            'height': 18
        }
        
        if self.is_platform_reachable(spawn_x, spawn_y, first_platform['x'], first_platform['y'], first_platform['width']):
            platforms.append(first_platform)
        
        second_platform = {
            'x': 380,
            'y': height - 240,  # 240px altura - ALCANZABLE desde primera
            'width': 110,
            'height': 18
        }
        
        if self.is_platform_reachable(first_platform['x'], first_platform['y'], second_platform['x'], second_platform['y'], second_platform['width']):
            platforms.append(second_platform)
        
        # 3. PLATAFORMAS DISTRIBUIDAS - ALTURAS CORREGIDAS
        start_generation = 600
        end_generation = width - 400
        generation_width = end_generation - start_generation
        
        num_segments = 7
        segment_width = generation_width // num_segments
        
        for segment in range(num_segments):
            segment_start = start_generation + (segment * segment_width)
            segment_end = segment_start + segment_width
            
            num_platforms = random.randint(1, 2)
            attempts_per_segment = 0
            platforms_added_in_segment = 0
            
            while platforms_added_in_segment < num_platforms and attempts_per_segment < 25:
                attempts_per_segment += 1
                
                margin_left = int(segment_width * 0.15)
                margin_right = int(segment_width * 0.25)
                
                available_width = segment_width - margin_left - margin_right
                if available_width < 80:
                    break
                
                x = random.randint(
                    segment_start + margin_left,
                    segment_end - margin_right
                )
                
                # CORREGIDO: Altura máxima ALCANZABLE
                # Desert medio: Entre 130px y 300px de altura
                # Esto permite:
                # - Saltos desde el suelo (hasta ~200px)
                # - Saltos entre plataformas (hasta 200px diferencia)
                y = random.randint(
                    height - 300,  # Máximo 300px alto (vs 380 antes) - ALCANZABLE
                    height - 130   # Mínimo 130px alto
                )
                
                platform_width = random.randint(100, 140)
                platform_height = 18
                
                # === VALIDACIÓN 1: No cerca de checkpoints ===
                if self.is_near_checkpoint(x, y, checkpoints):
                    continue
                
                # === VALIDACIÓN 2: No superpuesta ===
                overlaps = False
                for existing_platform in platforms:
                    if self.rectangles_overlap(
                        x, y, platform_width, platform_height,
                        existing_platform['x'], existing_platform['y'],
                        existing_platform['width'], existing_platform['height']
                    ):
                        overlaps = True
                        break
                
                if overlaps:
                    continue
                
                # === VALIDACIÓN 3: Espaciamiento riguroso ===
                too_close = False
                
                for existing_platform in platforms:
                    horizontal_distance = abs(x - existing_platform['x'])
                    vertical_distance = abs(y - existing_platform['y'])
                    
                    if horizontal_distance < 220:
                        if vertical_distance < MIN_VERTICAL_SPACING:
                            too_close = True
                            break
                    
                    if vertical_distance < 40:
                        if horizontal_distance < MIN_HORIZONTAL_SPACING:
                            too_close = True
                            break
                
                if too_close:
                    continue
                
                # === VALIDACIÓN 4: Alcanzable ===
                is_reachable = False
                
                # Desde el suelo
                ground_to_platform_height = (height - 50) - y
                if ground_to_platform_height <= MAX_JUMP_HEIGHT:
                    # Está suficientemente bajo para alcanzar desde el suelo
                    is_reachable = True
                
                # Desde plataforma previa
                if not is_reachable:
                    for prev_platform in platforms:
                        if prev_platform['x'] < x + 350:
                            if self.is_platform_reachable(
                                prev_platform['x'] + prev_platform['width'],
                                prev_platform['y'],
                                x,
                                y,
                                platform_width
                            ):
                                is_reachable = True
                                break
                
                # Desde plataformas cercanas (bidireccional)
                if not is_reachable:
                    for prev_platform in platforms:
                        if prev_platform['x'] > x - 350 and prev_platform['x'] < x + segment_width:
                            if self.is_platform_reachable(
                                prev_platform['x'],
                                prev_platform['y'],
                                x,
                                y,
                                platform_width
                            ):
                                is_reachable = True
                                break
                
                if not is_reachable:
                    continue
                
                # === VALIDACIONES PASADAS ===
                platforms.append({
                    'x': x,
                    'y': y,
                    'width': platform_width,
                    'height': platform_height
                })
                platforms_added_in_segment += 1
        
        # 4. PLATAFORMAS FLOTANTES ALTAS - ALTURAS CORREGIDAS
        # Feature de Desert pero con alturas alcanzables
        num_high_platforms = random.randint(2, 3)
        
        if num_segments > 2:
            eligible_segments = list(range(1, num_segments - 1))
            selected_segments = random.sample(eligible_segments, min(num_high_platforms, len(eligible_segments)))
            
            for zone in selected_segments:
                attempts_high = 0
                
                while attempts_high < 15:
                    attempts_high += 1
                    
                    zone_center = start_generation + (zone * segment_width) + (segment_width // 2)
                    
                    # CORREGIDO: Altura flotante entre 280-350px
                    # Más alto que las normales pero aún ALCANZABLE desde otras plataformas
                    high_y = height - random.randint(280, 350)  # vs 400-450 antes
                    high_width = random.randint(80, 110)
                    high_height = 18
                    high_x = zone_center - random.randint(30, 70)
                    
                    # Validar checkpoints
                    if self.is_near_checkpoint(high_x, high_y, checkpoints):
                        continue
                    
                    # Validar superposición
                    overlaps = False
                    for existing_platform in platforms:
                        if self.rectangles_overlap(
                            high_x, high_y, high_width, high_height,
                            existing_platform['x'], existing_platform['y'],
                            existing_platform['width'], existing_platform['height']
                        ):
                            overlaps = True
                            break
                    
                    if overlaps:
                        continue
                    
                    # Validar espaciamiento
                    too_close = False
                    for existing_platform in platforms:
                        horizontal_distance = abs(high_x - existing_platform['x'])
                        vertical_distance = abs(high_y - existing_platform['y'])
                        
                        if horizontal_distance < 220 and vertical_distance < MIN_VERTICAL_SPACING:
                            too_close = True
                            break
                    
                    if too_close:
                        continue
                    
                    # VALIDACIÓN CRÍTICA: Debe ser alcanzable desde ALGUNA plataforma cercana
                    is_reachable = False
                    for prev_platform in platforms:
                        # Solo plataformas dentro de rango razonable
                        horizontal_dist = abs(prev_platform['x'] - high_x)
                        if horizontal_dist < 400:
                            if self.is_platform_reachable(
                                prev_platform['x'],
                                prev_platform['y'],
                                high_x,
                                high_y,
                                high_width
                            ):
                                is_reachable = True
                                break
                    
                    if not is_reachable:
                        continue  # No alcanzable, rechazar
                    
                    # Añadir plataforma alta
                    platforms.append({
                        'x': high_x,
                        'y': high_y,
                        'width': high_width,
                        'height': high_height
                    })
                    break
        
        # 5. PLATAFORMA FINAL
        final_platform = {
            'x': width - 350,
            'y': height - 190,
            'width': 130,
            'height': 18
        }
        
        if not self.is_near_checkpoint(final_platform['x'], final_platform['y'], checkpoints):
            can_add = True
            for existing_platform in platforms:
                horizontal_distance = abs(final_platform['x'] - existing_platform['x'])
                vertical_distance = abs(final_platform['y'] - existing_platform['y'])
                
                if horizontal_distance < 220 and vertical_distance < MIN_VERTICAL_SPACING:
                    can_add = False
                    break
            
            if can_add:
                platforms.append(final_platform)
        
        return platforms


    
    def generate_hazards(self, width, height, platforms, checkpoints):
        """Genera espinas con validaciones RIGUROSAS - Nivel MEDIO"""
        spikes = []
        ground_y = height - 50
        
        # 1. ZONA SEGURA
        safe_zone = 400
        
        # 2. ZONA DE GENERACIÓN
        start_generation = safe_zone
        end_generation = width - 250
        generation_width = end_generation - start_generation
        
        # 3. DIVIDIR EN ZONAS
        num_zones = 12
        zone_width = generation_width // num_zones
        
        # 4. ESPINAS EN EL SUELO - Individuales
        for zone in range(num_zones):
            zone_start = start_generation + (zone * zone_width)
            zone_end = zone_start + zone_width
            
            # MEDIO: 45% probabilidad
            if random.random() < 0.45:
                attempts = 0
                spike_placed = False
                
                while not spike_placed and attempts < 8:
                    attempts += 1
                    
                    x = random.randint(zone_start + 30, zone_end - 30)
                    y = ground_y - 32  # EN EL SUELO
                    spike_width = 38
                    spike_height = 32
                    
                    # Validar checkpoints
                    if self.is_near_checkpoint(x, y, checkpoints, radius=150):
                        continue
                    
                    # IMPORTANTE: Verificar que está sobre el suelo
                    if not self.is_on_surface(x, y, spike_height, platforms, ground_y):
                        continue
                    
                    # Validar superposición
                    overlaps = False
                    for existing_spike in spikes:
                        if self.rectangles_overlap(
                            x, y, spike_width, spike_height,
                            existing_spike['x'], existing_spike['y'],
                            existing_spike['width'], existing_spike['height']
                        ):
                            overlaps = True
                            break
                    
                    if overlaps:
                        continue
                    
                    spikes.append({
                        'x': x,
                        'y': y,
                        'width': spike_width,
                        'height': spike_height
                    })
                    spike_placed = True
        
        # 5. ZONAS DE PELIGRO - Grupos en el suelo
        if num_zones >= 4:
            # 3 zonas de peligro
            danger_zones = random.sample(
                range(2, num_zones - 1),
                min(3, num_zones - 3)
            )
            
            for danger_zone in danger_zones:
                zone_start = start_generation + (danger_zone * zone_width)
                zone_center_x = zone_start + zone_width // 2
                zone_center_y = ground_y - 35
                
                if self.is_near_checkpoint(zone_center_x, zone_center_y, checkpoints, radius=200):
                    continue
                
                # CORREGIDO: MÁXIMO 2 espinas juntas (vs 3-4 antes)
                num_spikes_in_danger = 2  # ← FIJO en 2
                spikes_added = 0
                
                for i in range(num_spikes_in_danger):
                    x = zone_start + (spikes_added * 50) + 40
                    y = ground_y - 35
                    spike_width = 38
                    spike_height = 35
                    
                    if self.is_near_checkpoint(x, y, checkpoints, radius=150):
                        continue
                    
                    if not self.is_on_surface(x, y, spike_height, platforms, ground_y):
                        continue
                    
                    overlaps = False
                    for existing_spike in spikes:
                        if self.rectangles_overlap(
                            x, y, spike_width, spike_height,
                            existing_spike['x'], existing_spike['y'],
                            existing_spike['width'], existing_spike['height']
                        ):
                            overlaps = True
                            break
                    
                    if overlaps:
                        continue
                    
                    spikes.append({
                        'x': x,
                        'y': y,
                        'width': spike_width,
                        'height': spike_height
                    })
                    spikes_added += 1

        
        # 6. ESPINAS SOBRE PLATAFORMAS (NO flotantes, SOBRE plataformas)
        eligible_platforms = []
        
        for platform in platforms:
            # No es el suelo principal
            if platform['y'] < height - 100:
                # No cerca de checkpoints
                if not self.is_near_checkpoint(platform['x'] + platform['width'] // 2, platform['y'], checkpoints, radius=200):
                    # Plataforma suficientemente grande para una espina
                    if platform['width'] >= 80:
                        eligible_platforms.append(platform)
        
        # MEDIO: 2-3 espinas en plataformas
        num_platform_spikes = min(random.randint(2, 3), len(eligible_platforms))
        
        if num_platform_spikes > 0 and len(eligible_platforms) > 0:
            selected_platforms = random.sample(eligible_platforms, num_platform_spikes)
            
            for platform in selected_platforms:
                attempts = 0
                spike_placed = False
                
                while not spike_placed and attempts < 5:
                    attempts += 1
                    
                    # Posición centrada o aleatoria en la plataforma
                    available_space = platform['width'] - 60  # Margen
                    
                    if available_space < 40:
                        break  # Plataforma muy pequeña
                    
                    offset = random.randint(20, int(available_space))
                    spike_x = platform['x'] + offset
                    spike_y = platform['y'] - 32  # SOBRE la plataforma
                    spike_width = 38
                    spike_height = 32
                    
                    # CRÍTICO: Verificar que está EXACTAMENTE sobre esta plataforma
                    spike_bottom = spike_y + spike_height
                    if abs(spike_bottom - platform['y']) > 2:
                        continue  # No está alineada con la plataforma
                    
                    # Verificar que está dentro del rango horizontal
                    if spike_x < platform['x'] or spike_x + spike_width > platform['x'] + platform['width']:
                        continue
                    
                    # Validar superposición con otras espinas
                    overlaps = False
                    for existing_spike in spikes:
                        if self.rectangles_overlap(
                            spike_x, spike_y, spike_width, spike_height,
                            existing_spike['x'], existing_spike['y'],
                            existing_spike['width'], existing_spike['height']
                        ):
                            overlaps = True
                            break
                    
                    if overlaps:
                        continue
                    
                    spikes.append({
                        'x': spike_x,
                        'y': spike_y,
                        'width': spike_width,
                        'height': spike_height,
                        'on_platform': True  # Flag para indicar que está sobre plataforma
                    })
                    spike_placed = True
        
        return spikes
   
    def add_special_features(self, world_data, width, height):
        """Añade música y características del desierto"""
        # Música de desierto (ritmo medio, atmosférica)
        world_data['music'] = WORLD_MUSIC_PATH + 'desert_theme.mp3'



class IceWorldGenerator(WorldGenerator):
    """Generador de mundo de hielo (nivel difícil)"""

    def get_powerup_type(self):
        """Ice: PowerUps de vida para zona difícil"""
        rand = random.random()
        if rand < 0.50:
            return 'life'
        elif rand < 0.75:
            return 'speed'
        else:
            return 'jump'

    
    def define_colors(self):
        """Colores fríos y helados"""
        return {
            'sky': (176, 224, 230),      # Azul hielo pálido
            'ground': (240, 248, 255),   # Blanco hielo
            'platform': (175, 238, 238),  # Turquesa helado
            'hazard': (70, 130, 180)     # Azul acero (estalactitas)
        }
    
    def get_world_name(self):
        """Nombre del mundo"""
        return "Mundo de Hielo"
    
    def generate_platforms(self, width, height, checkpoints):
        """Genera plataformas estrechas y muy separadas - DIFÍCIL pero estructura simple"""
        platforms = []
        
        # 1. SUELO PRINCIPAL - Continuo como Grass y Desert
        ground = {
            'x': 0,
            'y': height - 50,
            'width': width,
            'height': 50
        }
        platforms.append(ground)
        
        # 2. PLATAFORMAS DE INICIO - Más desafiantes
        spawn_x = 100
        spawn_y = 100
        
        first_platform = {
            'x': 220,  # Más lejos que Desert (vs 180)
            'y': height - 200,
            'width': 85,  # Más pequeña (vs 120 Desert)
            'height': 15  # Más delgada
        }
        
        if self.is_platform_reachable(spawn_x, spawn_y, first_platform['x'], first_platform['y'], first_platform['width']):
            platforms.append(first_platform)
        
        second_platform = {
            'x': 450,  # Más lejos (vs 380 Desert)
            'y': height - 280,
            'width': 80,
            'height': 15
        }
        
        if self.is_platform_reachable(first_platform['x'], first_platform['y'], second_platform['x'], second_platform['y'], second_platform['width']):
            platforms.append(second_platform)
        
        # 3. PLATAFORMAS DISTRIBUIDAS - DIFÍCIL
        start_generation = 700  # Empieza más tarde (vs 600)
        end_generation = width - 400
        generation_width = end_generation - start_generation
        
        num_segments = 8  # Más segmentos que Desert (vs 7)
        segment_width = generation_width // num_segments
        
        for segment in range(num_segments):
            segment_start = start_generation + (segment * segment_width)
            segment_end = segment_start + segment_width
            
            # DIFÍCIL: Solo 1 plataforma por segmento (vs 1-2 Desert)
            # 85% probabilidad (15% segmentos vacíos)
            if random.random() < 0.85:
                
                attempts_per_segment = 0
                platform_placed = False
                
                while not platform_placed and attempts_per_segment < 30:
                    attempts_per_segment += 1
                    
                    # Márgenes más estrictos
                    margin_left = int(segment_width * 0.25)  # vs 0.15 Desert
                    margin_right = int(segment_width * 0.35)  # vs 0.25 Desert
                    
                    available_width = segment_width - margin_left - margin_right
                    if available_width < 60:
                        break
                    
                    x = random.randint(
                        segment_start + margin_left,
                        segment_end - margin_right
                    )
                    
                    # DIFÍCIL: Altura muy variable
                    y = random.randint(
                        height - 350,  # Muy alto
                        height - 140   # Muy bajo
                    )
                    
                    # DIFÍCIL: Plataformas muy estrechas
                    platform_width = random.randint(65, 95)  # vs 100-140 Desert
                    platform_height = 15
                    
                    # === VALIDACIÓN 1: No cerca de checkpoints ===
                    if self.is_near_checkpoint(x, y, checkpoints):
                        continue
                    
                    # === VALIDACIÓN 2: No superpuesta ===
                    overlaps = False
                    for existing_platform in platforms:
                        if self.rectangles_overlap(
                            x, y, platform_width, platform_height,
                            existing_platform['x'], existing_platform['y'],
                            existing_platform['width'], existing_platform['height']
                        ):
                            overlaps = True
                            break
                    
                    if overlaps:
                        continue
                    
                    # === VALIDACIÓN 3: Espaciamiento muy estricto ===
                    too_close = False
                    
                    for existing_platform in platforms:
                        horizontal_distance = abs(x - existing_platform['x'])
                        vertical_distance = abs(y - existing_platform['y'])
                        
                        # DIFÍCIL: Espaciamiento más amplio
                        if horizontal_distance < 270:  # vs 220 Desert
                            if vertical_distance < MIN_VERTICAL_SPACING:
                                too_close = True
                                break
                        
                        if vertical_distance < 30:
                            if horizontal_distance < 130:  # vs 100
                                too_close = True
                                break
                    
                    if too_close:
                        continue
                    
                    # === VALIDACIÓN 4: Alcanzable ===
                    is_reachable = False
                    
                    # Desde el suelo
                    ground_height_diff = (height - 50) - y
                    if ground_height_diff <= MAX_JUMP_HEIGHT:
                        is_reachable = True
                    
                    # Desde plataforma previa
                    if not is_reachable:
                        for prev_platform in platforms:
                            if prev_platform['y'] != height - 50:
                                if prev_platform['x'] < x + 400:
                                    if self.is_platform_reachable(
                                        prev_platform['x'] + prev_platform['width'],
                                        prev_platform['y'],
                                        x,
                                        y,
                                        platform_width
                                    ):
                                        is_reachable = True
                                        break
                    
                    # Bidireccional
                    if not is_reachable:
                        for prev_platform in platforms:
                            if prev_platform['y'] != height - 50:
                                if abs(prev_platform['x'] - x) < 400:
                                    if self.is_platform_reachable(
                                        prev_platform['x'],
                                        prev_platform['y'],
                                        x,
                                        y,
                                        platform_width
                                    ):
                                        is_reachable = True
                                        break
                    
                    if not is_reachable:
                        continue
                    
                    # === VALIDACIONES PASADAS ===
                    platforms.append({
                        'x': x,
                        'y': y,
                        'width': platform_width,
                        'height': platform_height
                    })
                    platform_placed = True
        
        # 4. PLATAFORMA FINAL
        final_platform = {
            'x': width - 380,
            'y': height - 210,
            'width': 95,  # Pequeña
            'height': 15
        }
        
        if not self.is_near_checkpoint(final_platform['x'], final_platform['y'], checkpoints):
            can_add = True
            for existing_platform in platforms:
                horizontal_distance = abs(final_platform['x'] - existing_platform['x'])
                vertical_distance = abs(final_platform['y'] - existing_platform['y'])
                
                if horizontal_distance < 270 and vertical_distance < MIN_VERTICAL_SPACING:
                    can_add = False
                    break
            
            if can_add:
                platforms.append(final_platform)
        
        return platforms


    
    def generate_hazards(self, width, height, platforms, checkpoints):
        """Genera espinas con máxima densidad - DIFÍCIL pero estructura simple"""
        spikes = []
        ground_y = height - 50
        
        # 1. ZONA SEGURA - Muy corta
        safe_zone = 350
        
        # 2. ZONA DE GENERACIÓN
        start_generation = safe_zone
        end_generation = width - 200
        generation_width = end_generation - start_generation
        
        # 3. DIVIDIR EN ZONAS - Máxima densidad
        num_zones = 16  # Más que Desert (vs 12)
        zone_width = generation_width // num_zones
        
        # 4. ESPINAS INDIVIDUALES EN EL SUELO - Máxima frecuencia
        for zone in range(num_zones):
            zone_start = start_generation + (zone * zone_width)
            zone_end = zone_start + zone_width
            
            # DIFÍCIL: 65% probabilidad (vs 60% inicial, 45% Desert, 25% Grass)
            if random.random() < 0.65:
                attempts = 0
                spike_placed = False
                
                while not spike_placed and attempts < 10:
                    attempts += 1
                    
                    x = random.randint(zone_start + 25, zone_end - 25)
                    y = ground_y - 35
                    spike_width = 35
                    spike_height = 35
                    
                    # Validar checkpoints
                    if self.is_near_checkpoint(x, y, checkpoints, radius=150):
                        continue
                    
                    # Validar superficie
                    if not self.is_on_surface(x, y, spike_height, platforms, ground_y):
                        continue
                    
                    # Validar superposición
                    overlaps = False
                    for existing_spike in spikes:
                        if self.rectangles_overlap(
                            x, y, spike_width, spike_height,
                            existing_spike['x'], existing_spike['y'],
                            existing_spike['width'], existing_spike['height']
                        ):
                            overlaps = True
                            break
                    
                    if overlaps:
                        continue
                    
                    spikes.append({
                        'x': x,
                        'y': y,
                        'width': spike_width,
                        'height': spike_height
                    })
                    spike_placed = True
        
        # 5. ZONAS DE PELIGRO - Máximas
        if num_zones >= 5:
            # 5 zonas de peligro (vs 4 antes, 3 Desert, 2 Grass)
            danger_zones = random.sample(
                range(2, num_zones - 1),
                min(5, num_zones - 3)
            )
            
            for danger_zone in danger_zones:
                zone_start = start_generation + (danger_zone * zone_width)
                zone_center_x = zone_start + zone_width // 2
                zone_center_y = ground_y - 35
                
                if self.is_near_checkpoint(zone_center_x, zone_center_y, checkpoints, radius=200):
                    continue
                
                # CORREGIDO: MÁXIMO 2 espinas juntas (vs 5-7 antes)
                num_spikes_in_danger = 2  # ← FIJO en 2
                spikes_added = 0
                
                for i in range(num_spikes_in_danger):
                    x = zone_start + (spikes_added * 45) + 30
                    y = ground_y - 35
                    spike_width = 35
                    spike_height = 35
                    
                    if self.is_near_checkpoint(x, y, checkpoints, radius=150):
                        continue
                    
                    if not self.is_on_surface(x, y, spike_height, platforms, ground_y):
                        continue
                    
                    overlaps = False
                    for existing_spike in spikes:
                        if self.rectangles_overlap(
                            x, y, spike_width, spike_height,
                            existing_spike['x'], existing_spike['y'],
                            existing_spike['width'], existing_spike['height']
                        ):
                            overlaps = True
                            break
                    
                    if overlaps:
                        continue
                    
                    spikes.append({
                        'x': x,
                        'y': y,
                        'width': spike_width,
                        'height': spike_height
                    })
                    spikes_added += 1

        
        # 6. ESPINAS EN PLATAFORMAS - Máximas
        eligible_platforms = []
        
        for platform in platforms:
            # No es el suelo
            if platform['y'] < height - 100:
                # No cerca de checkpoints
                if not self.is_near_checkpoint(platform['x'] + platform['width'] // 2, platform['y'], checkpoints, radius=200):
                    # Plataforma suficientemente grande
                    if platform['width'] >= 65:
                        eligible_platforms.append(platform)
        
        # DIFÍCIL: 5-7 espinas en plataformas (vs 4-6 antes, 2-3 Desert, 0-2 Grass)
        num_platform_spikes = min(random.randint(5, 7), len(eligible_platforms))
        
        if num_platform_spikes > 0 and len(eligible_platforms) > 0:
            selected_platforms = random.sample(eligible_platforms, num_platform_spikes)
            
            for platform in selected_platforms:
                attempts = 0
                spike_placed = False
                
                while not spike_placed and attempts < 5:
                    attempts += 1
                    
                    available_space = platform['width'] - 45
                    
                    if available_space < 35:
                        break
                    
                    offset = random.randint(10, int(max(10, available_space)))
                    spike_x = platform['x'] + offset
                    spike_y = platform['y'] - 35
                    spike_width = 35
                    spike_height = 35
                    
                    # Verificar alineación
                    spike_bottom = spike_y + spike_height
                    if abs(spike_bottom - platform['y']) > 2:
                        continue
                    
                    # Verificar rango horizontal
                    if spike_x < platform['x'] or spike_x + spike_width > platform['x'] + platform['width']:
                        continue
                    
                    # Validar superposición
                    overlaps = False
                    for existing_spike in spikes:
                        if self.rectangles_overlap(
                            spike_x, spike_y, spike_width, spike_height,
                            existing_spike['x'], existing_spike['y'],
                            existing_spike['width'], existing_spike['height']
                        ):
                            overlaps = True
                            break
                    
                    if overlaps:
                        continue
                    
                    spikes.append({
                        'x': spike_x,
                        'y': spike_y,
                        'width': spike_width,
                        'height': spike_height,
                        'on_platform': True
                    })
                    spike_placed = True
        
        return spikes

  
    def add_special_features(self, world_data, width, height):
        """Añade física resbaladiza y música del hielo"""
        # Música épica/intensa para nivel difícil
        world_data['music'] = WORLD_MUSIC_PATH + 'ice_theme.mp3'
        
        # FEATURE PRINCIPAL: Física resbaladiza
        world_data['slippery'] = True  # Todas las superficies son resbaladizas
        world_data['friction'] = 0.3   # Coeficiente bajo de fricción (vs 1.0 normal)

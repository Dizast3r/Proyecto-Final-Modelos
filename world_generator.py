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

class WorldGenerator(ABC):
    """Clase abstracta que define el template method para generar mundos"""
    
    def generate_world(self, width, height):
        """
        TEMPLATE METHOD - Define el esqueleto del algoritmo
        Este método no debe ser sobrescrito por las subclases
        """
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
        
        # Pasos del algoritmo en orden
        world_data['colors'] = self.define_colors()
        world_data['name'] = self.get_world_name()
        world_data['platforms'] = self.generate_platforms(width, height)
        world_data['spikes'] = self.generate_hazards(width, height)
        world_data['checkpoints'] = self.generate_checkpoints(width, height)
        world_data['powerups'] = self.add_powerups(width, height)
        world_data['enemies'] = self.add_enemies(width, height)      
        world_data['goal'] = self.add_goal(width, height)        
        
        # Hook method para características especiales
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
    def generate_platforms(self, width, height):
        """Genera las plataformas del mundo"""
        pass
    
    @abstractmethod
    def generate_hazards(self, width, height):
        """Genera los obstáculos/trampas del mundo"""
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
    
    def add_powerups(self, width, height):
        """Genera power-ups (implementación por defecto - vacía por ahora)"""
        return []
    
    def add_enemies(self, width, height):
        """Genera enemigos (implementación por defecto - vacía por ahora)"""
        return []
    
    @abstractmethod
    def add_goal(self, width, height):
        """Genera la meta del nivel (cada mundo debe implementarlo)"""
        pass
    
    def add_special_features(self, world_data, width, height):
        """Hook method - características únicas del mundo (música, física, etc)"""
        pass



class GrassWorldGenerator(WorldGenerator):
    """Generador de mundo de pasto (nivel fácil)"""
    
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
    
    def generate_platforms(self, width, height):
        """Genera plataformas distribuidas responsivamente"""
        platforms = []
        
        # 1. SUELO PRINCIPAL - Cubre todo el ancho del mundo
        platforms.append({
            'x': 0, 
            'y': height - 50, 
            'width': width,      # Responsivo: usa el ancho completo
            'height': 50
        })
        
        # 2. PLATAFORMAS DE INICIO (zona segura) - Fijas
        # Estas siempre están para que el jugador tenga dónde empezar
        platforms.append({
            'x': 150, 
            'y': height - 150, 
            'width': 150, 
            'height': 20
        })
        platforms.append({
            'x': 350, 
            'y': height - 200, 
            'width': 130, 
            'height': 20
        })
        
        # 3. PLATAFORMAS DISTRIBUIDAS - Responsivo y aleatorio
        # Dividir el mundo en segmentos después de la zona de inicio
        start_generation = 600  # Empezar después de zona inicial
        end_generation = width - 400  # Terminar antes de zona final
        generation_width = end_generation - start_generation
        
        num_segments = 6  # 6 zonas de generación
        segment_width = generation_width // num_segments
        
        for segment in range(num_segments):
            # Calcular límites de este segmento
            segment_start = start_generation + (segment * segment_width)
            segment_end = segment_start + segment_width
            
            # 2-3 plataformas por segmento (nivel fácil = muchas)
            num_platforms = random.randint(2, 3)
            
            for i in range(num_platforms):
                # Posición X aleatoria dentro del segmento
                x = random.randint(
                    segment_start + 80,   # Margen desde inicio segmento
                    segment_end - 180     # Margen antes de fin segmento
                )
                
                # Altura Y aleatoria pero controlada (fácil = no muy alto)
                y = random.randint(
                    height - 280,  # Altura máxima (280px del suelo)
                    height - 130   # Altura mínima (130px del suelo)
                )
                
                # Ancho de plataforma (fácil = plataformas grandes)
                platform_width = random.randint(130, 180)
                
                platforms.append({
                    'x': x, 
                    'y': y, 
                    'width': platform_width, 
                    'height': 20
                })
        
        # 4. PLATAFORMAS FINALES (zona de meta) - Fijas
        # Ayudan a llegar a la meta
        platforms.append({
            'x': width - 400, 
            'y': height - 170, 
            'width': 150, 
            'height': 20
        })
        platforms.append({
            'x': width - 220, 
            'y': height - 140, 
            'width': 120, 
            'height': 20
        })
        
        return platforms
    
    def generate_hazards(self, width, height):
        """Genera espinas distribuidas con aleatoriedad"""
        spikes = []
        
        # 1. ZONA SEGURA DE INICIO - Sin espinas
        safe_zone = 500
        
        # 2. ZONA DE GENERACIÓN
        start_generation = safe_zone
        end_generation = width - 300  # No poner espinas muy cerca de la meta
        generation_width = end_generation - start_generation
        
        # 3. DIVIDIR EN ZONAS PARA DISTRIBUIR ESPINAS
        num_zones = 10
        zone_width = generation_width // num_zones
        
        # 4. ESPINAS INDIVIDUALES ALEATORIAS
        for zone in range(num_zones):
            zone_start = start_generation + (zone * zone_width)
            zone_end = zone_start + zone_width
            
            # 25% probabilidad de espina en esta zona (fácil = pocas)
            if random.random() < 0.25:
                x = random.randint(zone_start + 40, zone_end - 40)
                
                spikes.append({
                    'x': x, 
                    'y': height - 80,  # En el suelo
                    'width': 40, 
                    'height': 30
                })
        
        # 5. ZONAS DE PELIGRO (grupos de espinas)
        # Seleccionar 2 zonas aleatorias para poner múltiples espinas
        if num_zones >= 3:
            danger_zones = random.sample(range(2, num_zones - 1), min(2, num_zones - 3))
            
            for danger_zone in danger_zones:
                zone_start = start_generation + (danger_zone * zone_width)
                
                # 2-3 espinas juntas en esta zona
                num_spikes_in_danger = random.randint(2, 3)
                
                for i in range(num_spikes_in_danger):
                    spikes.append({
                        'x': zone_start + (i * 55) + 50,
                        'y': height - 80,
                        'width': 40,
                        'height': 30
                    })
        
        return spikes
    
    def add_goal(self, width, height):
        """Genera la meta al final del mundo"""
        # Meta: bandera grande al final
        goal = {
            'x': width - 120,      # Cerca del borde derecho
            'y': height - 130,     # En el suelo
            'width': 60,
            'height': 80,
            'type': 'flag'         # Tipo de meta
        }
        return goal
    
    def add_special_features(self, world_data, width, height):
        """Añade música y características especiales del mundo de pasto"""
        # Música relajada para nivel fácil
        world_data['music'] = WORLD_MUSIC_PATH + 'grass_theme.mp3'  # Path a archivo de música
        
        # Podrías añadir más features aquí en el futuro:
        # - Partículas de flores
        # - Animación de pasto moviéndose
        # - Nubes en el fondo



class DesertWorldGenerator(WorldGenerator):
    """Generador de mundo desértico (nivel medio)"""
    
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
    
    def generate_platforms(self, width, height):
        """Genera plataformas más separadas y difíciles que grass"""
        platforms = []
        
        # 1. SUELO PRINCIPAL - Cubre todo el mundo
        platforms.append({
            'x': 0, 
            'y': height - 50, 
            'width': width,
            'height': 50
        })
        
        # 2. PLATAFORMAS DE INICIO (zona segura) - Menos generosas que grass
        # Solo 2 plataformas iniciales (vs 2 en grass, pero más separadas)
        platforms.append({
            'x': 180, 
            'y': height - 180,      # Más alta que grass (180 vs 150)
            'width': 120,            # Más pequeña que grass (120 vs 150)
            'height': 18             # Más delgada (18 vs 20)
        })
        platforms.append({
            'x': 380, 
            'y': height - 240,      # Mucho más alta (240 vs 200)
            'width': 110,
            'height': 18
        })
        
        # 3. PLATAFORMAS DISTRIBUIDAS - Más difíciles que grass
        start_generation = 600
        end_generation = width - 400
        generation_width = end_generation - start_generation
        
        # MEDIO: 7 segmentos (vs 6 en fácil)
        num_segments = 7
        segment_width = generation_width // num_segments
        
        for segment in range(num_segments):
            segment_start = start_generation + (segment * segment_width)
            segment_end = segment_start + segment_width
            
            # MEDIO: 1-2 plataformas por segmento (vs 2-3 en fácil)
            # Menos plataformas = más difícil
            num_platforms = random.randint(1, 2)
            
            for i in range(num_platforms):
                # Posición X aleatoria
                x = random.randint(
                    segment_start + 100,   # Más margen que grass
                    segment_end - 200
                )
                
                # MEDIO: Altura Y más variable y más alta
                # Rango más amplio que grass para más variedad
                y = random.randint(
                    height - 380,  # Mucho más alto (380 vs 280 en grass)
                    height - 140   # Similar mínimo pero puede ser más bajo
                )
                
                # MEDIO: Plataformas medianas (más pequeñas que grass)
                platform_width = random.randint(100, 140)  # vs 130-180 en grass
                
                platforms.append({
                    'x': x, 
                    'y': y, 
                    'width': platform_width, 
                    'height': 18  # Más delgadas (18 vs 20)
                })
        
        # 4. PLATAFORMAS FLOTANTES ALTAS - Feature especial del desierto
        # Añadir 3-4 plataformas muy altas distribuidas aleatoriamente
        num_high_platforms = random.randint(3, 4)
        high_platform_zones = random.sample(
            range(1, num_segments - 1), 
            min(num_high_platforms, num_segments - 2)
        )
        
        for zone in high_platform_zones:
            zone_center = start_generation + (zone * segment_width) + (segment_width // 2)
            
            # Plataformas muy altas (desafío extra)
            platforms.append({
                'x': zone_center - 50,
                'y': height - random.randint(400, 450),  # MUY altas
                'width': random.randint(80, 110),         # Pequeñas
                'height': 18
            })
        
        # 5. PLATAFORMAS FINALES - Menos ayuda que grass
        # Solo 1 plataforma final (vs 2 en grass)
        platforms.append({
            'x': width - 350, 
            'y': height - 190,  # Más alta que grass
            'width': 130, 
            'height': 18
        })
        
        return platforms
    
    def generate_hazards(self, width, height):
        """Genera más espinas que grass (cactus en el desierto)"""
        spikes = []
        
        # 1. ZONA SEGURA DE INICIO - Más corta que grass
        safe_zone = 400  # vs 500 en grass
        
        # 2. ZONA DE GENERACIÓN
        start_generation = safe_zone
        end_generation = width - 250  # Espinas más cerca de la meta que grass
        generation_width = end_generation - start_generation
        
        # 3. DIVIDIR EN ZONAS
        num_zones = 12  # Más zonas = más densidad potencial (vs 10 en grass)
        zone_width = generation_width // num_zones
        
        # 4. ESPINAS INDIVIDUALES - Más frecuentes que grass
        for zone in range(num_zones):
            zone_start = start_generation + (zone * zone_width)
            zone_end = zone_start + zone_width
            
            # MEDIO: 45% probabilidad (vs 25% en fácil)
            if random.random() < 0.45:
                x = random.randint(zone_start + 30, zone_end - 30)
                
                spikes.append({
                    'x': x, 
                    'y': height - 80,
                    'width': 38,   # Ligeramente más anchos
                    'height': 32   # Ligeramente más altos
                })
        
        # 5. ZONAS DE PELIGRO - Más que grass
        # 3 zonas de peligro (vs 2 en grass)
        if num_zones >= 4:
            danger_zones = random.sample(
                range(2, num_zones - 1), 
                min(3, num_zones - 3)
            )
            
            for danger_zone in danger_zones:
                zone_start = start_generation + (danger_zone * zone_width)
                
                # MEDIO: 3-4 espinas juntas (vs 2-3 en fácil)
                num_spikes_in_danger = random.randint(3, 4)
                
                for i in range(num_spikes_in_danger):
                    spikes.append({
                        'x': zone_start + (i * 50) + 40,
                        'y': height - 80,
                        'width': 38,
                        'height': 32
                    })
        
        # 6. ESPINAS EN PLATAFORMAS (feature del desierto)
        # Algunas espinas flotantes en ciertas plataformas
        num_platform_spikes = random.randint(2, 3)
        
        for _ in range(num_platform_spikes):
            # Posición aleatoria en el mundo
            spike_x = random.randint(
                start_generation + 200,
                end_generation - 200
            )
            
            # Altura aleatoria flotante
            spike_y = random.randint(
                height - 350,
                height - 150
            )
            
            spikes.append({
                'x': spike_x,
                'y': spike_y,
                'width': 38,
                'height': 32
            })
        
        return spikes
    
    def add_goal(self, width, height):
        """Meta del desierto - Oasis al final"""
        goal = {
            'x': width - 110,
            'y': height - 130,
            'width': 60,
            'height': 80,
            'type': 'oasis'  # Tipo específico del desierto
        }
        return goal
    
    def add_special_features(self, world_data, width, height):
        """Añade música y características del desierto"""
        # Música de desierto (ritmo medio, atmosférica)
        world_data['music'] = WORLD_MUSIC_PATH + 'desert_theme.mp3'
        
        # Features especiales del desierto (para futuro):
        # - Tormentas de arena periódicas
        # - Viento que afecta el salto
        # - Calor que reduce velocidad gradualmente
        world_data['wind_effect'] = True  # Flag para implementar viento



class IceWorldGenerator(WorldGenerator):
    """Generador de mundo de hielo (nivel difícil)"""
    
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
    
    def generate_platforms(self, width, height):
        """Genera plataformas estrechas y muy separadas (difícil)"""
        platforms = []
        
        # 1. SUELO PRINCIPAL - Pero con huecos (feature del hielo)
        # DIFÍCIL: El suelo NO es continuo, tiene gaps
        num_ground_segments = 8
        segment_width = width // num_ground_segments
        
        for segment in range(num_ground_segments):
            segment_start = segment * segment_width
            
            # 70% probabilidad de que este segmento tenga suelo
            # 30% probabilidad de gap = caída al vacío
            if random.random() < 0.70 or segment == 0:  # Primer segmento siempre tiene suelo
                platforms.append({
                    'x': segment_start,
                    'y': height - 50,
                    'width': segment_width - 20,  # Gap de 20px entre segmentos
                    'height': 50
                })
        
        # 2. PLATAFORMAS DE INICIO - Muy básicas y desafiantes
        # Solo 2 plataformas pequeñas
        platforms.append({
            'x': 200,
            'y': height - 220,      # Muy alta desde el inicio (220 vs 180 desert)
            'width': 90,            # Muy pequeña (90 vs 120 desert)
            'height': 15            # Muy delgada (15 vs 18 desert)
        })
        platforms.append({
            'x': 420,
            'y': height - 300,      # Extremadamente alta (300 vs 240 desert)
            'width': 85,            # Muy pequeña
            'height': 15
        })
        
        # 3. PLATAFORMAS DISTRIBUIDAS - Extremadamente difíciles
        start_generation = 650
        end_generation = width - 400
        generation_width = end_generation - start_generation
        
        # DIFÍCIL: 8 segmentos (más que desert para distribuir mejor)
        num_segments = 8
        segment_width = generation_width // num_segments
        
        for segment in range(num_segments):
            segment_start = start_generation + (segment * segment_width)
            segment_end = segment_start + segment_width
            
            # DIFÍCIL: 1 plataforma por segmento (vs 1-2 en medio)
            # Algunas veces ninguna (20% probabilidad de segmento vacío)
            if random.random() < 0.80:  # 20% chance de NO generar plataforma
                
                # Posición X aleatoria
                x = random.randint(
                    segment_start + 120,   # Más margen que desert
                    segment_end - 220
                )
                
                # DIFÍCIL: Altura Y muy variable y extrema
                # Puede estar MUUUY alta o baja
                y = random.randint(
                    height - 480,  # Extremadamente alto (480 vs 380 desert)
                    height - 150   # Puede estar bajo también
                )
                
                # DIFÍCIL: Plataformas muy estrechas
                platform_width = random.randint(70, 100)  # vs 100-140 desert
                
                platforms.append({
                    'x': x,
                    'y': y,
                    'width': platform_width,
                    'height': 15  # Muy delgadas (15 vs 18 desert)
                })
        
        # 4. PLATAFORMAS MÓVILES SIMULADAS - Feature del hielo
        # Plataformas muy pequeñas en posiciones difíciles
        # (En el futuro podrían moverse, por ahora solo son muy pequeñas)
        num_tiny_platforms = random.randint(4, 6)
        
        for _ in range(num_tiny_platforms):
            x = random.randint(start_generation, end_generation - 100)
            y = random.randint(height - 450, height - 200)
            
            platforms.append({
                'x': x,
                'y': y,
                'width': random.randint(60, 80),  # MUY pequeñas
                'height': 12,  # Extra delgadas
                'slippery': True  # Flag para física resbaladiza
            })
        
        # 5. PLATAFORMAS VERTICALES - Feature único del hielo
        # Torres/columnas de plataformas apiladas
        num_towers = 2
        tower_positions = random.sample(
            range(2, num_segments - 2),
            min(num_towers, num_segments - 4)
        )
        
        for tower_segment in tower_positions:
            tower_x = start_generation + (tower_segment * segment_width) + (segment_width // 2)
            
            # 3-4 plataformas apiladas verticalmente
            num_levels = random.randint(3, 4)
            for level in range(num_levels):
                platforms.append({
                    'x': tower_x - 40,
                    'y': height - 150 - (level * 100),  # Separadas 100px verticalmente
                    'width': 80,
                    'height': 15
                })
        
        # 6. PLATAFORMAS FINALES - Mínima ayuda
        # Solo 1 plataforma y muy alta
        platforms.append({
            'x': width - 380,
            'y': height - 230,  # Muy alta (230 vs 190 desert)
            'width': 100,       # Pequeña
            'height': 15
        })
        
        return platforms
    
    def generate_hazards(self, width, height):
        """Genera MUCHAS espinas (estalactitas y hielo puntiagudo)"""
        spikes = []
        
        # 1. ZONA SEGURA DE INICIO - Muy corta
        safe_zone = 350  # vs 400 desert, 500 grass
        
        # 2. ZONA DE GENERACIÓN
        start_generation = safe_zone
        end_generation = width - 200  # Espinas MUY cerca de la meta
        generation_width = end_generation - start_generation
        
        # 3. DIVIDIR EN ZONAS - Más densidad
        num_zones = 15  # Más zonas que desert (vs 12)
        zone_width = generation_width // num_zones
        
        # 4. ESPINAS EN EL SUELO - Muy frecuentes
        for zone in range(num_zones):
            zone_start = start_generation + (zone * zone_width)
            zone_end = zone_start + zone_width
            
            # DIFÍCIL: 60% probabilidad (vs 45% desert, 25% grass)
            if random.random() < 0.60:
                x = random.randint(zone_start + 25, zone_end - 25)
                
                spikes.append({
                    'x': x,
                    'y': height - 80,
                    'width': 35,   # Más delgados (más difíciles de ver/evitar)
                    'height': 35   # Más altos
                })
        
        # 5. ZONAS DE PELIGRO EXTREMO
        # 4 zonas (vs 3 desert, 2 grass)
        if num_zones >= 5:
            danger_zones = random.sample(
                range(2, num_zones - 1),
                min(4, num_zones - 3)
            )
            
            for danger_zone in danger_zones:
                zone_start = start_generation + (danger_zone * zone_width)
                
                # DIFÍCIL: 4-6 espinas juntas (vs 3-4 desert, 2-3 grass)
                num_spikes_in_danger = random.randint(4, 6)
                
                for i in range(num_spikes_in_danger):
                    spikes.append({
                        'x': zone_start + (i * 45) + 30,
                        'y': height - 80,
                        'width': 35,
                        'height': 35
                    })
        
        # 6. ESTALACTITAS (espinas colgando del techo) - Feature único del hielo
        num_stalactites = random.randint(8, 12)  # Muchas
        
        for _ in range(num_stalactites):
            x = random.randint(start_generation, end_generation)
            
            # Cuelgan del techo (parte superior de la pantalla)
            spikes.append({
                'x': x,
                'y': 30,  # Cerca del techo
                'width': 30,
                'height': random.randint(60, 100),  # Altura variable (cuelgan)
                'hanging': True  # Flag para dibujar invertido
            })
        
        # 7. ESPINAS FLOTANTES EN PLATAFORMAS - Más que desert
        num_platform_spikes = random.randint(4, 6)  # vs 2-3 desert
        
        for _ in range(num_platform_spikes):
            spike_x = random.randint(
                start_generation + 200,
                end_generation - 200
            )
            
            # Altura aleatoria flotante
            spike_y = random.randint(
                height - 450,  # Más alto que desert
                height - 150
            )
            
            spikes.append({
                'x': spike_x,
                'y': spike_y,
                'width': 35,
                'height': 35
            })
        
        # 8. CAMPOS DE ESPINAS (áreas grandes llenas) - Feature extremo
        # 2 áreas grandes con muchas espinas
        num_spike_fields = 2
        field_zones = random.sample(
            range(3, num_zones - 3),
            min(num_spike_fields, num_zones - 6)
        )
        
        for field_zone in field_zones:
            field_start = start_generation + (field_zone * zone_width)
            field_width = zone_width * 2  # Ocupa 2 zonas
            
            # Llenar con espinas cada 60px
            num_spikes_in_field = field_width // 60
            
            for i in range(num_spikes_in_field):
                spikes.append({
                    'x': field_start + (i * 60) + 20,
                    'y': height - 80,
                    'width': 35,
                    'height': 35
                })
        
        return spikes
    
    def add_goal(self, width, height):
        """Meta del hielo - Iglú o portal al final"""
        goal = {
            'x': width - 100,
            'y': height - 130,
            'width': 60,
            'height': 80,
            'type': 'igloo'  # Tipo específico del hielo
        }
        return goal
    
    def add_special_features(self, world_data, width, height):
        """Añade física resbaladiza y música del hielo"""
        # Música épica/intensa para nivel difícil
        world_data['music'] = WORLD_MUSIC_PATH + 'ice_theme.mp3'
        
        # FEATURE PRINCIPAL: Física resbaladiza
        world_data['slippery'] = True  # Todas las superficies son resbaladizas
        world_data['friction'] = 0.3   # Coeficiente bajo de fricción (vs 1.0 normal)
        
        # Features adicionales del hielo (para futuro):
        # - Nieve cayendo que reduce visibilidad
        # - Viento helado que empuja al jugador
        # - Plataformas que se rompen después de pisarlas
        world_data['snowfall'] = True  # Flag para efecto de nieve
        world_data['breaking_platforms'] = True  # Flag para plataformas que se rompen

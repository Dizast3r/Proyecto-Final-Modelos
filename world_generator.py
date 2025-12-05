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
        return {
            'sky': (176, 224, 230),      # Azul hielo
            'ground': (240, 248, 255),   # Blanco hielo
            'platform': (175, 238, 238),  # Turquesa claro
            'hazard': (70, 130, 180)     # Azul acero
        }
    
    def get_world_name(self):
        return "Mundo de Hielo"
    
    def generate_platforms(self, width, height):
        platforms = []
        
        # Suelo principal
        platforms.append({'x': 0, 'y': height - 50, 'width': width, 'height': 50})
        
        # Plataformas estrechas y altas (difícil)
        for i in range(7):
            x = 100 + i * 250
            y = height - 200 - (i % 4) * 70
            platforms.append({'x': x, 'y': y, 'width': 100, 'height': 15})
        
        # Plataformas muy altas
        platforms.append({'x': 500, 'y': height - 400, 'width': 90, 'height': 15})
        platforms.append({'x': 1000, 'y': height - 450, 'width': 90, 'height': 15})
        
        return platforms
    
    def generate_hazards(self, width, height):
        spikes = []
        
        # Muchas espinas de hielo
        for i in range(12):
            x = 200 + i * 150
            spikes.append({'x': x, 'y': height - 80, 'width': 35, 'height': 30})
        
        # Estalactitas (espinas colgantes - implementación futura)
        for i in range(4):
            x = 300 + i * 400
            # Estas podrían colgar del techo
            spikes.append({'x': x, 'y': 50, 'width': 35, 'height': 40})
        
        return spikes
    
    def add_special_features(self, world_data, width, height):
        """El hielo podría tener física resbaladiza"""
        world_data['slippery'] = True  # Flag para implementar física resbaladiza
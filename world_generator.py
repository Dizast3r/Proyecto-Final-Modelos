"""
TEMPLATE METHOD PATTERN - Para generar diferentes tipos de mundos
Define el esqueleto del algoritmo de generación de mundos,
permitiendo que las subclases implementen pasos específicos
"""

from abc import ABC, abstractmethod
import random

SPACE_BETWEEN_CHECKPOINTS = 800
NUMBER_OF_CHECKPOINTS_PER_LEVEL = 3

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
            'colors': {},
            'name': ''
        }
        
        # Pasos del algoritmo (algunos abstractos, otros con implementación por defecto)
        world_data['colors'] = self.define_colors()
        world_data['name'] = self.get_world_name()
        world_data['platforms'] = self.generate_platforms(width, height)
        world_data['spikes'] = self.generate_hazards(width, height)
        world_data['checkpoints'] = self.generate_checkpoints(width, height)
        
        # Hook method (opcional de sobrescribir)
        self.add_special_features(world_data, width, height)
        
        return world_data
    
    @abstractmethod
    def define_colors(self):
        """Define los colores del mundo (debe implementarse en subclases)"""
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
            checkpoints.append({'x': i * SPACE_BETWEEN_CHECKPOINTS, 'y': height - 150})
        return checkpoints
    
    def add_special_features(self, world_data, width, height):
        """Hook method - puede ser sobrescrito para añadir características especiales"""
        pass


class GrassWorldGenerator(WorldGenerator):
    """Generador de mundo de pasto (nivel fácil)"""
    
    def define_colors(self):
        return {
            'sky': (135, 206, 235),      # Azul cielo
            'ground': (34, 139, 34),     # Verde
            'platform': (101, 67, 33),   # Marrón
            'hazard': (255, 0, 0)        # Rojo
        }
    
    def get_world_name(self):
        return "Mundo de Pasto"
    
    def generate_platforms(self, width, height):
        platforms = []
        
        # Suelo principal
        platforms.append({'x': 0, 'y': height - 50, 'width': width, 'height': 50})
        
        # Plataformas escalonadas fáciles
        for i in range(5):
            x = 200 + i * 300
            y = height - 150 - (i % 3) * 50
            platforms.append({'x': x, 'y': y, 'width': 150, 'height': 20})
        
        # Plataformas adicionales
        platforms.append({'x': 100, 'y': height - 200, 'width': 100, 'height': 20})
        platforms.append({'x': 1200, 'y': height - 250, 'width': 120, 'height': 20})
        
        return platforms
    
    def generate_hazards(self, width, height):
        spikes = []
        
        # Algunas espinas en el suelo
        spike_positions = [600, 900, 1400]
        for x in spike_positions:
            spikes.append({'x': x, 'y': height - 80, 'width': 40, 'height': 30})
        
        return spikes


class DesertWorldGenerator(WorldGenerator):
    """Generador de mundo desértico (nivel medio)"""
    
    def define_colors(self):
        return {
            'sky': (255, 218, 185),      # Naranja claro
            'ground': (210, 180, 140),   # Arena
            'platform': (139, 90, 43),   # Marrón oscuro
            'hazard': (255, 140, 0)      # Naranja oscuro
        }
    
    def get_world_name(self):
        return "Mundo Desértico"
    
    def generate_platforms(self, width, height):
        platforms = []
        
        # Suelo principal
        platforms.append({'x': 0, 'y': height - 50, 'width': width, 'height': 50})
        
        # Plataformas más separadas (más difícil)
        for i in range(6):
            x = 150 + i * 280
            y = height - 180 - random.randint(0, 100)
            platforms.append({'x': x, 'y': y, 'width': 120, 'height': 20})
        
        # Plataformas flotantes
        platforms.append({'x': 400, 'y': height - 300, 'width': 80, 'height': 20})
        platforms.append({'x': 800, 'y': height - 350, 'width': 80, 'height': 20})
        
        return platforms
    
    def generate_hazards(self, width, height):
        spikes = []
        
        # Más espinas que en el mundo de pasto
        for i in range(8):
            x = 250 + i * 200
            spikes.append({'x': x, 'y': height - 80, 'width': 40, 'height': 30})
        
        # Espinas en algunas plataformas
        spikes.append({'x': 400, 'y': height - 330, 'width': 40, 'height': 30})
        
        return spikes
    
    def add_special_features(self, world_data, width, height):
        """Añade dunas (plataformas redondeadas)"""
        # Aquí podrías añadir características especiales del desierto
        pass


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
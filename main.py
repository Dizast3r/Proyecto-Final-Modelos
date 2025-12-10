"""
MAIN - Punto de entrada del juego.
Inicializa el juego, configura los generadores de niveles y comienza la ejecucion.
Integracion de patrones:
- Template Method: En la generacion de mundos.
- Command: En el manejo de inputs.
- Observer: En el sistema de eventos.
"""

import pygame
from game import Game
from world_generator import GrassWorldGenerator, DesertWorldGenerator, IceWorldGenerator

# Dimensiones constantes del juego
ANCHO_DEL_MUNDO = 3000
ANCHO_VENTANA = 1600
ALTO_VENTANA = 600


def main():
    """Funcion principal que orquesta el inicio del juego."""
    # Instanciar clase principal del juego
    game = Game(ANCHO_VENTANA, ALTO_VENTANA, ANCHO_DEL_MUNDO)
    
    # Crear e inyectar generadores de mundos (Template Method Pattern)
    print("\nInicializando generadores...")
    generators = [
        GrassWorldGenerator(),
        DesertWorldGenerator(),
        IceWorldGenerator()
    ]
    
    # Inyeccion de dependencias de generacion
    game.set_world_generators(generators)
    
    print("\n" + "=" * 60)
    print("SUPER KIRBY BRO - PATRONES DE DISENO")
    print("=" * 60)
    print("\nPATRONES IMPLEMENTADOS:")
    print("  1. COMMAND PATTERN - Controles del personaje")
    print("  2. MEMENTO PATTERN - Sistema de checkpoints")
    print("  3. TEMPLATE METHOD PATTERN - Generacion de mundos")
    print("  4. FLYWEIGHT PATTERN - Optimizacion de sprites")
    print("  5. OBSERVER PATTERN - Sistema de eventos")
    print("  6. STRATEGY PATTERN - Comportamiento de PowerUps")
    print("  7. STATE PATTERN - Sistema de menus")
    print("=" * 60)
    print("\nIniciando ejecucion...\n")
    
    # Iniciar el bucle del juego
    game.run()
    
    print("\nEjecucion finalizada.")


if __name__ == "__main__":
    main()
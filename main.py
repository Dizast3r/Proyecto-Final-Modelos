"""
MAIN - Programa principal CON REGENERACIÓN DE MUNDOS
✅ NUEVO: Usa generadores reutilizables en vez de mundos pre-generados

Ejecuta este archivo para jugar
"""

import pygame
from game import Game
from world_generator import GrassWorldGenerator, DesertWorldGenerator, IceWorldGenerator

ANCHO_DEL_MUNDO = 3000
ANCHO_VENTANA = 1600
ALTO_VENTANA = 600


def main():
    # Crear el juego
    game = Game(ANCHO_VENTANA, ALTO_VENTANA, ANCHO_DEL_MUNDO)
    
    # ✅ Crear generadores (reutilizables)
    print("\n🔧 Configurando generadores de mundos...")
    generators = [
        GrassWorldGenerator(),
        DesertWorldGenerator(),
        IceWorldGenerator()
    ]
    
    # ✅ Pasar generadores al juego
    game.set_world_generators(generators)
    
    print("\n" + "=" * 60)
    print("SUPER KIRBY BRO - PATRONES DE DISEÑO")
    print("=" * 60)
    print("\n🎮 PATRONES IMPLEMENTADOS:")
    print("  1. COMMAND PATTERN - Controles del personaje")
    print("  2. MEMENTO PATTERN - Sistema de checkpoints")
    print("  3. TEMPLATE METHOD PATTERN - Generación de mundos")
    print("  4. FLYWEIGHT PATTERN - Optimización de sprites")
    print("  5. OBSERVER PATTERN - Sistema de eventos")
    print("  6. STRATEGY PATTERN - Comportamiento de PowerUps")
    print("\n🎨 SISTEMA DE MENÚS:")
    print("  ✅ Menú principal con botones interactivos")
    print("  ✅ Menús de completar nivel")
    print("  ✅ Game Over con reintentar")
    print("  ✅ Pantalla de victoria")
    print("  ✅ Regeneración de mundos en cada partida")
    print("\n🕹️ CONTROLES:")
    print("  ← → / A D : Mover")
    print("  Espacio / ↑ / W : Saltar")
    print("  Mouse : Interactuar con menús")
    print("  ESC : Salir del menú principal")
    print("\n⭐ OBJETIVO:")
    print("  - Completa los 3 mundos en secuencia")
    print("  - Recoge PowerUps para mejorar tus habilidades")
    print("  - Evita enemigos y trampas")
    print("  - ¡Alcanza la meta de cada mundo!")
    print("\n🔄 NUEVO: Los mundos se regeneran en cada partida")
    print("=" * 60)
    print("\n✨ Iniciando juego...\n")
    
    # Ejecutar el juego
    game.run()
    
    print("\n¡Gracias por jugar!")


if __name__ == "__main__":
    main()
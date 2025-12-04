"""
MAIN - Programa principal que integra todos los patrones
Ejecuta este archivo para jugar
"""

import pygame
from game import Game
from world_generator import GrassWorldGenerator, DesertWorldGenerator, IceWorldGenerator

def main():
    # Crear el juego
    game = Game(width=1600, height=600)
    
    # Crear generadores de mundos (Template Method Pattern)
    grass_generator = GrassWorldGenerator()
    desert_generator = DesertWorldGenerator()
    ice_generator = IceWorldGenerator()
    
    # Generar mundos
    worlds = {
        'grass': grass_generator.generate_world(game.width, game.height),
        'desert': desert_generator.generate_world(game.width, game.height),
        'ice': ice_generator.generate_world(game.width, game.height)
    }
    
    # Cargar mundo inicial (pasto)
    current_world_key = 'grass'
    game.load_world(worlds[current_world_key])
    
    print("=" * 50)
    print("JUEGO DE SALTOS - PATRONES DE DISEÑO")
    print("=" * 50)
    print("\n🎮 PATRONES IMPLEMENTADOS:")
    print("  1. COMMAND PATTERN - Controles del personaje")
    print("  2. MEMENTO PATTERN - Sistema de checkpoints")
    print("  3. TEMPLATE METHOD PATTERN - Generación de mundos")
    print("\n🕹️  CONTROLES:")
    print("  ← → / A D : Mover")
    print("  Espacio / ↑ / W : Saltar")
    print("  1 : Mundo de Pasto (Fácil)")
    print("  2 : Mundo Desértico (Medio)")
    print("  3 : Mundo de Hielo (Difícil)")
    print("  ESC : Salir")
    print("\n⭐ OBJETIVO:")
    print("  - Llega a los checkpoints (banderas doradas)")
    print("  - Evita las espinas/trampas")
    print("  - Si mueres, revives en el último checkpoint")
    print("=" * 50)
    print("\n¡Iniciando juego...\n")
    
    # Loop principal del juego con cambio de mundos
    clock = pygame.time.Clock()
    running = True
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                # Cambiar mundos
                elif event.key == pygame.K_1:
                    current_world_key = 'grass'
                    game.load_world(worlds[current_world_key])
                    print(f"\n🌱 Cargando: {worlds[current_world_key]['name']}")
                elif event.key == pygame.K_2:
                    current_world_key = 'desert'
                    game.load_world(worlds[current_world_key])
                    print(f"\n🏜️  Cargando: {worlds[current_world_key]['name']}")
                elif event.key == pygame.K_3:
                    current_world_key = 'ice'
                    game.load_world(worlds[current_world_key])
                    print(f"\n❄️  Cargando: {worlds[current_world_key]['name']}")
        
        # Input (Command Pattern)
        keys = pygame.key.get_pressed()
        game.input_handler.handle_input(keys, game.player)
        
        # Actualizar juego
        game.update()
        
        # Dibujar
        game.draw()
        
        # Actualizar pantalla
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()
    print("\n¡Gracias por jugar!")


if __name__ == "__main__":
    main()
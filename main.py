"""
MAIN - Programa principal refactorizado
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
    
    # Crear generadores de mundos (Template Method Pattern)
    grass_generator = GrassWorldGenerator()
    desert_generator = DesertWorldGenerator()
    ice_generator = IceWorldGenerator()
    
    # Generar mundos
    print("\n🔨 Generando mundos...")
    worlds = {
        'grass': grass_generator.generate_world(game.world_width, game.height),
        'desert': desert_generator.generate_world(game.world_width, game.height),
        'ice': ice_generator.generate_world(game.world_width, game.height)
    }
    
    # Cargar mundo inicial (pasto)
    current_world_key = 'grass'
    game.load_world(worlds[current_world_key])
    
    print("\n" + "=" * 60)
    print("SUPER KIRBY BRO - PATRONES DE DISEÑO")
    print("=" * 60)
    print("\n🎮 PATRONES IMPLEMENTADOS:")
    print("  1. COMMAND PATTERN - Controles del personaje")
    print("  2. MEMENTO PATTERN - Sistema de checkpoints")
    print("  3. TEMPLATE METHOD PATTERN - Generación de mundos")
    print("  4. FLYWEIGHT PATTERN - Optimización de sprites")
    print("  5. OBSERVER PATTERN - Sistema de eventos")
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
    print("  - Derrota enemigos saltando sobre ellos")
    print("  - Recolecta PowerUps (velocidad, salto, vida)")
    print("  - Si mueres, revives en el último checkpoint")
    print("=" * 60)
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
                elif event.key == pygame.K_2:
                    current_world_key = 'desert'
                    game.load_world(worlds[current_world_key])
                elif event.key == pygame.K_3:
                    current_world_key = 'ice'
                    game.load_world(worlds[current_world_key])
        
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
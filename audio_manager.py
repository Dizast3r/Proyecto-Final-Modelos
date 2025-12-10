"""
Gestor de Audio.
Controla la reproduccion de musica de fondo y efectos de sonido.
"""
import pygame


def play_world_music(music_file: str):
    """
    Inicia la reproduccion de la musica de fondo especificada.
    
    Args:
        music_file: Ruta absoluta al archivo de audio.
    """
    try:
        pygame.mixer.music.load(music_file)
        pygame.mixer.music.set_volume(0.5)  # 50% volumen
        pygame.mixer.music.play(-1)  # Loop infinito
        print(f"Reproduciendo: {music_file}")
    except pygame.error as e:
        print(f"Error cargando musica {music_file}: {e}")


def stop_music():
    """Detiene la reproduccion de musica actual."""
    pygame.mixer.music.stop()

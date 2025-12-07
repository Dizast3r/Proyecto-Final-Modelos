"""
Sistema de Audio
"""
import pygame


def play_world_music(music_file: str):
    """
    Reproduce la música de un mundo
    
    Args:
        music_file: Ruta completa al archivo de música
    """
    try:
        pygame.mixer.music.load(music_file)
        pygame.mixer.music.set_volume(0.5)  # 50% volumen
        pygame.mixer.music.play(-1)  # Loop infinito
        print(f"🎵 Reproduciendo: {music_file}")
    except pygame.error as e:
        print(f"⚠️ Error cargando música {music_file}: {e}")


def stop_music():
    """Detiene la música actual"""
    pygame.mixer.music.stop()
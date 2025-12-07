"""
OBSERVER PATTERN - Sistema de eventos del juego
Permite que diferentes componentes reaccionen a eventos sin acoplamiento directo
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any
from enum import Enum


class GameEventType(Enum):
    """Tipos de eventos en el juego"""
    CHECKPOINT_ACTIVATED = "checkpoint_activated"
    GOAL_REACHED = "goal_reached"
    PLAYER_DIED = "player_died"
    PLAYER_RESPAWNED = "player_respawned"
    ENEMY_KILLED = "enemy_killed"
    POWERUP_COLLECTED = "powerup_collected"
    WORLD_LOADED = "world_loaded"


class GameEvent:
    """Evento con datos asociados"""
    
    def __init__(self, event_type: GameEventType, data: Dict[str, Any] = None):
        self.event_type = event_type
        self.data = data or {}
    
    def __repr__(self):
        return f"GameEvent({self.event_type.value}, {self.data})"


class GameEventObserver(ABC):
    """Interfaz Observer - Los observadores deben implementar este método"""
    
    @abstractmethod
    def on_game_event(self, event: GameEvent):
        """Método llamado cuando ocurre un evento"""
        pass


class GameEventManager:
    """
    Subject - Gestor central de eventos (Singleton-like)
    Mantiene lista de observadores y notifica cuando ocurren eventos
    """
    
    def __init__(self):
        self._observers: List[GameEventObserver] = []
    
    def subscribe(self, observer: GameEventObserver):
        """Registra un observador para recibir notificaciones"""
        if observer not in self._observers:
            self._observers.append(observer)
            print(f"✅ Observador registrado: {observer.__class__.__name__}")
    
    def unsubscribe(self, observer: GameEventObserver):
        """Elimina un observador"""
        if observer in self._observers:
            self._observers.remove(observer)
            print(f"❌ Observador eliminado: {observer.__class__.__name__}")
    
    def notify(self, event: GameEvent):
        """Notifica a todos los observadores sobre un evento"""
        for observer in self._observers:
            observer.on_game_event(event)
    
    def clear_observers(self):
        """Limpia todos los observadores"""
        self._observers.clear()


# ============================================================================
# OBSERVADORES CONCRETOS
# ============================================================================

class ConsoleLogger(GameEventObserver):
    """Observador que imprime eventos en consola"""
    
    def on_game_event(self, event: GameEvent):
        """Registra eventos en consola"""
        messages = {
            GameEventType.CHECKPOINT_ACTIVATED: 
                lambda e: f"✓ Checkpoint {e.data.get('checkpoint_id')} guardado!",
            
            GameEventType.GOAL_REACHED: 
                lambda e: f"🎉 ¡META ALCANZADA! Completaste {e.data.get('world_name', 'el nivel')}",
            
            GameEventType.PLAYER_DIED: 
                lambda e: f"💀 Jugador murió. Vidas restantes: {e.data.get('lives_remaining', 0)}",
            
            GameEventType.PLAYER_RESPAWNED: 
                lambda e: f"🔄 Jugador reaparece en checkpoint",
            
            GameEventType.ENEMY_KILLED: 
                lambda e: f"💥 ¡Enemigo aplastado!",
            
            GameEventType.POWERUP_COLLECTED: 
                lambda e: self._format_powerup_message(e.data.get('type')),
            
            GameEventType.WORLD_LOADED: 
                lambda e: f"🌍 Mundo cargado: {e.data.get('world_name')}"
        }
        
        if event.event_type in messages:
            print(messages[event.event_type](event))
    
    def _format_powerup_message(self, powerup_type: str) -> str:
        """Formatea mensajes de PowerUps"""
        messages = {
            'speed': "⚡ Speed boost!",
            'jump': "🦘 Jump boost!",
            'life': "❤️ Extra life!"
        }
        return messages.get(powerup_type, "✨ PowerUp recolectado!")


class GameOverChecker(GameEventObserver):
    """Observador que verifica condición de Game Over"""
    
    def __init__(self, game):
        self.game = game
    
    def on_game_event(self, event: GameEvent):
        """Verifica si el juego debe terminar"""
        if event.event_type == GameEventType.PLAYER_DIED:
            lives = event.data.get('lives_remaining', 0)
            if lives <= 0:
                print("\n" + "="*50)
                print("GAME OVER!")
                print("="*50)
                self.game.running = False


class CheckpointSaver(GameEventObserver):
    """Observador que guarda checkpoints automáticamente"""
    
    def __init__(self, checkpoint_manager):
        self.checkpoint_manager = checkpoint_manager
        self.game = None  # Se asigna después
    
    def set_game(self, game):
        """Asigna la referencia al juego para acceder al player actual"""
        self.game = game
    
    def on_game_event(self, event: GameEvent):
        """Guarda checkpoint cuando se activa"""
        if event.event_type == GameEventType.CHECKPOINT_ACTIVATED:
            if self.game is None:
                return
            
            checkpoint_id = event.data.get('checkpoint_id')
            if checkpoint_id is not None:
                memento = self.game.player.create_memento()
                self.checkpoint_manager.save_checkpoint(checkpoint_id, memento)
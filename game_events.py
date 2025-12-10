"""
Patron de Diseno Observer:
Implementa un sistema de eventos y suscriptores para desacoplar la logica del juego.
GameEventManager actua como el Sujeto (Subject) y notifica a los Observadores
(GameEventObserver) cuando ocurren eventos importantes.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any
from enum import Enum
from menu_system import GameState


class GameEventType(Enum):
    """Enumeracion de los tipos de eventos posibles en el juego."""
    CHECKPOINT_ACTIVATED = "checkpoint_activated"
    GOAL_REACHED = "goal_reached"
    PLAYER_DIED = "player_died"
    PLAYER_RESPAWNED = "player_respawned"
    ENEMY_KILLED = "enemy_killed"
    POWERUP_COLLECTED = "powerup_collected"
    WORLD_LOADED = "world_loaded"


class GameEvent:
    """Clase que encapsula la informacion de un evento."""
    
    def __init__(self, event_type: GameEventType, data: Dict[str, Any] = None):
        self.event_type = event_type
        self.data = data or {}
    
    def __repr__(self):
        return f"GameEvent({self.event_type.value}, {self.data})"


class GameEventObserver(ABC):
    """
    Interfaz Observer:
    Define el metodo update (on_game_event) que deben implementar todos
    los objetos que deseen escuchar eventos del juego.
    """
    
    @abstractmethod
    def on_game_event(self, event: GameEvent):
        """Metodo invocado cuando el Sujeto notifica un nuevo evento."""
        pass


class GameEventManager:
    """
    Sujeto (Subject):
    Gestiona la lista de suscriptores (observadores) y se encarga de
    notificarles cuando ocurre un evento.
    """
    
    def __init__(self):
        self._observers: List[GameEventObserver] = []
    
    def subscribe(self, observer: GameEventObserver):
        """Añade un nuevo observador a la lista de notificaciones."""
        if observer not in self._observers:
            self._observers.append(observer)
            print(f"Observador registrado: {observer.__class__.__name__}")
    
    def unsubscribe(self, observer: GameEventObserver):
        """Elimina un observador de la lista."""
        if observer in self._observers:
            self._observers.remove(observer)
            print(f"Observador eliminado: {observer.__class__.__name__}")
    
    def notify(self, event: GameEvent):
        """Dispara la notificacion del evento a todos los suscriptores."""
        for observer in self._observers:
            observer.on_game_event(event)
    
    def clear_observers(self):
        """Elimina todos los observadores registrados."""
        self._observers.clear()


# ============================================================================
# OBSERVADORES CONCRETOS
# ============================================================================

class ConsoleLogger(GameEventObserver):
    """
    Observador Concreto - Logger:
    Su responsabilidad es registrar (imprimir) informacion sobre los eventos
    que ocurren en el sistema.
    """
    
    def on_game_event(self, event: GameEvent):
        messages = {
            GameEventType.CHECKPOINT_ACTIVATED: 
                lambda e: f"[CHECKPOINT] Checkpoint {e.data.get('checkpoint_id')} guardado",
            
            GameEventType.GOAL_REACHED: 
                lambda e: f"[META] Completaste {e.data.get('world_name', 'el nivel')}",
            
            GameEventType.PLAYER_DIED: 
                lambda e: f"[MUERTE] Jugador murio. Vidas restantes: {e.data.get('lives_remaining', 0)}",
            
            GameEventType.PLAYER_RESPAWNED: 
                lambda e: f"[RESPAWN] Jugador reaparece",
            
            GameEventType.ENEMY_KILLED: 
                lambda e: f"[COMBATE] Enemigo eliminado",
            
            GameEventType.POWERUP_COLLECTED: 
                lambda e: self._format_powerup_message(e.data.get('type')),
            
            GameEventType.WORLD_LOADED: 
                lambda e: f"[MUNDO] Mundo cargado: {e.data.get('world_name')}"
        }
        
        if event.event_type in messages:
            print(messages[event.event_type](event))
    
    def _format_powerup_message(self, powerup_type: str) -> str:
        messages = {
            'speed': "[POWERUP] Speed boost!",
            'jump': "[POWERUP] Jump boost!",
            'life': "[POWERUP] Extra life!"
        }
        return messages.get(powerup_type, "[POWERUP] Recolectado!")


class GameOverChecker(GameEventObserver):
    """
    Observador Concreto - Gestor de Game Over:
    Monitorea los eventos de muerte del jugador para determinar cuando
    se acaba el juego y cambiar el estado global.
    """
    
    def __init__(self, game):
        self.game = game
    
    def on_game_event(self, event: GameEvent):
        if event.event_type == GameEventType.PLAYER_DIED:
            lives = event.data.get('lives_remaining', 0)
            if lives <= 0:
                print("\nGAME OVER\n")
                self.game.menu_manager.current_state = GameState.GAME_OVER


class LevelCompleteChecker(GameEventObserver):
    """
    Observador Concreto - Completitud de Nivel:
    Verifica si se ha alcanzado la meta para transicionar al siguiente nivel
    o finalizar el juego.
    """
    
    def __init__(self, game):
        self.game = game
    
    def on_game_event(self, event: GameEvent):
        if event.event_type == GameEventType.GOAL_REACHED:
            
            # Determinar si es el ultimo mundo
            if self.game.current_world_index >= len(self.game.world_sequence) - 1:
                self.game.menu_manager.current_state = GameState.GAME_COMPLETE
                print("JUEGO COMPLETADO")
            else:
                self.game.menu_manager.current_state = GameState.LEVEL_COMPLETE
                print("Nivel completado, siguiente mundo disponible")


class CheckpointSaver(GameEventObserver):
    """
    Observador Concreto - Guardado Automatico:
    Se encarga de activar el guardado del Memento cuando se alcanza un checkpoint.
    """
    
    def __init__(self, checkpoint_manager):
        self.checkpoint_manager = checkpoint_manager
        self.game = None
    
    def set_game(self, game):
        self.game = game
    
    def on_game_event(self, event: GameEvent):
        if event.event_type == GameEventType.CHECKPOINT_ACTIVATED:
            if self.game is None:
                return
            
            checkpoint_id = event.data.get('checkpoint_id')
            if checkpoint_id is not None:
                memento = self.game.player.create_memento()
                self.checkpoint_manager.save_checkpoint(checkpoint_id, memento)

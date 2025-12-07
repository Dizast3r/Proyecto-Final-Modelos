"""
MEMENTO PATTERN - Para guardar y restaurar checkpoints
Permite guardar el estado del jugador y restaurarlo cuando sea necesario
"""

class PlayerMemento:
    """Memento que guarda el estado del jugador"""
    
    def __init__(self, x, y,speed, jump_power):
        self._x = x
        self._y = y
        self._velocity_x = 0 #el personaje volvio al checkpoint no se esta moviendo nada
        self._velocity_y = 0
        self.speed = speed
        self.jump_power = jump_power

    
    def get_state(self):
        """Retorna el estado guardado"""
        return {
            'x': self._x,
            'y': self._y,
            'velocity_x': self._velocity_x,
            'velocity_y': self._velocity_y,
            'speed': self.speed,
            'jump_power': self.jump_power
        }


class CheckpointManager:
    """Caretaker que maneja los checkpoints guardados"""
    
    def __init__(self):
        self._checkpoints = {}
        self._current_checkpoint = None
    
    def save_checkpoint(self, checkpoint_id, memento):
        """Guarda un checkpoint con un identificador"""
        self._checkpoints[checkpoint_id] = memento
        self._current_checkpoint = checkpoint_id
        print(f"✓ Checkpoint {checkpoint_id} guardado!")
    
    def get_checkpoint(self, checkpoint_id):
        """Recupera un checkpoint específico"""
        return self._checkpoints.get(checkpoint_id)
    
    def get_last_checkpoint(self):
        if self._current_checkpoint is not None:
            return self._checkpoints.get(self._current_checkpoint)
        return None

    
    def has_checkpoints(self):
        """Verifica si hay checkpoints guardados"""
        return len(self._checkpoints) > 0
    
    def clear_checkpoints(self):
        """Limpia todos los checkpoints"""
        self._checkpoints.clear()
        self._current_checkpoint = None
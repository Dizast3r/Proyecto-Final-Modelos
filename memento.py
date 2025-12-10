"""
Patron de Diseno Memento:
Permite capturar y externalizar el estado interno de un objeto (el jugador)
para que pueda ser restaurado posteriormente a este estado, sin violar su
encapsulamiento. Util para el sistema de checkpoints.
"""

class PlayerMemento:
    """
    Memento:
    Almacena el estado interno del objeto Originator (Player).
    Guarda la posicion, velocidad y atributos del jugador en un momento especifico.
    """
    
    def __init__(self, x, y, speed, jump_power):
        self._x = x
        self._y = y
        self._velocity_x = 0  # Al restaurar, el jugador aparece quieto
        self._velocity_y = 0
        self.speed = speed
        self.jump_power = jump_power

    def get_state(self):
        """Retorna el estado almacenado en el memento."""
        return {
            'x': self._x,
            'y': self._y,
            'velocity_x': self._velocity_x,
            'velocity_y': self._velocity_y,
            'speed': self.speed,
            'jump_power': self.jump_power
        }


class CheckpointManager:
    """
    Caretaker:
    Es responsable de guardar y resguardar los mementos (checkpoints).
    No opera ni inspecciona el contenido de los mementos.
    """
    
    def __init__(self):
        self._checkpoints = {}
        self._current_checkpoint = None
    
    def save_checkpoint(self, checkpoint_id, memento):
        """Guarda el memento asociado a un identificador unico."""
        self._checkpoints[checkpoint_id] = memento
        self._current_checkpoint = checkpoint_id
        print(f"Checkpoint {checkpoint_id} guardado")
    
    def get_checkpoint(self, checkpoint_id):
        """Recupera un memento especifico por su ID."""
        return self._checkpoints.get(checkpoint_id)
    
    def get_last_checkpoint(self):
        """Recupera el ultimo checkpoint guardado."""
        if self._current_checkpoint is not None:
            return self._checkpoints.get(self._current_checkpoint)
        return None
    
    def has_checkpoints(self):
        """Verifica si existen checkpoints almacenados."""
        return len(self._checkpoints) > 0
    
    def clear_checkpoints(self):
        """Elimina todos los checkpoints almacenados."""
        self._checkpoints.clear()
        self._current_checkpoint = None
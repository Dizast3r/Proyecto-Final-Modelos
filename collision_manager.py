"""
Gestor de colisiones/fisica.
Centraliza la logica de deteccion y resolucion de colisiones entre entidades.
Actua como mediador interactuando con:
- EventManager (Observer): Para notificar eventos (muerte, items, meta).
- CheckpointManager (Memento): Para gestionar la recuperacion de estado al morir.
"""

from game_events import GameEvent, GameEventType


class CollisionManager:
    """
    Clase que gestiona todas las colisiones del juego.
    Separa la logica de fisica de las entidades individuales.
    """
    
    def __init__(self, event_manager, checkpoint_manager):
        self.event_manager = event_manager
        self.checkpoint_manager = checkpoint_manager
    
    def check_all_collisions(self, player, checkpoints, goal, enemies, powerups, spikes, world_name):
        """Metodo fachada para verificar todos los tipos de colisiones en un frame."""
        player_rect = player.get_rect()
        
        # 1. Colisiones con checkpoints
        self._check_checkpoint_collisions(player_rect, checkpoints)
        
        # 2. Colisiones con goal
        self._check_goal_collision(player_rect, goal, world_name)
        
        # 3. Colisiones con PowerUps
        self._check_powerup_collisions(player_rect, player, powerups)
        
        # 4. Colisiones con enemigos
        self._check_enemy_collisions(player_rect, player, enemies)
        
        # 5. Colisiones con espinas
        self._check_spike_collisions(player_rect, player, spikes)
    
    def _check_checkpoint_collisions(self, player_rect, checkpoints):
        """Detecta y activa nuevos checkpoints."""
        for checkpoint in checkpoints:
            if player_rect.colliderect(checkpoint.get_rect()):
                if not checkpoint.activated:
                    checkpoint.activate()
                    # Notificar evento
                    event = GameEvent(
                        GameEventType.CHECKPOINT_ACTIVATED,
                        {'checkpoint_id': checkpoint.checkpoint_id}
                    )
                    self.event_manager.notify(event)
    
    def _check_goal_collision(self, player_rect, goal, world_name):
        """Detecta si el jugador ha llegado a la meta."""
        if goal and not goal.reached:
            if player_rect.colliderect(goal.get_rect()):
                goal.activate()
                # Notificar evento
                event = GameEvent(
                    GameEventType.GOAL_REACHED,
                    {'world_name': world_name}
                )
                self.event_manager.notify(event)
    
    def _check_powerup_collisions(self, player_rect, player, powerups):
        """Aplica efectos de PowerUps al colisionar."""
        for powerup in powerups:
            if powerup.collected:
                continue
            
            if player_rect.colliderect(powerup.get_rect()):
                powerup.apply_power(player)
                # Notificar evento
                event = GameEvent(
                    GameEventType.POWERUP_COLLECTED,
                    {'type': powerup.powerup_type}
                )
                self.event_manager.notify(event)
    
    def _check_enemy_collisions(self, player_rect, player, enemies):
        """
        Resuelve colisiones con enemigos.
        - Si el jugador cae sobre el enemigo: Enemigo muere.
        - Si es colision frontal/lateral: Jugador muere.
        """
        for enemy in enemies:
            if not enemy.alive:
                continue
            
            enemy_rect = enemy.get_rect()
            
            if player_rect.colliderect(enemy_rect):
                # Determinar tipo de colision
                player_bottom = player.y + player.height
                enemy_top = enemy_rect.y
                
                # Si el jugador viene desde arriba (aplastando)
                if player.velocity_y > 0 and player_bottom < enemy_top + 15:
                    enemy.die()
                    player.velocity_y = -10
                    # Notificar evento
                    event = GameEvent(GameEventType.ENEMY_KILLED, {})
                    self.event_manager.notify(event)
                else:
                    # Colision frontal - el enemigo mata al jugador
                    self._handle_player_death(player)
    
    def _check_spike_collisions(self, player_rect, player, spikes):
        """Mata al jugador si toca espinas."""
        for spike in spikes:
            if player_rect.colliderect(spike.get_rect()):
                self._handle_player_death(player)
    
    def _handle_player_death(self, player):
        """
        Coordina la logica de respawn usando Memento.
        Si hay vidas, restaura al ultimo checkpoint. Si no, reinicia o game over.
        """
        still_alive = player.die()
        
        # Notificar evento de muerte
        event = GameEvent(
            GameEventType.PLAYER_DIED,
            {'lives_remaining': player.lives}
        )
        self.event_manager.notify(event)
        
        if still_alive:
            # Intentar restaurar desde checkpoint (Memento Pattern)
            memento = self.checkpoint_manager.get_last_checkpoint()
            
            if memento:
                # Hay checkpoint: restaurar estado
                player.restore_from_memento(memento)
                print("Restaurado desde ultimo checkpoint")
            else:
                # NO hay checkpoint: resetear al spawn inicial
                player.reset_to_initial_spawn()
                print("Sin checkpoints, reiniciando al inicio")
            
            # Notificar evento de respawn
            event = GameEvent(GameEventType.PLAYER_RESPAWNED, {})
            self.event_manager.notify(event)

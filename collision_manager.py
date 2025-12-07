"""
Gestor de colisiones - Separa la lógica de detección de colisiones
"""

from game_events import GameEvent, GameEventType


class CollisionManager:
    """Maneja todas las colisiones del juego"""
    
    def __init__(self, event_manager, checkpoint_manager):
        self.event_manager = event_manager
        self.checkpoint_manager = checkpoint_manager
    
    def check_all_collisions(self, player, checkpoints, goal, enemies, powerups, spikes, world_name):
        """Verifica todas las colisiones del juego"""
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
        """Verifica colisiones con checkpoints"""
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
        """Verifica colisión con la meta"""
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
        """Verifica colisiones con PowerUps"""
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
        """Verifica colisiones con enemigos"""
        for enemy in enemies:
            if not enemy.alive:
                continue
            
            enemy_rect = enemy.get_rect()
            
            if player_rect.colliderect(enemy_rect):
                # Determinar tipo de colisión
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
                    # Colisión frontal - el enemigo mata al jugador
                    self._handle_player_death(player)
    
    def _check_spike_collisions(self, player_rect, player, spikes):
        """Verifica colisiones con espinas"""
        for spike in spikes:
            if player_rect.colliderect(spike.get_rect()):
                self._handle_player_death(player)
    
    def _handle_player_death(self, player):
        """Maneja la muerte del jugador"""
        still_alive = player.die()
        
        # Notificar evento de muerte
        event = GameEvent(
            GameEventType.PLAYER_DIED,
            {'lives_remaining': player.lives}
        )
        self.event_manager.notify(event)
        
        if still_alive:
            # Restaurar desde checkpoint
            memento = self.checkpoint_manager.get_last_checkpoint()
            if memento:
                player.restore_from_memento(memento)
            else:
                # No hay checkpoint, volver al inicio
                player.x = 100
                player.y = 100
                player.velocity_x = 0
                player.velocity_y = 0
            
            # Notificar evento de respawn
            event = GameEvent(GameEventType.PLAYER_RESPAWNED, {})
            self.event_manager.notify(event)
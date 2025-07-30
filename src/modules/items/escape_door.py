import pygame
from ..resource_manager import resource_manager

class EscapeDoor(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.world_x = x
        self.world_y = y
        self.is_locked = True
        self.is_opened = False
        
        # 创建逃生门图像（使用简单的矩形作为临时图像）
        self.image = pygame.Surface((32, 48), pygame.SRCALPHA)
        if self.is_locked:
            # 锁定的门 - 红色
            pygame.draw.rect(self.image, (200, 50, 50), (0, 0, 32, 48))
            pygame.draw.rect(self.image, (100, 25, 25), (0, 0, 32, 48), 2)
        else:
            # 解锁的门 - 绿色
            pygame.draw.rect(self.image, (50, 200, 50), (0, 0, 32, 48))
            pygame.draw.rect(self.image, (25, 100, 25), (0, 0, 32, 48), 2)
        
        # 添加门的把手
        pygame.draw.circle(self.image, (139, 69, 19), (8, 24), 3)
        pygame.draw.circle(self.image, (139, 69, 19), (24, 24), 3)
        
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        
        # 交互范围
        self.interaction_range = 40
        
    def update(self, player):
        """更新逃生门状态"""
        if self.is_opened:
            return
            
        # 计算与玩家的距离
        dx = player.world_x - self.world_x
        dy = player.world_y - self.world_y
        distance = (dx**2 + dy**2)**0.5
        
        # 检查玩家是否在交互范围内
        if distance < self.interaction_range:
            self._handle_interaction(player)
    
    def _handle_interaction(self, player):
        """处理玩家与门的交互"""
        if self.is_opened:
            return
            
        # 检查玩家是否有钥匙
        if hasattr(player, 'has_key') and player.has_key:
            # 玩家有钥匙，可以开启门
            self.is_locked = False
            self.is_opened = True
            self._update_appearance()
            
            # 显示胜利消息
            if hasattr(player, 'game') and player.game:
                player.game.show_message("You have opened the escape door! You win!", 5.0)
                player.game.game_victory = True
        else:
            # 玩家没有钥匙，显示提示
            if hasattr(player, 'game') and player.game:
                player.game.show_message("You need a key to open the escape door!", 2.0)
    
    def _update_appearance(self):
        """更新门的外观"""
        self.image = pygame.Surface((32, 48), pygame.SRCALPHA)
        if self.is_locked:
            # 锁定的门 - 红色
            pygame.draw.rect(self.image, (200, 50, 50), (0, 0, 32, 48))
            pygame.draw.rect(self.image, (100, 25, 25), (0, 0, 32, 48), 2)
        else:
            # 解锁的门 - 绿色
            pygame.draw.rect(self.image, (50, 200, 50), (0, 0, 32, 48))
            pygame.draw.rect(self.image, (25, 100, 25), (0, 0, 32, 48), 2)
        
        # 添加门的把手
        pygame.draw.circle(self.image, (139, 69, 19), (8, 24), 3)
        pygame.draw.circle(self.image, (139, 69, 19), (24, 24), 3)
    
    def render(self, screen, camera_x, camera_y, screen_center_x, screen_center_y):
        """渲染逃生门"""
        # 计算屏幕位置
        screen_x = screen_center_x + (self.world_x - camera_x)
        screen_y = screen_center_y + (self.world_y - camera_y)
        self.rect.center = (screen_x, screen_y)
        
        screen.blit(self.image, self.rect) 
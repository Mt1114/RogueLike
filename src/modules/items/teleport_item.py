import pygame
from .item import Item
from ..resource_manager import resource_manager

class TeleportItem(Item):
    """传送道具，可以将神秘剑客传送到忍者蛙身边"""
    
    def __init__(self, x, y):
        # 先创建图像，然后再调用父类初始化
        # 加载传送道具图标
        try:
            # 尝试加载传送图标
            self.image = resource_manager.load_image('teleport_icon', 'images/ui/transport.png')
            if self.image:
                # 缩放图标到合适大小
                self.image = pygame.transform.scale(self.image, (96, 96))
            else:
                # 如果加载失败，创建蓝色圆圈作为备用
                self.image = pygame.Surface((48, 48), pygame.SRCALPHA)
                pygame.draw.circle(self.image, (0, 100, 255), (24, 24), 24)
        except:
            # 如果加载失败，创建蓝色圆圈作为备用
            self.image = pygame.Surface((48, 48), pygame.SRCALPHA)
            pygame.draw.circle(self.image, (0, 100, 255), (24, 24), 24)
        
        # 现在调用父类初始化
        super().__init__(x, y, "teleport")
        
        # 传送相关属性
        self.teleport_duration = 1.0  # 传送持续时间（秒）
        self.teleport_timer = 0  # 传送计时器
        self.is_teleporting = False  # 是否正在传送
        self.mystic_start_pos = None  # 神秘剑客起始位置
        self.mystic_target_pos = None  # 神秘剑客目标位置
        
    def collect(self, player):
        """收集传送道具"""
        # 两个角色都可以收集传送道具，但效果转移给忍者蛙
        if hasattr(player, 'game') and player.game:
            # 确定实际受益者：传送道具总是给忍者蛙
            actual_beneficiary = player
            if hasattr(player, 'game') and player.game and hasattr(player.game, 'dual_player_system'):
                # 在双人模式下，传送道具总是给忍者蛙
                actual_beneficiary = player.game.dual_player_system.ninja_frog
            
            # 将道具添加到实际受益者的道具栏
            if not hasattr(actual_beneficiary, 'teleport_items'):
                actual_beneficiary.teleport_items = 0
            actual_beneficiary.teleport_items += 1
            
            # 从传送道具管理器中移除道具
            if hasattr(player, 'game') and player.game and hasattr(player.game, 'teleport_manager'):
                player.game.teleport_manager.remove_item(self)
                
            return True
        return False
    
    def use_teleport(self, dual_player_system):
        """使用传送道具"""
        if not hasattr(dual_player_system.ninja_frog, 'teleport_items') or dual_player_system.ninja_frog.teleport_items <= 0:
            return False
            
        # 消耗一个传送道具
        dual_player_system.ninja_frog.teleport_items -= 1
        
        # 开始传送
        self.is_teleporting = True
        self.teleport_timer = 0
        
        # 记录神秘剑客的起始位置
        self.mystic_start_pos = (dual_player_system.mystic_swordsman.world_x, dual_player_system.mystic_swordsman.world_y)
        
        # 计算目标位置（忍者蛙身边，距离忍者蛙50像素）
        ninja_x = dual_player_system.ninja_frog.world_x
        ninja_y = dual_player_system.ninja_frog.world_y
        
        # 计算从忍者蛙到神秘剑客的方向
        dx = self.mystic_start_pos[0] - ninja_x
        dy = self.mystic_start_pos[1] - ninja_y
        distance = (dx**2 + dy**2)**0.5
        
        if distance > 0:
            # 归一化方向向量
            dx /= distance
            dy /= distance
            
            # 目标位置：忍者蛙身边50像素
            target_distance = 0
            self.mystic_target_pos = (
                ninja_x + dx * target_distance,
                ninja_y + dy * target_distance
            )
        else:
            # 如果神秘剑客就在忍者蛙位置，稍微偏移一点
            self.mystic_target_pos = (ninja_x + 0, ninja_y)
            
        
        return True
    
    def update_teleport(self, dt, dual_player_system):
        """更新传送状态"""
        if not self.is_teleporting:
            return
            
        self.teleport_timer += dt
        progress = min(self.teleport_timer / self.teleport_duration, 1.0)
        
        # 使用缓动函数使传送更平滑
        ease_progress = 1 - (1 - progress) ** 3  # 缓出效果
        
        if self.mystic_start_pos and self.mystic_target_pos:
            # 插值计算神秘剑客的新位置
            start_x, start_y = self.mystic_start_pos
            target_x, target_y = self.mystic_target_pos
            
            dual_player_system.mystic_swordsman.world_x = start_x + (target_x - start_x) * ease_progress
            dual_player_system.mystic_swordsman.world_y = start_y + (target_y - start_y) * ease_progress
        
        # 传送完成
        if progress >= 1.0:
            self.is_teleporting = False
            self.teleport_timer = 0
            self.mystic_start_pos = None
            self.mystic_target_pos = None
            
            
    def is_teleport_active(self):
        """检查是否正在传送"""
        return self.is_teleporting
        
    def check_collision(self, player):
        """检查与玩家的碰撞"""
        if self.collected:
            return False
            
        # 计算与玩家的距离
        dx = player.world_x - self.world_x
        dy = player.world_y - self.world_y
        distance = (dx**2 + dy**2)**0.5
        
        # 如果距离小于拾取范围，则发生碰撞
        return distance < 32  # 32像素的拾取范围 
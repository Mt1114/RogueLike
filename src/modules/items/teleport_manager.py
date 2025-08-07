import random
import pygame
from .teleport_item import TeleportItem

class TeleportManager:
    """传送道具管理器"""
    
    def __init__(self, map_manager):
        self.map_manager = map_manager
        self.teleport_items = []
        self.spawned_count = 0
        self.max_items = 10  # 最大同时存在的传送道具数量（因为存在时间较长）
        
        # 生成计时器
        self.spawn_timer = 0
        self.spawn_interval = 20.0  # 每60秒生成一个传送道具
        
        # 道具存在时间
        self.item_lifetime = 120.0  # 传送道具存在120秒（2分钟）
        
    def spawn_teleport_item(self):
        """生成一个传送道具"""
        if len(self.teleport_items) >= self.max_items:
            return
            
        # 获取地图边界
        map_width = self.map_manager.map_width
        map_height = self.map_manager.map_height
        
        # 随机生成位置
        attempts = 0
        max_attempts = 50
        
        while attempts < max_attempts:
            x = random.randint(100, map_width - 100)
            y = random.randint(100, map_height - 100)
            
            # 检查位置是否合适（不在墙壁内）
            if not self._is_position_blocked(x, y):
                teleport_item = TeleportItem(x, y)
                self.teleport_items.append(teleport_item)
                self.spawned_count += 1
                
                return teleport_item
                
            attempts += 1
            
        
        
    def _is_position_blocked(self, x, y):
        """检查位置是否被阻挡"""
        if not self.map_manager:
            return False
            
        # 获取碰撞图块
        collision_tiles = self.map_manager.get_collision_tiles()
        
        # 检查位置是否与任何碰撞图块重叠
        player_rect = pygame.Rect(x - 48, y - 48, 96, 96)  # 传送道具大小为96x96
        
        for tile_rect in collision_tiles:
            if player_rect.colliderect(tile_rect):
                return True
                
        return False
        
    def update(self, dt, player):
        """更新传送道具"""
        # 更新生成计时器
        self.spawn_timer += dt
        
        # 每60秒生成一个新的传送道具
        if self.spawn_timer >= self.spawn_interval:
            self.spawn_timer = 0
            self.spawn_teleport_item()
        
        # 检查玩家是否收集了传送道具
        for teleport_item in self.teleport_items[:]:  # 使用切片创建副本避免修改迭代列表
            if teleport_item.check_collision(player):
                if teleport_item.collect(player):
                    # 收集成功后，传送道具会自动从管理器中移除
                    # 这里不需要再次移除，因为 collect 方法已经处理了
                    pass
                    
        # 更新传送道具位置和生命周期
        for teleport_item in self.teleport_items[:]:  # 使用切片创建副本避免修改迭代列表
            teleport_item.update(dt, player)
            
            # 更新道具的生命周期
            if not hasattr(teleport_item, 'lifetime_timer'):
                teleport_item.lifetime_timer = 0
            teleport_item.lifetime_timer += dt
            
            # 如果道具存在时间超过2分钟，自动移除
            if teleport_item.lifetime_timer >= self.item_lifetime:
                self.teleport_items.remove(teleport_item)
                
            
    def render(self, screen, camera_x, camera_y):
        """渲染传送道具"""
        screen_center_x = screen.get_width() // 2
        screen_center_y = screen.get_height() // 2
        for teleport_item in self.teleport_items:
            teleport_item.render(screen, camera_x, camera_y, screen_center_x, screen_center_y)
            
    def get_items(self):
        """获取所有传送道具"""
        return self.teleport_items
        
    def remove_item(self, item):
        """移除传送道具"""
        if item in self.teleport_items:
            self.teleport_items.remove(item)
            
    def clear_all(self):
        """清除所有传送道具"""
        self.teleport_items.clear() 
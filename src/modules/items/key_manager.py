import pygame
import random
from .item import Item

class KeyManager:
    """钥匙管理器，负责按时间生成钥匙"""
    
    def __init__(self, game):
        self.game = game
        self.keys = []  # 当前存在的钥匙列表
        self.spawned_keys = 0  # 已生成的钥匙数量
        self.max_keys = 3  # 最大钥匙数量
        self.key_spawn_times = [0.0, 60.0,120.0]  # 钥匙生成时间点（秒）
        self.spawned_keys_set = set()  # 记录已生成的钥匙时间点
        
    def update(self, dt, game_time):
        """更新钥匙管理器
        
        Args:
            dt: 时间增量
            game_time: 当前游戏时间（秒）
        """
        # 检查是否需要生成新钥匙
        for i, spawn_time in enumerate(self.key_spawn_times):
            if (game_time >= spawn_time and 
                i not in self.spawned_keys_set and 
                len(self.keys) < self.max_keys):
                self._spawn_key(i + 1)  # 传递钥匙编号
                self.spawned_keys_set.add(i)
                
    
    def _spawn_key(self, key_id):
        """生成一把新钥匙
        
        Args:
            key_id: 钥匙编号（1, 2, 3）
        """
        if not self.game or not self.game.map_manager:
            return
            
        # 获取地图尺寸
        map_width, map_height = self.game.map_manager.get_map_size()
        
        # 获取碰撞图块
        collision_tiles = self.game.map_manager.get_collision_tiles()
        
        # 尝试找到有效位置
        max_attempts = 100
        for attempt in range(max_attempts):
            # 随机生成位置（避开边缘）
            margin = 50
            x = random.randint(margin, map_width - margin)
            y = random.randint(margin, map_height - margin)
            
            # 检查位置是否有效（不与墙壁碰撞）
            if self._is_valid_position(x, y, collision_tiles):
                # 创建钥匙
                key_item = Item(x, y, 'key')
                key_item.key_id = key_id  # 给钥匙一个唯一ID
                self.keys.append(key_item)
                
                # 添加到物品管理器
                if self.game.item_manager:
                    self.game.item_manager.items.append(key_item)
                
                
                return
        
       
    
    def _is_valid_position(self, x, y, collision_tiles):
        """检查位置是否有效（不与墙壁碰撞）
        
        Args:
            x, y: 要检查的位置
            collision_tiles: 碰撞图块列表
            
        Returns:
            bool: 位置是否有效
        """
        # 创建钥匙的碰撞矩形（钥匙大小为48x48）
        key_rect = pygame.Rect(x - 24, y - 24, 48, 48)
        
        # 检查是否与任何碰撞图块重叠
        for tile_rect in collision_tiles:
            if key_rect.colliderect(tile_rect):
                return False
        
        # 检查是否与其他钥匙重叠
        for key in self.keys:
            if hasattr(key, 'rect'):
                key_rect_other = pygame.Rect(key.world_x - 24, key.world_y - 24, 48, 48)
                if key_rect.colliderect(key_rect_other):
                    return False
        
        return True
    
    def remove_key(self, key_item):
        """移除钥匙
        
        Args:
            key_item: 要移除的钥匙对象
        """
        try:
            if key_item in self.keys:
                self.keys.remove(key_item)
        except ValueError:
            pass
            
        try:
            if self.game.item_manager and key_item in self.game.item_manager.items:
                self.game.item_manager.items.remove(key_item)
        except ValueError:
            pass
    
    def get_key_count(self):
        """获取当前存在的钥匙数量"""
        return len(self.keys)
    
    def get_total_spawned(self):
        """获取已生成的总钥匙数量"""
        return self.spawned_keys
        
    def on_key_collected(self):
        """当钥匙被拾取时调用"""
        # 钥匙被拾取，不需要生成新的钥匙（钥匙按时间生成）
        
        
    def get_next_key_spawn_time(self, game_time):
        """获取下一把钥匙的生成时间
        
        Args:
            game_time: 当前游戏时间（秒）
            
        Returns:
            float: 下一把钥匙的生成时间（秒），如果所有钥匙都已生成则返回None
        """
        for i, spawn_time in enumerate(self.key_spawn_times):
            if i not in self.spawned_keys_set:
                return spawn_time
        return None
        
    def get_next_key_countdown(self, game_time):
        """获取下一把钥匙的倒计时
        
        Args:
            game_time: 当前游戏时间（秒）
            
        Returns:
            float: 倒计时秒数，如果所有钥匙都已生成则返回None
        """
        next_spawn_time = self.get_next_key_spawn_time(game_time)
        if next_spawn_time is None:
            return None
        return max(0, next_spawn_time - game_time) 
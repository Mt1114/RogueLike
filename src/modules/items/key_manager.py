import pygame
import random
from .item import Item

class KeyManager:
    """钥匙管理器，负责按时间生成钥匙"""
    
    def __init__(self, game):
        self.game = game
        self.keys = []  # 当前存在的钥匙列表
        self.key_spawn_times = [0, 90, 210]  # 钥匙生成时间（秒）：0秒、1:30、3:30
        self.spawned_keys = 0  # 已生成的钥匙数量
        self.max_keys = 3  # 最大钥匙数量
        
    def update(self, dt, game_time):
        """更新钥匙管理器
        
        Args:
            dt: 时间增量
            game_time: 当前游戏时间（秒）
        """
        # 检查是否需要生成新钥匙
        for i, spawn_time in enumerate(self.key_spawn_times):
            if (game_time >= spawn_time and 
                self.spawned_keys <= i and 
                self.spawned_keys < self.max_keys):
                self._spawn_key()
                self.spawned_keys += 1
                print(f"生成第 {self.spawned_keys} 把钥匙，游戏时间: {game_time:.1f}秒")
    
    def _spawn_key(self):
        """生成一把新钥匙"""
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
                key_item.key_id = self.spawned_keys + 1  # 给钥匙一个唯一ID
                self.keys.append(key_item)
                
                # 添加到物品管理器
                if self.game.item_manager:
                    self.game.item_manager.items.append(key_item)
                
                print(f"钥匙 {key_item.key_id} 生成在位置 ({x}, {y})")
                return
        
        print("警告：无法找到有效的钥匙生成位置")
    
    def _is_valid_position(self, x, y, collision_tiles):
        """检查位置是否有效（不与墙壁碰撞）
        
        Args:
            x, y: 要检查的位置
            collision_tiles: 碰撞图块列表
            
        Returns:
            bool: 位置是否有效
        """
        # 创建钥匙的碰撞矩形（假设钥匙大小为16x16）
        key_rect = pygame.Rect(x - 8, y - 8, 16, 16)
        
        # 检查是否与任何碰撞图块重叠
        for tile_rect in collision_tiles:
            if key_rect.colliderect(tile_rect):
                return False
        
        # 检查是否与其他钥匙重叠
        for key in self.keys:
            if hasattr(key, 'rect'):
                key_rect_other = pygame.Rect(key.world_x - 8, key.world_y - 8, 16, 16)
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
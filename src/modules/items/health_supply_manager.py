"""
生命补给管理器
管理生命补给物品的生成、更新和拾取
"""

import pygame
import random
import math
from .health_supply import HealthSupply

class HealthSupplyManager:
    """生命补给管理器"""
    
    def __init__(self, game):
        """
        初始化生命补给管理器
        
        Args:
            game: 游戏实例
        """
        self.game = game
        self.supplies = []  # 补给物品列表
        self.spawn_timer = 0.0  # 生成计时器
        self.spawn_interval = 30.0  # 生成间隔（30秒）
        self.spawn_count = 1  # 每次生成1个补给
        
        # 生成区域（地图边界内）
        self.spawn_margin = 100  # 距离地图边缘的最小距离
        
        # 游戏开始时立即生成一些补给
        print("初始化生命补给管理器...")
        self._generate_initial_supplies()
        
    def _generate_initial_supplies(self):
        """游戏开始时生成初始补给"""
        print("生成初始生命补给...")
        for i in range(3):  # 生成3个初始补给
            self.spawn_supply()
        
        
    def update(self, dt):
        """更新补给管理器"""
        # 更新生成计时器
        self.spawn_timer += dt
        
        # 检查是否需要生成新的补给
        if self.spawn_timer >= self.spawn_interval:
            
            # 生成1个补给
            for i in range(self.spawn_count):
                self.spawn_supply()
            self.spawn_timer = 0.0
            
        
        # 更新所有补给物品
        for supply in self.supplies[:]:  # 使用切片创建副本，避免在迭代时修改列表
            if not supply.update(dt):
                # 如果补给超时，移除它
                self.supplies.remove(supply)
                
                
    def spawn_supply(self):
        """生成一个新的生命补给"""
        if not hasattr(self.game, 'map_manager'):
            print("错误: 游戏没有地图管理器")
            return
            
        # 获取地图尺寸
        map_width = self.game.map_manager.map_width
        map_height = self.game.map_manager.map_height
        
        # 尝试生成补给，最多尝试100次
        for attempt in range(100):
            # 随机生成位置
            x = random.randint(self.spawn_margin, map_width - self.spawn_margin)
            y = random.randint(self.spawn_margin, map_height - self.spawn_margin)
            
            # 检查位置是否有效
            if self._is_valid_spawn_position(x, y):
                # 创建补给
                supply = HealthSupply(x, y)
                self.supplies.append(supply)
                
                return
            
        
        
        
    def _is_valid_spawn_position(self, x, y):
        """检查位置是否适合生成补给
        
        Args:
            x, y: 要检查的位置坐标
            
        Returns:
            bool: 如果位置有效返回True，否则返回False
        """
        # 检查是否在地图边界内
        if not hasattr(self.game, 'map_manager'):
            return False
            
        map_width = self.game.map_manager.map_width
        map_height = self.game.map_manager.map_height
        
        # 确保位置在地图边界内
        if x < self.spawn_margin or x > map_width - self.spawn_margin:
            return False
        if y < self.spawn_margin or y > map_height - self.spawn_margin:
            return False
            
        # 检查是否与墙壁重叠
        collision_tiles = self.game.map_manager.get_collision_tiles()
        if collision_tiles:
            for tile in collision_tiles:
                # 检查补给位置是否与墙壁重叠
                if tile.collidepoint(x, y):
                    return False
                    
                # 检查补给区域是否与墙壁重叠（96x96区域）
                supply_rect = pygame.Rect(x - 48, y - 48, 96, 96)
                if tile.colliderect(supply_rect):
                    return False
        else:
            print(f"警告: 没有找到碰撞图块数据")
                
        # 检查是否与玩家重叠
        if hasattr(self.game, 'player'):
            player_rect = pygame.Rect(x - 32, y - 32, 64, 64)
            if player_rect.colliderect(self.game.player.collision_rect):
                return False
                
        # 检查是否与弹药补给重叠
        if hasattr(self.game, 'ammo_supply_manager'):
            for ammo_supply in self.game.ammo_supply_manager.supplies:
                supply_rect = pygame.Rect(x - 48, y - 48, 96, 96)
                if supply_rect.colliderect(ammo_supply.rect):
                    return False
        
        # 检查是否与其他生命补给重叠
        for supply in self.supplies:
            supply_rect = pygame.Rect(x - 48, y - 48, 96, 96)
            if supply_rect.colliderect(supply.rect):
                return False
                
        return True
        
    def check_pickup(self, player):
        """检查玩家是否拾取了补给
        
        Args:
            player: 玩家实例
        """
        # 生命补给两个角色都可以拾取，但效果转移给忍者蛙
            
        for supply in self.supplies[:]:
            # 检查玩家是否与补给重叠
            # 使用玩家的碰撞区域和补给的碰撞区域进行检测
            if hasattr(player, 'collision_rect') and hasattr(supply, 'rect'):
                # 添加调试信息
           
                
                if player.collision_rect.colliderect(supply.rect):
                    # 确定实际受益者：生命补给总是给忍者蛙
                    actual_beneficiary = player
                    if hasattr(player, 'game') and player.game and hasattr(player.game, 'dual_player_system'):
                        # 在双人模式下，生命补给总是给忍者蛙
                        actual_beneficiary = player.game.dual_player_system.ninja_frog
                    
                    if supply.on_pickup(actual_beneficiary):
                        # 拾取成功，移除补给
                        self.supplies.remove(supply)
                      
                        return  # 一次只能拾取一个补给
                else:
                    # 计算距离
                    distance = ((player.world_x - supply.world_x) ** 2 + 
                              (player.world_y - supply.world_y) ** 2) ** 0.5
                 
                    
                    # 如果距离很近但碰撞检测失败，尝试扩大检测范围
                    if distance < 50:  # 如果距离小于50像素
                        # 扩大玩家的碰撞检测范围
                        expanded_player_rect = player.collision_rect.inflate(20, 20)
                        if expanded_player_rect.colliderect(supply.rect):
                            # 确定实际受益者：生命补给总是给忍者蛙
                            actual_beneficiary = player
                            if hasattr(player, 'game') and player.game and hasattr(player.game, 'dual_player_system'):
                                # 在双人模式下，生命补给总是给忍者蛙
                                actual_beneficiary = player.game.dual_player_system.ninja_frog
                            
                            if supply.on_pickup(actual_beneficiary):
                                self.supplies.remove(supply)
                              
                                return
                    
    def render(self, screen, camera_x, camera_y, screen_center_x=None, screen_center_y=None):
        """渲染所有补给物品
        
        Args:
            screen: pygame屏幕对象
            camera_x: 相机X坐标
            camera_y: 相机Y坐标
            screen_center_x: 屏幕中心X坐标
            screen_center_y: 屏幕中心Y坐标
        """
        for supply in self.supplies:
            supply.render(screen, camera_x, camera_y, screen_center_x, screen_center_y)
            
    def get_supplies_for_minimap(self):
        """获取补给物品列表用于小地图显示
        
        Returns:
            list: 补给物品列表
        """
        return self.supplies
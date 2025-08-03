"""
弹药补给管理器
负责生成和管理弹药补给物品
"""

import pygame
import random
import math
from .ammo_supply import AmmoSupply

class AmmoSupplyManager:
    """弹药补给管理器"""
    
    def __init__(self, game):
        """
        初始化弹药补给管理器
        
        Args:
            game: 游戏实例
        """
        self.game = game
        self.supplies = []  # 补给物品列表
        self.spawn_timer = 0.0  # 生成计时器
        self.spawn_interval = 30.0  # 生成间隔（30秒）
        self.spawn_count = 1  # 每次生成1个补给
        
        # 生成区域（地图边界内）
        self.spawn_margin = 400  # 距离地图边缘的最小距离（考虑4倍缩放）
        
        # 游戏开始时立即生成一些补给
        print("初始化弹药补给管理器...")
        self._generate_initial_supplies()
        
    def _generate_initial_supplies(self):
        """游戏开始时生成初始补给"""
        print("生成初始补给...")
        for i in range(3):  # 生成3个初始补给
            self.spawn_supply()
        print(f"初始补给生成完成，当前补给数量: {len(self.supplies)}")
        
    def update(self, dt):
        """更新补给管理器"""
        # 更新生成计时器
        self.spawn_timer += dt
        
        # 检查是否需要生成新的补给
        if self.spawn_timer >= self.spawn_interval:
            print(f"开始生成 {self.spawn_count} 个补给...")
            # 生成1个补给
            for i in range(self.spawn_count):
                self.spawn_supply()
            self.spawn_timer = 0.0
            print(f"当前补给数量: {len(self.supplies)}")
        
        # 更新所有补给物品
        for supply in self.supplies[:]:  # 使用切片创建副本，避免在迭代时修改列表
            if not supply.update(dt):
                # 如果补给超时，移除它
                self.supplies.remove(supply)
                print(f"补给超时移除，剩余补给数量: {len(self.supplies)}")
                
    def spawn_supply(self):
        """生成新的弹药补给"""
        if not hasattr(self.game, 'map_manager'):
            print("地图管理器未初始化，无法生成补给")
            return
            
        # 获取地图边界
        map_width = self.game.map_manager.map_width
        map_height = self.game.map_manager.map_height
        
        # 在有效区域内随机生成位置
        attempts = 0
        max_attempts = 100  # 增加尝试次数
        
        while attempts < max_attempts:
            # 随机生成位置（确保在地图边界内）
            x = random.randint(self.spawn_margin, map_width - self.spawn_margin)
            y = random.randint(self.spawn_margin, map_height - self.spawn_margin)
            
            # 检查位置是否有效（不与墙壁重叠）
            if self._is_valid_spawn_position(x, y):
                # 创建新的补给物品
                supply = AmmoSupply(x, y)
                self.supplies.append(supply)
                print(f"✓ 成功生成弹药补给在位置 ({x}, {y})")
                return
            else:
                if attempts < 3:  # 只打印前3次失败的尝试
                    print(f"✗ 位置 ({x}, {y}) 无效，重新生成...")
                
            attempts += 1
            
        print(f"❌ 无法找到有效的补给生成位置，尝试了 {max_attempts} 次")
        
    def _is_valid_spawn_position(self, x, y):
        """检查生成位置是否有效
        
        Args:
            x, y: 生成位置的坐标
            
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
                    
                # 检查补给区域是否与墙壁重叠（32x32区域）
                supply_rect = pygame.Rect(x - 16, y - 16, 32, 32)
                if tile.colliderect(supply_rect):
                    return False
        else:
            print(f"警告: 没有找到碰撞图块数据")
                
        # 检查是否与玩家重叠
        if hasattr(self.game, 'player'):
            player_rect = pygame.Rect(x - 32, y - 32, 64, 64)
            if player_rect.colliderect(self.game.player.collision_rect):
                return False
                
        # 检查是否与其他补给重叠
        for supply in self.supplies:
            supply_rect = pygame.Rect(x - 16, y - 16, 32, 32)
            if supply_rect.colliderect(supply.rect):
                return False
                
        return True
        
    def check_pickup(self, player):
        """检查玩家是否拾取了补给
        
        Args:
            player: 玩家实例
        """
       
        
        # 弹药补给只能由神秘剑士拾取
        if not hasattr(player, 'hero_type') or player.hero_type != "role2":
            
            return
            
        for supply in self.supplies[:]:
            # 检查玩家是否与补给重叠
            # 使用玩家的碰撞区域和补给的碰撞区域进行检测
            if hasattr(player, 'collision_rect') and hasattr(supply, 'rect'):
                # 添加调试信息
                
                
                if player.collision_rect.colliderect(supply.rect):
                    
                    if supply.on_pickup(player):
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
                            if supply.on_pickup(player):
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
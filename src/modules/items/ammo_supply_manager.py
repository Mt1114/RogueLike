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
        self.spawn_interval = 20.0  # 生成间隔（20秒）
        self.spawn_count = 5  # 每次生成5个补给
        
        # 生成区域（地图边界内）
        self.spawn_margin = 100  # 距离地图边缘的最小距离
        
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
            # 生成5个补给
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
                print(f"生成弹药补给在位置 ({x}, {y})")
                return
                
            attempts += 1
            
        print(f"无法找到有效的补给生成位置，尝试了 {max_attempts} 次")
        
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
        if hasattr(self.game.map_manager, 'collision_tiles'):
            for tile in self.game.map_manager.collision_tiles:
                # 检查补给位置是否与墙壁重叠
                if tile.collidepoint(x, y):
                    return False
                    
                # 检查补给区域是否与墙壁重叠（32x32区域）
                supply_rect = pygame.Rect(x - 16, y - 16, 32, 32)
                if tile.colliderect(supply_rect):
                    return False
                
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
        for supply in self.supplies[:]:
            # 检查玩家是否与补给重叠
            # 使用玩家的碰撞区域和补给的碰撞区域进行检测
            if hasattr(player, 'collision_rect') and hasattr(supply, 'rect'):
                # 打印调试信息
                print(f"玩家碰撞区域: {player.collision_rect}")
                print(f"补给碰撞区域: {supply.rect}")
                print(f"玩家世界坐标: ({player.world_x}, {player.world_y})")
                print(f"补给世界坐标: ({supply.world_x}, {supply.world_y})")
                
                if player.collision_rect.colliderect(supply.rect):
                    print(f"检测到补给拾取碰撞！")
                    if supply.on_pickup(player):
                        # 拾取成功，移除补给
                        self.supplies.remove(supply)
                        print("拾取弹药补给成功！")
                        return  # 一次只能拾取一个补给
                else:
                    # 计算距离
                    distance = ((player.world_x - supply.world_x) ** 2 + 
                              (player.world_y - supply.world_y) ** 2) ** 0.5
                    print(f"玩家与补给距离: {distance:.2f}")
                    
                    # 如果距离很近但碰撞检测失败，尝试扩大检测范围
                    if distance < 50:  # 如果距离小于50像素
                        print("距离很近但碰撞检测失败，尝试扩大检测范围")
                        # 扩大玩家的碰撞检测范围
                        expanded_player_rect = player.collision_rect.inflate(20, 20)
                        if expanded_player_rect.colliderect(supply.rect):
                            print("使用扩大范围检测到碰撞！")
                            if supply.on_pickup(player):
                                self.supplies.remove(supply)
                                print("拾取弹药补给成功！")
                                return
                    
    def render(self, screen, camera_x, camera_y):
        """渲染所有补给物品
        
        Args:
            screen: pygame屏幕对象
            camera_x: 相机X坐标
            camera_y: 相机Y坐标
        """
        # 添加调试信息
        if len(self.supplies) > 0:
            print(f"渲染 {len(self.supplies)} 个补给，相机位置: ({camera_x}, {camera_y})")
            
        for supply in self.supplies:
            supply.render(screen, camera_x, camera_y)
            
    def get_supplies_for_minimap(self):
        """获取补给物品列表用于小地图显示
        
        Returns:
            list: 补给物品列表
        """
        return self.supplies 
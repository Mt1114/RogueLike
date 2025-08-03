"""
移动组件
负责处理实体的移动、方向和速度计算
"""

import pygame
from .base_component import Component

class MovementComponent(Component):
    """移动组件，处理实体的移动逻辑"""
    
    def __init__(self, owner, speed=200):
        """
        初始化移动组件
        
        Args:
            owner: 组件所属的实体
            speed: 移动速度
        """
        super().__init__(owner)
        
        # 基础属性
        self.base_speed = speed
        self.speed = speed
        
        # 移动状态
        self.velocity = pygame.math.Vector2()
        self.direction = pygame.math.Vector2()
        self.last_movement_direction = pygame.math.Vector2(1, 0)
        
        # 移动输入状态
        self.moving = {
            'up': False, 
            'down': False, 
            'left': False, 
            'right': False
        }
        
        # 朝向状态 - 基于鼠标方向
        self.facing_right = True
        self.mouse_direction = pygame.math.Vector2(1, 0)  # 鼠标方向向量
        
        # 边界检测
        self.boundaries = None  # (min_x, min_y, max_x, max_y)
        
        # 地图碰撞检测
        self.collision_tiles = []  # 碰撞图块列表
        self.tile_width = 32  # 默认瓦片宽度
        self.tile_height = 32  # 默认瓦片高度
        
    def set_boundaries(self, min_x, min_y, max_x, max_y):
        """
        设置移动边界
        
        Args:
            min_x: 最小X坐标
            min_y: 最小Y坐标
            max_x: 最大X坐标
            max_y: 最大Y坐标
        """
        self.boundaries = (min_x, min_y, max_x, max_y)
        
    def set_collision_tiles(self, collision_tiles, tile_width=32, tile_height=32):
        """
        设置碰撞图块数据
        
        Args:
            collision_tiles: 碰撞图块矩形列表
            tile_width: 瓦片宽度
            tile_height: 瓦片高度
        """
        self.collision_tiles = collision_tiles
        self.tile_width = tile_width
        self.tile_height = tile_height
        
    def _check_collision(self, new_x, new_y):
        """
        检查新位置是否与碰撞图块重叠
        
        Args:
            new_x: 新的X坐标
            new_y: 新的Y坐标
            
        Returns:
            bool: 如果发生碰撞返回True，否则返回False
        """
        if not self.collision_tiles:
            return False
            
        # 使用玩家的collision_rect进行碰撞检测
        if hasattr(self.owner, 'collision_rect'):
            # 创建玩家在新位置的碰撞矩形
            player_rect = pygame.Rect(
                new_x - self.owner.collision_rect.width // 2,
                new_y - self.owner.collision_rect.height // 2,
                self.owner.collision_rect.width,
                self.owner.collision_rect.height
            )
        else:
            # 回退到使用rect
            player_rect = pygame.Rect(
                new_x - self.owner.rect.width // 2,
                new_y - self.owner.rect.height // 2,
                self.owner.rect.width,
                self.owner.rect.height
            )
        
        # 检查与所有碰撞图块的碰撞
        for tile_rect in self.collision_tiles:
            if player_rect.colliderect(tile_rect):
                return True
                
        return False
        
    def handle_event(self, event):
        """
        处理移动相关的输入事件
        
        Args:
            event: Pygame事件对象
        """
        if not self.enabled:
            return
            
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_w:
                self.moving['up'] = True
            elif event.key == pygame.K_s:
                self.moving['down'] = True
            elif event.key == pygame.K_a:
                self.moving['left'] = True
                # 角色朝向：A键朝左
                self.facing_right = False
            elif event.key == pygame.K_d:
                self.moving['right'] = True
                # 角色朝向：D键朝右
                self.facing_right = True
                
        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_w:
                self.moving['up'] = False
            elif event.key == pygame.K_s:
                self.moving['down'] = False
            elif event.key == pygame.K_a:
                self.moving['left'] = False
            elif event.key == pygame.K_d:
                self.moving['right'] = False
        
        # 更新移动方向
        self._update_movement_direction()
        
    def update(self, dt):
        """
        更新移动状态
        
        Args:
            dt: 时间增量（秒）
        """
        if not self.enabled:
            return
            
        # 计算速度
        self.velocity = self.direction * self.speed
        
        # 更新实体位置
        if hasattr(self.owner, 'world_x') and hasattr(self.owner, 'world_y'):
            new_x = self.owner.world_x + self.velocity.x * dt
            new_y = self.owner.world_y + self.velocity.y * dt
            
            # 应用边界检测
            if self.boundaries:
                min_x, min_y, max_x, max_y = self.boundaries
                new_x = max(min_x, min(new_x, max_x))
                new_y = max(min_y, min(new_y, max_y))
            
            # 检查地图碰撞（如果不在穿墙状态且不在强制拉回状态）
            is_force_pulling = False
            if hasattr(self.owner, 'game') and hasattr(self.owner.game, 'dual_player_system'):
                dual_system = self.owner.game.dual_player_system
                if hasattr(dual_system, 'is_force_pulling'):
                    is_force_pulling = dual_system.is_force_pulling
            
            if hasattr(self.owner, 'phase_through_walls') and self.owner.phase_through_walls:
                # 穿墙状态，直接移动
                self.owner.world_x = new_x
                self.owner.world_y = new_y
            elif is_force_pulling:
                # 强制拉回状态，忽略碰撞直接移动
                self.owner.world_x = new_x
                self.owner.world_y = new_y
            elif not self._check_collision(new_x, new_y):
                self.owner.world_x = new_x
                self.owner.world_y = new_y
            else:
                # 如果发生碰撞，尝试分别检查X和Y方向的移动
                # 先尝试只移动X方向
                if not self._check_collision(new_x, self.owner.world_y):
                    self.owner.world_x = new_x
                # 再尝试只移动Y方向
                elif not self._check_collision(self.owner.world_x, new_y):
                    self.owner.world_y = new_y
    
    def _update_mouse_direction(self):
        """更新鼠标朝向"""
        # 获取鼠标位置
        mouse_x, mouse_y = pygame.mouse.get_pos()
        
        # 获取屏幕中心（假设游戏窗口居中）
        screen_width = pygame.display.get_surface().get_width()
        screen_height = pygame.display.get_surface().get_height()
        screen_center_x = screen_width // 2
        screen_center_y = screen_height // 2
        
        # 计算从屏幕中心到鼠标的方向向量
        self.mouse_direction.x = mouse_x - screen_center_x
        self.mouse_direction.y = mouse_y - screen_center_y
        
        # 标准化方向向量
        if self.mouse_direction.length() > 0:
            self.mouse_direction = self.mouse_direction.normalize()
            
            # 更新朝向（基于鼠标X方向）
            self.facing_right = self.mouse_direction.x >= 0
        else:
            # 如果鼠标在屏幕中心，保持之前的朝向
            pass
    
    def _update_movement_direction(self):
        """更新移动方向和对应的角度"""
        # 更新方向向量（基于键盘输入）
        self.direction.x = float(self.moving['right']) - float(self.moving['left'])
        self.direction.y = float(self.moving['down']) - float(self.moving['up'])
        
        # 如果有移动输入，更新最后移动方向
        if self.direction.x != 0 or self.direction.y != 0:
            self.last_movement_direction.x = self.direction.x
            self.last_movement_direction.y = self.direction.y
            
            # 标准化方向向量（如果长度不为0）
            if self.direction.length() > 0:
                self.direction = self.direction.normalize()
                
            # 更新角色朝向：基于移动方向
            if self.direction.x > 0:
                self.facing_right = True
            elif self.direction.x < 0:
                self.facing_right = False
            
    def is_moving(self):
        """
        检查是否正在移动
        
        Returns:
            bool: 如果正在移动返回True，否则返回False
        """
        return self.direction.length() > 0
        
    def set_speed(self, speed):
        """
        设置移动速度
        
        Args:
            speed: 新的移动速度
        """
        self.speed = speed 
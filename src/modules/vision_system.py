import pygame
import math
import numpy as np
import time

class VisionSystem:
    def __init__(self, radius=300, angle=90, color=(255, 255, 200, 100), 
                 circle_radius=80, circle_color=(255, 255, 200, 100)):
        """
        视野系统初始化
        
        Args:
            radius (int): 视野半径（像素）
            angle (int): 视野角度（度），0-360
            color (tuple): 视野颜色 (R, G, B, A)
            circle_radius (int): 圆形光圈半径
            circle_color (tuple): 圆形光圈颜色 (R, G, B, A)
        """
        self.radius = radius
        self.angle = math.radians(angle)  # 转换为弧度
        self.color = color
        self.center_x = 0
        self.center_y = 0
        self.direction = 0  # 视野方向（弧度）
        
        # 圆形光圈参数
        self.circle_radius = circle_radius
        self.circle_color = circle_color
        
        # 视野遮罩
        self.vision_mask = None
        self.vision_surface = None
        
        # 性能优化：预计算一些值
        self.half_angle = self.angle / 2
        
        # 光线追踪相关
        self.walls = []  # 墙壁列表
        self.tile_size = 32  # 图块大小
        self.map_width = 0
        self.map_height = 0
        
        # 相机和屏幕相关
        self.camera_x = 0
        self.camera_y = 0
        self.screen_center_x = 0
        self.screen_center_y = 0
        
        # 性能优化：缓存和优化
        self._cache_vertices = None
        self._cache_center = None
        self._cache_direction = None
        self._cache_radius = None
        self._cache_angle = None
        self._last_update_time = 0
        self._update_interval = 0.033  # 30 FPS = 33ms，限制更新频率
        
        # 性能监控
        self._performance_stats = {
            'raycast_calls': 0,
            'raycast_time': 0,
            'render_time': 0,
            'cache_hits': 0,
            'cache_misses': 0
        }
        
        # 配置管理
        self.config = {
            "sector": {"radius": radius, "angle": math.degrees(self.angle), "color": color},
            "circle": {"radius": circle_radius, "color": circle_color},
            "enabled": True
        }
        
    def update(self, center_x, center_y, mouse_x, mouse_y):
        """
        更新视野位置和方向
        
        Args:
            center_x (int): 视野中心X坐标（通常是玩家位置）
            center_y (int): 视野中心Y坐标
            mouse_x (int): 鼠标X坐标
            mouse_y (int): 鼠标Y坐标
        """
        self.center_x = center_x
        self.center_y = center_y
        
        # 计算视野方向（指向鼠标）
        dx = mouse_x - center_x
        dy = mouse_y - center_y
        self.direction = math.atan2(dy, dx)
        
        # 确保方向在0-2π范围内
        if self.direction < 0:
            self.direction += 2 * math.pi
            
    def create_vision_mask(self, screen_width, screen_height):
        """
        创建视野遮罩（消除黑暗区域）- 高度优化版本
        
        Args:
            screen_width (int): 屏幕宽度
            screen_height (int): 屏幕高度
            
        Returns:
            pygame.Surface: 视野遮罩
        """
        # 性能优化：检查缓存是否有效
        current_time = time.time()
        if (self._cache_vertices and 
            self._cache_center == (self.center_x, self.center_y) and
            self._cache_direction == self.direction and
            self._cache_radius == self.radius and
            self._cache_angle == self.angle and
            current_time - self._last_update_time < self._update_interval):
            
            self._performance_stats['cache_hits'] += 1
            # 使用缓存的遮罩
            mask_surface = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
            mask_surface.fill((0, 0, 0, 0))
            
            # 绘制圆形光圈
            pygame.draw.circle(mask_surface, (255, 255, 255, 255), 
                             (self.center_x, self.center_y), self.circle_radius)
            
            # 绘制扇形视野
            if len(self._cache_vertices) >= 3:
                pygame.draw.polygon(mask_surface, (255, 255, 255, 255), self._cache_vertices)
            
            return mask_surface
        
        self._performance_stats['cache_misses'] += 1
        self._last_update_time = current_time
        
        # 创建新的遮罩表面
        mask_surface = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
        mask_surface.fill((0, 0, 0, 0))
        
        # 绘制圆形光圈（始终显示）
        pygame.draw.circle(mask_surface, (255, 255, 255, 255), 
                         (self.center_x, self.center_y), self.circle_radius)
        
        # 计算视野顶点
        if self.walls:
            vertices = self._calculate_vision_vertices_with_raycast(screen_width, screen_height)
        else:
            vertices = self._calculate_vision_vertices(screen_width, screen_height)
        
        # 缓存顶点
        self._cache_vertices = vertices
        self._cache_center = (self.center_x, self.center_y)
        self._cache_direction = self.direction
        self._cache_radius = self.radius
        self._cache_angle = self.angle
        
        # 绘制扇形视野
        if len(vertices) >= 3:
            pygame.draw.polygon(mask_surface, (255, 255, 255, 255), vertices)
            
        return mask_surface
        

    
    def _calculate_vision_vertices(self, screen_width, screen_height):
        """
        计算视野扇形的顶点
        
        Returns:
            list: 顶点坐标列表 [(x1, y1), (x2, y2), ...]
        """
        vertices = []
        
        # 添加中心点
        vertices.append((self.center_x, self.center_y))
        
        # 计算扇形的边界点
        start_angle = self.direction - self.half_angle
        end_angle = self.direction + self.half_angle
        
        # 生成扇形边缘的点
        num_points = max(10, int(self.radius / 20))  # 根据半径调整点的数量
        angles = np.linspace(start_angle, end_angle, num_points)
        
        for angle in angles:
            x = self.center_x + self.radius * math.cos(angle)
            y = self.center_y + self.radius * math.sin(angle)
            
            # 确保点在屏幕范围内
            x = max(0, min(x, screen_width))
            y = max(0, min(y, screen_height))
            
            vertices.append((x, y))
            
        return vertices
        
    def _draw_circle_with_raycast(self, surface, screen_width, screen_height):
        """
        绘制带光线追踪的圆形区域（高度优化版本）
        
        Args:
            surface (pygame.Surface): 绘制表面
            screen_width (int): 屏幕宽度
            screen_height (int): 屏幕高度
        """
        if not self.walls:
            # 如果没有墙壁，绘制完整圆形
            pygame.draw.circle(surface, (255, 255, 255, 255), 
                             (self.center_x, self.center_y), self.circle_radius)
            return
            
        # 计算圆形边界的所有顶点（按照扇形的逻辑）
        vertices = []
        
        # 添加中心点
        vertices.append((self.center_x, self.center_y))
        
        # 性能优化：减少圆形边界的采样点
        num_points = max(16, int(self.circle_radius / 8))  # 大幅减少采样点
        angles = np.linspace(0, 2 * math.pi, num_points)
        
        for angle in angles:
            # 计算理论上的终点
            end_x = self.center_x + self.circle_radius * math.cos(angle)
            end_y = self.center_y + self.circle_radius * math.sin(angle)
            
            # 进行光线追踪
            blocked, hit_point = self.ray_cast(self.center_x, self.center_y, end_x, end_y)
            
            if blocked:
                # 如果被阻挡，使用阻挡点
                x, y = hit_point
            else:
                # 如果没有被阻挡，使用理论终点
                x, y = end_x, end_y
            
            # 确保点在屏幕范围内
            x = max(0, min(x, screen_width))
            y = max(0, min(y, screen_height))
            
            vertices.append((x, y))
        
        # 绘制多边形
        if len(vertices) >= 3:
            pygame.draw.polygon(surface, (255, 255, 255, 255), vertices)
        
    def _calculate_vision_vertices_with_raycast(self, screen_width, screen_height):
        """
        计算带光线追踪的视野扇形顶点（高度优化版本）
        
        Returns:
            list: 顶点坐标列表 [(x1, y1), (x2, y2), ...]
        """
        vertices = []
        
        # 添加中心点
        vertices.append((self.center_x, self.center_y))
        
        # 计算扇形的边界点
        start_angle = self.direction - self.half_angle
        end_angle = self.direction + self.half_angle
        
        # 性能优化：大幅减少光线数量
        # 根据半径动态调整，但设置更保守的上限
        base_points = max(4, min(12, int(self.radius / 100)))  # 减少光线数量
        num_points = base_points
        
        # 使用更高效的角度生成
        angles = []
        for i in range(num_points):
            angle = start_angle + (end_angle - start_angle) * i / (num_points - 1)
            angles.append(angle)
        
        # 批量处理光线追踪
        start_time = time.time()
        for angle in angles:
            # 计算理论上的终点
            end_x = self.center_x + self.radius * math.cos(angle)
            end_y = self.center_y + self.radius * math.sin(angle)
            
            # 进行光线追踪
            blocked, hit_point = self.ray_cast(self.center_x, self.center_y, end_x, end_y)
            
            if blocked:
                # 如果被阻挡，使用阻挡点
                x, y = hit_point
            else:
                # 如果没有被阻挡，使用理论终点
                x, y = end_x, end_y
            
            # 确保点在屏幕范围内
            x = max(0, min(x, screen_width))
            y = max(0, min(y, screen_height))
            
            vertices.append((x, y))
        
        self._performance_stats['raycast_time'] += time.time() - start_time
        self._performance_stats['raycast_calls'] += len(angles)
            
        return vertices
    
    def render(self, screen, dark_overlay=None):
        """
        渲染视野系统（优化版本）
        
        Args:
            screen (pygame.Surface): 游戏屏幕
            dark_overlay (pygame.Surface): 黑暗遮罩（可选）
        """
        start_time = time.time()
        screen_width, screen_height = screen.get_size()
        
        # 创建视野遮罩
        vision_mask = self.create_vision_mask(screen_width, screen_height)
        
        if dark_overlay:
            # 如果有黑暗遮罩，创建复合效果
            # 复制黑暗遮罩
            final_overlay = dark_overlay.copy()
            
            # 在视野区域清除黑暗（使用减法混合模式）
            final_overlay.blit(vision_mask, (0, 0), special_flags=pygame.BLEND_RGBA_SUB)
            
            # 渲染最终遮罩
            screen.blit(final_overlay, (0, 0))
        else:
            # 直接渲染视野遮罩
            screen.blit(vision_mask, (0, 0))
        
        self._performance_stats['render_time'] += time.time() - start_time
    
    def is_in_vision(self, x, y):
        """
        检查点是否在视野范围内（包括圆形和扇形）
        
        Args:
            x (int): 点的X坐标
            y (int): 点的Y坐标
            
        Returns:
            bool: 是否在视野内
        """
        # 首先检查是否在圆形光圈内
        dx = x - self.center_x
        dy = y - self.center_y
        distance = math.sqrt(dx * dx + dy * dy)
        
        # 如果在圆形光圈内，直接返回True
        if distance <= self.circle_radius:
            return True
        
        # 检查是否在扇形视野内
        if distance > self.radius:
            return False
        
        # 计算点到中心的角度
        angle = math.atan2(dy, dx)
        if angle < 0:
            angle += 2 * math.pi
            
        # 计算角度差
        angle_diff = abs(angle - self.direction)
        if angle_diff > math.pi:
            angle_diff = 2 * math.pi - angle_diff
            
        # 检查是否在视野角度范围内
        return angle_diff <= self.half_angle
    
    def set_radius(self, radius):
        """设置视野半径"""
        self.radius = radius
        
    def set_angle(self, angle):
        """设置视野角度（度）"""
        self.angle = math.radians(angle)
        self.half_angle = self.angle / 2
        
    def set_color(self, color):
        """设置视野颜色"""
        self.color = color
        self.config["sector"]["color"] = color
        
    def set_circle_radius(self, radius):
        """设置圆形光圈半径"""
        self.circle_radius = radius
        self.config["circle"]["radius"] = radius
        
    def set_circle_color(self, color):
        """设置圆形光圈颜色"""
        self.circle_color = color
        self.config["circle"]["color"] = color
        
    def set_radius(self, radius):
        """设置视野半径"""
        self.radius = radius
        self.config["sector"]["radius"] = radius
        
    def set_angle(self, angle):
        """设置视野角度（度）"""
        self.angle = math.radians(angle)
        self.half_angle = self.angle / 2
        self.config["sector"]["angle"] = angle
        
    def toggle_enabled(self):
        """切换启用状态"""
        self.config["enabled"] = not self.config["enabled"]
        return self.config["enabled"]
        
    def is_enabled(self):
        """检查是否启用"""
        return self.config["enabled"]
        
    def get_config(self):
        """获取当前配置"""
        return self.config.copy()
        
    def apply_config(self, config):
        """应用配置"""
        if "sector" in config:
            sector = config["sector"]
            if "radius" in sector:
                self.set_radius(sector["radius"])
            if "angle" in sector:
                self.set_angle(sector["angle"])
            if "color" in sector:
                self.set_color(sector["color"])
                
        if "circle" in config:
            circle = config["circle"]
            if "radius" in circle:
                self.set_circle_radius(circle["radius"])
            if "color" in circle:
                self.set_circle_color(circle["color"])
                
        if "enabled" in config:
            self.config["enabled"] = config["enabled"]
    
    def get_performance_stats(self):
        """获取性能统计信息"""
        return self._performance_stats.copy()
    
    def reset_performance_stats(self):
        """重置性能统计"""
        self._performance_stats = {
            'raycast_calls': 0,
            'raycast_time': 0,
            'render_time': 0,
            'cache_hits': 0,
            'cache_misses': 0
        }
    
    def clear_cache(self):
        """清除缓存"""
        self._cache_vertices = None
        self._cache_center = None
        self._cache_direction = None
        self._cache_radius = None
        self._cache_angle = None
            
    def set_walls(self, walls, tile_size=32, map_width=0, map_height=0):
        """设置墙壁数据
        
        Args:
            walls (list): 墙壁矩形列表（世界坐标）
            tile_size (int): 图块大小
            map_width (int): 地图宽度
            map_height (int): 地图高度
        """
        self.walls = walls
        self.tile_size = tile_size
        self.map_width = map_width
        self.map_height = map_height
        
    def set_camera_and_screen(self, camera_x, camera_y, screen_center_x, screen_center_y):
        """设置相机位置和屏幕中心点
        
        Args:
            camera_x (int): 相机X坐标（世界坐标）
            camera_y (int): 相机Y坐标（世界坐标）
            screen_center_x (int): 屏幕中心X坐标
            screen_center_y (int): 屏幕中心Y坐标
        """
        self.camera_x = camera_x
        self.camera_y = camera_y
        self.screen_center_x = screen_center_x
        self.screen_center_y = screen_center_y
        
    def ray_cast(self, start_x, start_y, end_x, end_y):
        """光线追踪（高度优化版本）
        
        Args:
            start_x, start_y: 起始点坐标（屏幕坐标）
            end_x, end_y: 终点坐标（屏幕坐标）
            
        Returns:
            tuple: (是否被阻挡, 阻挡点坐标)
        """
        if not self.walls:
            return False, (end_x, end_y)
            
        # 计算光线方向
        dx = end_x - start_x
        dy = end_y - start_y
        distance = math.sqrt(dx * dx + dy * dy)
        
        if distance == 0:
            return False, (end_x, end_y)
            
        # 归一化方向向量
        dx /= distance
        dy /= distance
        
        # 性能优化：增加步长以减少计算量
        # 距离越远，步长越大，但不超过图块大小
        step_size = min(max(8, self.tile_size // 4), 32)  # 增加步长
        current_x = start_x
        current_y = start_y
        
        # 预计算世界坐标转换
        camera_offset_x = self.camera_x - self.screen_center_x
        camera_offset_y = self.camera_y - self.screen_center_y
        
        # 性能优化：使用更高效的碰撞检测
        # 只检查在视野范围内的墙壁
        vision_rect = pygame.Rect(
            self.center_x - self.radius, 
            self.center_y - self.radius,
            self.radius * 2, 
            self.radius * 2
        )
        
        # 筛选可能碰撞的墙壁
        relevant_walls = []
        for wall in self.walls:
            # 将墙壁转换到屏幕坐标
            screen_wall = pygame.Rect(
                wall.x - camera_offset_x,
                wall.y - camera_offset_y,
                wall.width,
                wall.height
            )
            if screen_wall.colliderect(vision_rect):
                relevant_walls.append(screen_wall)
        
        # 如果没有相关墙壁，直接返回
        if not relevant_walls:
            return False, (end_x, end_y)
        
        # 逐步检查（减少检查频率）
        check_interval = 2  # 每2步检查一次碰撞
        step_count = 0
        
        while True:
            # 移动到下一个检查点
            current_x += dx * step_size
            current_y += dy * step_size
            step_count += 1
            
            # 检查是否超出目标距离
            check_distance = math.sqrt((current_x - start_x) ** 2 + (current_y - start_y) ** 2)
            if check_distance >= distance:
                return False, (end_x, end_y)
                
            # 减少碰撞检测频率
            if step_count % check_interval == 0:
                # 检查是否与墙壁碰撞（使用屏幕坐标）
                for wall in relevant_walls:
                    if wall.collidepoint(current_x, current_y):
                        return True, (current_x, current_y)
                        
                # 检查是否超出地图边界（使用世界坐标）
                world_x = current_x + camera_offset_x
                world_y = current_y + camera_offset_y
                
                if (world_x < 0 or world_x >= self.map_width or 
                    world_y < 0 or world_y >= self.map_height):
                    return True, (current_x, current_y)


class DarkOverlay:
    """黑暗遮罩类，用于创建全局黑暗效果"""
    
    def __init__(self, screen_width, screen_height, darkness_alpha=200):
        """
        初始化黑暗遮罩
        
        Args:
            screen_width (int): 屏幕宽度
            screen_height (int): 屏幕高度
            darkness_alpha (int): 黑暗程度 (0-255)
        """
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.darkness_alpha = darkness_alpha
        self.overlay = None
        self._create_overlay()
        
    def _create_overlay(self):
        """创建黑暗遮罩"""
        self.overlay = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        self.overlay.fill((0, 0, 0, self.darkness_alpha))
        
    def get_overlay(self):
        """获取黑暗遮罩"""
        return self.overlay
        
    def set_darkness(self, alpha):
        """设置黑暗程度"""
        self.darkness_alpha = max(0, min(255, alpha))
        self._create_overlay()
        
    def get_config(self):
        """获取当前配置"""
        return {
            "darkness_alpha": self.darkness_alpha,
            "screen_width": self.screen_width,
            "screen_height": self.screen_height
        }
        
    def apply_config(self, config):
        """应用配置"""
        if "darkness_alpha" in config:
            self.set_darkness(config["darkness_alpha"]) 
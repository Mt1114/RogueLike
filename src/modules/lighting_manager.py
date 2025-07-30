import pygame
import numpy as np
import math
from .Pygame_Lights import LIGHT, global_light, pixel_shader


class LightingManager:
    """光照管理器，集成Pygame_Lights库"""

    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height

        # 光照设置
        self.light_intensity = 60  # 降低光照强度，减少条纹
        self.light_color = (255, 255, 255)  # 光照颜色

        # 玩家光照（圆形）
        self.player_light = None
        self.player_light_size = 150  # 增大玩家圆形光照大小
        self.player_light_radius = 75  # 玩家光照半径

        # 鼠标光照（扇形）
        self.mouse_light = None
        self.mouse_light_size = 250  # 调整鼠标扇形光照大小
        self.mouse_light_angle = 60  # 扇形角度
        self.mouse_light_radius = 125  # 鼠标光照半径

        # 墙壁碰撞数据
        self.walls = []
        self.tile_size = 32

        # 全局黑暗
        self.global_darkness = None
        self.darkness_intensity = 100  # 调整黑暗强度

        # 初始化光照
        self._init_lights()

    def _init_lights(self):
        """初始化光照"""
        # 创建玩家圆形光照
        player_shader = pixel_shader(
            self.player_light_size,
            self.light_color,
            self.light_intensity,
            point=False,  # 圆形光照
        )
        self.player_light = LIGHT(self.player_light_size, player_shader)

        # 创建鼠标扇形光照
        mouse_shader = pixel_shader(
            self.mouse_light_size,
            self.light_color,
            self.light_intensity,
            point=True,  # 扇形光照
            angle=0,
            angle_width=self.mouse_light_angle,
        )
        self.mouse_light = LIGHT(self.mouse_light_size, mouse_shader)

        # 创建全局黑暗
        self.global_darkness = global_light(
            (self.screen_width, self.screen_height), self.darkness_intensity
        )

    def set_walls(self, walls, tile_size=32):
        """设置墙壁数据"""
        self.walls = walls
        self.tile_size = tile_size

    def update_mouse_light_angle(self, mouse_x, mouse_y, player_x, player_y):
        """更新鼠标光照角度"""
        if mouse_x == player_x and mouse_y == player_y:
            return

        # 计算鼠标相对于玩家的角度
        dx = mouse_x - player_x
        dy = mouse_y - player_y
        angle = np.degrees(np.arctan2(dy, dx))

        # 调整角度，使其正确指向鼠标方向
        # Pygame_Lights中0度指向右边，90度指向下边
        # 而np.arctan2中0度指向右边，90度指向上边
        # 所以需要将Y轴翻转：angle = -angle
        angle = -angle

        # 更新鼠标光照的角度
        mouse_shader = pixel_shader(
            self.mouse_light_size,
            self.light_color,
            self.light_intensity,
            point=True,
            angle=angle,
            angle_width=self.mouse_light_angle,
        )
        self.mouse_light = LIGHT(self.mouse_light_size, mouse_shader)

    def render(
        self, screen, player_x, player_y, mouse_x, mouse_y, camera_x=0, camera_y=0
    ):
        """渲染光照效果"""
        # 玩家始终在屏幕中心
        screen_player_x = screen.get_width() // 2
        screen_player_y = screen.get_height() // 2

        # 鼠标坐标已经是屏幕坐标，不需要转换
        screen_mouse_x = mouse_x
        screen_mouse_y = mouse_y

        # 计算鼠标相对于屏幕中心玩家的角度
        dx = screen_mouse_x - screen_player_x
        dy = screen_mouse_y - screen_player_y
        angle = np.degrees(np.arctan2(dy, dx))

        # 创建墙壁矩形列表（用于光照库）
        wall_rects = []
        for wall in self.walls:
            # wall 是 pygame.Rect 对象，包含 x, y, width, height
            # 转换墙壁从世界坐标到屏幕坐标
            screen_wall_x = wall.x - camera_x + screen_player_x
            screen_wall_y = wall.y - camera_y + screen_player_y
            wall_rects.append(
                pygame.Rect(screen_wall_x, screen_wall_y, wall.width, wall.height)
            )

        # 更新鼠标光照角度（使用屏幕坐标）
        self.update_mouse_light_angle(
            screen_mouse_x, screen_mouse_y, screen_player_x, screen_player_y
        )

        # 渲染全局黑暗
        screen.blit(self.global_darkness, (0, 0))

        # 渲染玩家光照（在屏幕中心）
        if self.player_light:
            self.player_light.main(wall_rects, screen, screen_player_x, screen_player_y)

        # 渲染鼠标光照（从玩家位置发出，指向鼠标方向）
        if self.mouse_light:
            self.mouse_light.main(wall_rects, screen, screen_player_x, screen_player_y)

    def set_light_config(
        self,
        light_intensity=None,
        light_color=None,
        player_light_size=None,
        player_radius=None,
        mouse_light_size=None,
        mouse_angle=None,
        mouse_radius=None,
        darkness_intensity=None,
    ):
        """设置光照配置"""
        if light_intensity is not None:
            self.light_intensity = light_intensity
        if light_color is not None:
            self.light_color = light_color
        if player_light_size is not None:
            self.player_light_size = player_light_size
        if player_radius is not None:
            self.player_light_radius = player_radius
        if mouse_light_size is not None:
            self.mouse_light_size = mouse_light_size
        if mouse_angle is not None:
            self.mouse_light_angle = mouse_angle
        if mouse_radius is not None:
            self.mouse_light_radius = mouse_radius
        if darkness_intensity is not None:
            self.darkness_intensity = darkness_intensity

        # 重新初始化光照
        self._init_lights()
    
    def is_enabled(self):
        """检查光照系统是否启用"""
        return True  # 简化版本，总是启用
    
    def is_in_light(self, x, y):
        """检查指定点是否在光照范围内"""
        # 计算点到玩家光照中心的距离
        player_screen_x = self.screen_width // 2
        player_screen_y = self.screen_height // 2
        
        dx = x - player_screen_x
        dy = y - player_screen_y
        distance = math.sqrt(dx*dx + dy*dy)
        
        # 如果在玩家光照半径内，返回True
        return distance <= self.player_light_radius

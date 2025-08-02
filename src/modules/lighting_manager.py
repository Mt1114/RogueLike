import pygame
import math
from .vision_system import VisionSystem, DarkOverlay
from .vision_config import get_vision_config, get_vision_presets, apply_preset, validate_config

class LightingManager:
    """光照管理器，使用VisionSystem替代Pygame_Lights库"""

    def __init__(self, screen_width, screen_height, preset_name="default"):
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        # 加载配置
        self.config = get_vision_config()
        self.presets = get_vision_presets()
        
        # 应用预设配置
        if preset_name in self.presets:
            self.apply_preset(preset_name)
        else:
            # 使用默认配置
            self.apply_preset("default")

        # 创建视野系统（用于光照效果）
        self.vision_system = VisionSystem(
            radius=self.config["sector"]["radius"],  # 视野半径
            angle=self.config["sector"]["angle"],    # 视野角度（度）
            color=self.config["sector"]["color"],    # 视野颜色
            circle_radius=self.config["circle"]["radius"],  # 圆形光圈半径
            circle_color=self.config["circle"]["color"],  # 圆形光圈颜色
            ray_count=self.config["sector"].get("ray_count", 24)  # 光线数量
        )
        
        # 创建黑暗遮罩
        self.dark_overlay = DarkOverlay(
            screen_width, 
            screen_height, 
            darkness_alpha=self.config["darkness"]["alpha"]
        )
        
        # 墙壁碰撞数据
        self.walls = []
        self.tile_size = 32
        
        # 相机和屏幕相关
        self.camera_x = 0
        self.camera_y = 0
        self.screen_center_x = screen_width // 2
        self.screen_center_y = screen_height // 2
        
        # 当前预设名称
        self.current_preset = preset_name

    def apply_preset(self, preset_name):
        """应用预设配置
        
        Args:
            preset_name (str): 预设名称
        """
        if preset_name in self.presets:
            # 应用预设配置
            preset_config = apply_preset(preset_name)
            self.config = validate_config(preset_config)
            self.current_preset = preset_name
            
            # 如果视野系统已创建，更新其配置
            if hasattr(self, 'vision_system'):
                self.vision_system.set_radius(self.config["sector"]["radius"])
                self.vision_system.set_angle(self.config["sector"]["angle"])
                self.vision_system.set_color(self.config["sector"]["color"])
                self.vision_system.set_circle_radius(self.config["circle"]["radius"])
                self.vision_system.set_circle_color(self.config["circle"]["color"])
                # 更新光线数量（需要重新创建视野系统）
                ray_count = self.config["sector"].get("ray_count", 24)
                if hasattr(self.vision_system, 'ray_count') and self.vision_system.ray_count != ray_count:
                    # 重新创建视野系统以应用新的光线数量
                    self.vision_system = VisionSystem(
                        radius=self.config["sector"]["radius"],
                        angle=self.config["sector"]["angle"],
                        color=self.config["sector"]["color"],
                        circle_radius=self.config["circle"]["radius"],
                        circle_color=self.config["circle"]["color"],
                        ray_count=ray_count
                    )
            
            # 如果黑暗遮罩已创建，更新其配置
            if hasattr(self, 'dark_overlay'):
                self.dark_overlay.set_darkness(self.config["darkness"]["alpha"])
                
            print(f"已应用光照预设: {self.presets[preset_name]['name']}")
        else:
            print(f"预设 '{preset_name}' 不存在")

    def get_available_presets(self):
        """获取可用的预设列表"""
        return list(self.presets.keys())

    def get_current_preset(self):
        """获取当前预设名称"""
        return self.current_preset

    def get_preset_info(self, preset_name):
        """获取预设信息"""
        if preset_name in self.presets:
            return self.presets[preset_name]
        return None

    def set_walls(self, walls, tile_size=32):
        """设置墙壁数据"""
        self.walls = walls
        self.tile_size = tile_size
        
        # 更新视野系统的墙壁数据
        # 从墙壁数据中估算地图尺寸
        map_width = 0
        map_height = 0
        if walls:
            max_x = max(wall.x + wall.width for wall in walls)
            max_y = max(wall.y + wall.height for wall in walls)
            map_width = max_x
            map_height = max_y
        
        self.vision_system.set_walls(walls, tile_size, map_width, map_height)

    def update_mouse_light_angle(self, mouse_x, mouse_y, player_x, player_y):
        """更新鼠标光照角度（兼容性方法）"""
        # 这个方法在VisionSystem中不需要，因为update方法会自动处理
        pass

    def render(self, screen, player_x, player_y, mouse_x, mouse_y, camera_x=0, camera_y=0, 
               additional_lights=None):
        """
        渲染光照效果
        
        Args:
            screen: 屏幕表面
            player_x, player_y: 主光源位置（忍者蛙）
            mouse_x, mouse_y: 鼠标位置（用于视野方向）
            camera_x, camera_y: 相机位置
            additional_lights: 额外光源列表，每个元素为 (x, y, intensity, radius)
        """
        # 更新相机和屏幕信息
        self.camera_x = camera_x
        self.camera_y = camera_y
        self.screen_center_x = screen.get_width() // 2
        self.screen_center_y = screen.get_height() // 2
        
        # 更新视野系统的相机和屏幕信息
        self.vision_system.set_camera_and_screen(
            camera_x, camera_y, self.screen_center_x, self.screen_center_y
        )
        
        # 使用传入的玩家位置，而不是屏幕中心
        screen_player_x = player_x
        screen_player_y = player_y
        
        # 更新视野系统
        self.vision_system.update(screen_player_x, screen_player_y, mouse_x, mouse_y)
        
        # 重新创建黑暗遮罩，确保每次渲染都是干净的
        self.dark_overlay._create_overlay()
        
        # 创建最终的黑暗遮罩
        final_overlay = self.dark_overlay.get_overlay().copy()
        
        # 渲染主视野系统（忍者蛙的光照）到最终遮罩
        self._render_main_vision(final_overlay)
        
        # 渲染额外光源（神秘剑士的光源）到最终遮罩
        if additional_lights:
            self._render_additional_lights(final_overlay, additional_lights)
        
        # 将最终遮罩渲染到屏幕
        screen.blit(final_overlay, (0, 0))
        
    def render_with_independent_direction(self, screen, player_x, player_y, absolute_direction, camera_x=0, camera_y=0):
        """
        渲染光照效果（使用独立方向）
        
        Args:
            screen: 屏幕表面
            player_x: 玩家屏幕X坐标
            player_y: 玩家屏幕Y坐标
            absolute_direction: 绝对方向角度（弧度），独立于角色位置
            camera_x: 相机X偏移
            camera_y: 相机Y偏移
        """
        # 更新相机和屏幕信息
        self.camera_x = camera_x
        self.camera_y = camera_y
        self.screen_center_x = screen.get_width() // 2
        self.screen_center_y = screen.get_height() // 2
        
        # 更新视野系统的相机和屏幕信息
        self.vision_system.set_camera_and_screen(
            camera_x, camera_y, self.screen_center_x, self.screen_center_y
        )
        
        # 使用传入的玩家位置，而不是屏幕中心
        screen_player_x = player_x
        screen_player_y = player_y
        
        # 更新视野系统（使用独立方向）
        self.vision_system.update_with_independent_direction(screen_player_x, screen_player_y, absolute_direction)
        
        # 渲染视野系统（这会创建光照效果）
        self.vision_system.render(screen, self.dark_overlay.get_overlay())

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
        """设置光照配置（兼容性方法）"""
        # 转换参数到VisionSystem的配置
        if player_radius is not None:
            self.vision_system.set_circle_radius(player_radius)
            self.config["circle"]["radius"] = player_radius
            
        if mouse_radius is not None:
            self.vision_system.set_radius(mouse_radius)
            self.config["sector"]["radius"] = mouse_radius
            
        if mouse_angle is not None:
            self.vision_system.set_angle(mouse_angle)
            self.config["sector"]["angle"] = mouse_angle
            
        if light_color is not None:
            self.vision_system.set_color(light_color)
            self.vision_system.set_circle_color(light_color)
            self.config["sector"]["color"] = light_color
            self.config["circle"]["color"] = light_color
            
        if darkness_intensity is not None:
            # 将intensity转换为alpha值（0-255）
            alpha = max(0, min(255, 255 - darkness_intensity))
            self.dark_overlay.set_darkness(alpha)
            self.config["darkness"]["alpha"] = alpha

    def set_preset(self, preset_name):
        """设置预设（新方法）"""
        self.apply_preset(preset_name)

    def cycle_preset(self):
        """循环切换预设"""
        presets = self.get_available_presets()
        if presets:
            current_index = presets.index(self.current_preset)
            next_index = (current_index + 1) % len(presets)
            next_preset = presets[next_index]
            self.apply_preset(next_preset)

    def get_performance_stats(self):
        """获取性能统计信息"""
        if hasattr(self.vision_system, 'get_performance_stats'):
            return self.vision_system.get_performance_stats()
        return {}

    def is_enabled(self):
        """检查光照系统是否启用"""
        return self.vision_system.is_enabled()
    
    def is_in_light(self, x, y):
        """检查指定点是否在光照范围内"""
        return self.vision_system.is_in_vision(x, y)
        
    def _render_main_vision(self, final_overlay):
        """
        渲染主视野系统（忍者蛙的光照）到最终遮罩
        
        Args:
            final_overlay: 最终的黑暗遮罩
        """
        # 创建视野遮罩
        vision_mask = self.vision_system.create_vision_mask(
            self.screen_width, self.screen_height
        )
        
        # 在视野区域清除黑暗（使用减法混合模式）
        final_overlay.blit(vision_mask, (0, 0), special_flags=pygame.BLEND_RGBA_SUB)
        
    def _render_additional_lights(self, final_overlay, additional_lights):
        """
        渲染额外光源到最终遮罩
        
        Args:
            final_overlay: 最终的黑暗遮罩
            additional_lights: 额外光源列表，每个元素为 (x, y, intensity, radius)
        """
        if not additional_lights:
            return
            
        for light_x, light_y, intensity, radius in additional_lights:
            # 创建光源遮罩（用于清除黑暗）
            light_mask = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
            
            # 绘制圆形光源遮罩（白色，用于清除黑暗）
            # 使用统一的透明度，不搞渐进效果
            alpha = int(255 * intensity)
            if alpha > 0:
                # 绘制圆形，颜色为白色，统一透明度
                color = (255, 255, 255, alpha)
                pygame.draw.circle(light_mask, color, 
                                 (int(light_x), int(light_y)), int(radius))
            
            # 将光源遮罩应用到最终遮罩上，清除光源区域的黑暗
            # 使用BLEND_RGBA_SUB混合模式，让光源区域变得透明
            final_overlay.blit(light_mask, (0, 0), special_flags=pygame.BLEND_RGBA_SUB)

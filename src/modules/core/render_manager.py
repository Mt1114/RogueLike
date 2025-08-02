"""
渲染管理器
负责管理渲染层和渲染顺序，提供统一的渲染接口
"""

from typing import List, Dict, Callable, Optional, Tuple
import pygame


class RenderLayer:
    """渲染层类"""
    
    def __init__(self, name: str, priority: int = 0):
        self.name = name
        self.priority = priority  # 优先级，数字越小越先渲染
        self.renderables: List[Callable] = []
        
    def add_renderable(self, render_func: Callable):
        """添加可渲染对象"""
        self.renderables.append(render_func)
        
    def remove_renderable(self, render_func: Callable):
        """移除可渲染对象"""
        if render_func in self.renderables:
            self.renderables.remove(render_func)
            
    def render(self, screen: pygame.Surface, camera_x: float = 0, camera_y: float = 0):
        """渲染该层的所有对象"""
        for render_func in self.renderables:
            try:
                render_func(screen, camera_x, camera_y)
            except Exception as e:
                print(f"渲染错误 in layer {self.name}: {e}")
                
    def clear(self):
        """清空该层的所有渲染对象"""
        self.renderables.clear()


class RenderManager:
    """渲染管理器"""
    
    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self.layers: Dict[str, RenderLayer] = {}
        self.layer_order: List[str] = []
        
        # 相机设置
        self.camera_x = 0.0
        self.camera_y = 0.0
        
        # 渲染设置
        self.clear_color = (0, 0, 0)
        self.enable_grid = False
        self.grid_size = 50
        self.grid_color = (50, 50, 50)
        
        # 分屏设置
        self.split_screen = False
        self.screen1_rect = None
        self.screen2_rect = None
        self.camera1_x = 0.0
        self.camera1_y = 0.0
        self.camera2_x = 0.0
        self.camera2_y = 0.0
        
        # 初始化默认层
        self._setup_default_layers()
        
    def _setup_default_layers(self):
        """设置默认渲染层"""
        self.add_layer("background", 0)      # 背景层
        self.add_layer("map", 1)             # 地图层
        self.add_layer("items", 2)           # 物品层
        self.add_layer("enemies", 3)         # 敌怪层
        self.add_layer("players", 4)         # 玩家层
        self.add_layer("effects", 5)         # 特效层
        self.add_layer("lighting", 6)        # 光照层
        self.add_layer("ui", 7)              # UI层
        self.add_layer("overlay", 8)         # 覆盖层
        
    def add_layer(self, name: str, priority: int = 0):
        """添加渲染层"""
        self.layers[name] = RenderLayer(name, priority)
        self._update_layer_order()
        
    def remove_layer(self, name: str):
        """移除渲染层"""
        if name in self.layers:
            del self.layers[name]
            if name in self.layer_order:
                self.layer_order.remove(name)
                
    def get_layer(self, name: str) -> Optional[RenderLayer]:
        """获取渲染层"""
        return self.layers.get(name)
        
    def add_to_layer(self, layer_name: str, render_func: Callable):
        """添加渲染函数到指定层"""
        layer = self.get_layer(layer_name)
        if layer:
            layer.add_renderable(render_func)
        else:
            print(f"渲染层 {layer_name} 不存在")
            
    def remove_from_layer(self, layer_name: str, render_func: Callable):
        """从指定层移除渲染函数"""
        layer = self.get_layer(layer_name)
        if layer:
            layer.remove_renderable(render_func)
            
    def _update_layer_order(self):
        """更新层的渲染顺序"""
        self.layer_order = sorted(
            self.layers.keys(),
            key=lambda name: self.layers[name].priority
        )
        
    def set_camera(self, x: float, y: float):
        """设置相机位置"""
        self.camera_x = x
        self.camera_y = y
        
    def set_split_screen(self, enabled: bool, screen1_rect: pygame.Rect = None, screen2_rect: pygame.Rect = None):
        """设置分屏模式"""
        self.split_screen = enabled
        if enabled and screen1_rect and screen2_rect:
            self.screen1_rect = screen1_rect
            self.screen2_rect = screen2_rect
            
    def set_camera1(self, x: float, y: float):
        """设置相机1位置（分屏模式）"""
        self.camera1_x = x
        self.camera1_y = y
        
    def set_camera2(self, x: float, y: float):
        """设置相机2位置（分屏模式）"""
        self.camera2_x = x
        self.camera2_y = y
        
    def render(self):
        """执行渲染"""
        if self.split_screen:
            self._render_split_screen()
        else:
            self._render_single_screen()
            
    def _render_single_screen(self):
        """渲染单屏模式"""
        # 清屏
        self.screen.fill(self.clear_color)
        
        # 按顺序渲染各层
        for layer_name in self.layer_order:
            layer = self.layers[layer_name]
            layer.render(self.screen, self.camera_x, self.camera_y)
            
        # 渲染网格（调试用）
        if self.enable_grid:
            self._render_grid(self.screen, self.camera_x, self.camera_y)
            
    def _render_split_screen(self):
        """渲染分屏模式"""
        if not self.screen1_rect or not self.screen2_rect:
            return
            
        # 清屏
        self.screen.fill(self.clear_color)
        
        # 渲染屏幕1
        sub_surface1 = self.screen.subsurface(self.screen1_rect)
        sub_surface1.fill(self.clear_color)
        
        for layer_name in self.layer_order:
            layer = self.layers[layer_name]
            layer.render(sub_surface1, self.camera1_x, self.camera1_y)
            
        if self.enable_grid:
            self._render_grid(sub_surface1, self.camera1_x, self.camera1_y)
            
        # 渲染屏幕2
        sub_surface2 = self.screen.subsurface(self.screen2_rect)
        sub_surface2.fill(self.clear_color)
        
        for layer_name in self.layer_order:
            layer = self.layers[layer_name]
            layer.render(sub_surface2, self.camera2_x, self.camera2_y)
            
        if self.enable_grid:
            self._render_grid(sub_surface2, self.camera2_x, self.camera2_y)
            
    def _render_grid(self, surface: pygame.Surface, camera_x: float, camera_y: float):
        """渲染网格"""
        width, height = surface.get_size()
        
        # 计算网格偏移
        offset_x = int(camera_x) % self.grid_size
        offset_y = int(camera_y) % self.grid_size
        
        # 绘制垂直线
        for x in range(offset_x, width, self.grid_size):
            pygame.draw.line(surface, self.grid_color, (x, 0), (x, height))
            
        # 绘制水平线
        for y in range(offset_y, height, self.grid_size):
            pygame.draw.line(surface, self.grid_color, (0, y), (width, y))
            
    def clear_all_layers(self):
        """清空所有渲染层"""
        for layer in self.layers.values():
            layer.clear()
            
    def get_world_to_screen(self, world_x: float, world_y: float) -> Tuple[int, int]:
        """世界坐标转屏幕坐标"""
        screen_x = int(world_x - self.camera_x)
        screen_y = int(world_y - self.camera_y)
        return screen_x, screen_y
        
    def get_screen_to_world(self, screen_x: int, screen_y: int) -> Tuple[float, float]:
        """屏幕坐标转世界坐标"""
        world_x = screen_x + self.camera_x
        world_y = screen_y + self.camera_y
        return world_x, world_y 
"""
基础实体类
所有游戏对象的基础类，提供位置、渲染、更新等基础功能
"""

from abc import ABC, abstractmethod
from typing import Optional, Tuple, Dict, Any
import pygame


class Entity(ABC):
    """基础实体类"""
    
    def __init__(self, x: float, y: float, width: int = 32, height: int = 32):
        # 世界坐标
        self.world_x = x
        self.world_y = y
        
        # 尺寸
        self.width = width
        self.height = height
        
        # 矩形（用于碰撞检测）
        self.rect = pygame.Rect(0, 0, width, height)
        self._update_rect()
        
        # 渲染相关
        self.image: Optional[pygame.Surface] = None
        self.visible = True
        self.alpha = 255
        
        # 动画相关
        self.animation_frame = 0
        self.animation_timer = 0
        self.animation_speed = 0.1
        
        # 状态
        self.active = True
        self.alive = True
        
        # 标签（用于分类和识别）
        self.tags: set = set()
        
        # 自定义数据
        self.data: Dict[str, Any] = {}
        
    def _update_rect(self):
        """更新矩形位置"""
        self.rect.centerx = int(self.world_x)
        self.rect.centery = int(self.world_y)
        
    def set_position(self, x: float, y: float):
        """设置位置"""
        self.world_x = x
        self.world_y = y
        self._update_rect()
        
    def move(self, dx: float, dy: float):
        """移动实体"""
        self.world_x += dx
        self.world_y += dy
        self._update_rect()
        
    def get_position(self) -> Tuple[float, float]:
        """获取位置"""
        return self.world_x, self.world_y
        
    def get_center(self) -> Tuple[float, float]:
        """获取中心位置"""
        return self.world_x, self.world_y
        
    def set_image(self, image: pygame.Surface):
        """设置图像"""
        self.image = image
        if image:
            self.width = image.get_width()
            self.height = image.get_height()
            self.rect.width = self.width
            self.rect.height = self.height
            self._update_rect()
            
    def set_visible(self, visible: bool):
        """设置可见性"""
        self.visible = visible
        
    def set_alpha(self, alpha: int):
        """设置透明度"""
        self.alpha = max(0, min(255, alpha))
        
    def add_tag(self, tag: str):
        """添加标签"""
        self.tags.add(tag)
        
    def remove_tag(self, tag: str):
        """移除标签"""
        self.tags.discard(tag)
        
    def has_tag(self, tag: str) -> bool:
        """检查是否有标签"""
        return tag in self.tags
        
    def set_data(self, key: str, value: Any):
        """设置自定义数据"""
        self.data[key] = value
        
    def get_data(self, key: str, default: Any = None) -> Any:
        """获取自定义数据"""
        return self.data.get(key, default)
        
    def distance_to(self, other: 'Entity') -> float:
        """计算到另一个实体的距离"""
        dx = self.world_x - other.world_x
        dy = self.world_y - other.world_y
        return (dx * dx + dy * dy) ** 0.5
        
    def is_colliding_with(self, other: 'Entity') -> bool:
        """检查是否与另一个实体碰撞"""
        return self.rect.colliderect(other.rect)
        
    def is_in_range(self, other: 'Entity', range_distance: float) -> bool:
        """检查是否在指定范围内"""
        return self.distance_to(other) <= range_distance
        
    @abstractmethod
    def update(self, dt: float):
        """更新实体"""
        pass
        
    def render(self, screen: pygame.Surface, camera_x: float = 0, camera_y: float = 0):
        """渲染实体"""
        if not self.visible or not self.image:
            return
            
        # 计算屏幕坐标
        screen_x = int(self.world_x - camera_x)
        screen_y = int(self.world_y - camera_y)
        
        # 检查是否在屏幕范围内
        screen_width, screen_height = screen.get_size()
        if (screen_x < -self.width or screen_x > screen_width + self.width or
            screen_y < -self.height or screen_y > screen_height + self.height):
            return
            
        # 创建临时图像（用于透明度）
        if self.alpha != 255:
            temp_image = self.image.copy()
            temp_image.set_alpha(self.alpha)
            screen.blit(temp_image, (screen_x - self.width // 2, screen_y - self.height // 2))
        else:
            screen.blit(self.image, (screen_x - self.width // 2, screen_y - self.height // 2))
            
    def destroy(self):
        """销毁实体"""
        self.active = False
        self.alive = False
        
    def reset(self):
        """重置实体"""
        self.active = True
        self.alive = True
        self.animation_frame = 0
        self.animation_timer = 0 
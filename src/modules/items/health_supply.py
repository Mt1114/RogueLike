"""
生命补给物品
提供生命值恢复功能
"""

import pygame
import math
from .item import Item
from ..resource_manager import resource_manager

class HealthSupply(Item):
    """生命补给物品"""
    
    def __init__(self, x, y):
        """
        初始化生命补给
        
        Args:
            x, y: 补给在世界坐标系中的位置
        """
        # 设置图像（使用心形图标）
        try:
            # 使用资源管理器加载图片，确保在打包环境中也能正常工作
            self.image = resource_manager.load_image('heart_supply', 'images/ui/heart.png')
            self.image = pygame.transform.scale(self.image, (96, 96))
        except Exception as e:
            
            # 如果加载失败，创建一个默认的红色圆形图标
            self.image = pygame.Surface((96, 96), pygame.SRCALPHA)
            pygame.draw.circle(self.image, (255, 0, 0), (48, 48), 48)
        
        # 调用父类初始化
        super().__init__(x, y, 'health_supply')
        
        # 生命补给特有属性
        self.health_percent = 0.5  # 恢复50%的最大生命值
        self.lifetime = 60.0  # 存活时间20秒
        self.time_alive = 0.0  # 已存活时间
        
        # 动画效果
        self.bob_speed = 3.0  # 浮动速度
        self.bob_amount = 5.0  # 浮动幅度
        self.bob_timer = 0.0  # 浮动计时器
        
        # 闪烁效果（最后10秒开始闪烁）
        self.blink_start_time = 50.0  # 开始闪烁的时间
        self.blink_speed = 5.0  # 闪烁速度
        
    def update(self, dt):
        """更新生命补给状态
        
        Args:
            dt: 时间间隔
            
        Returns:
            bool: 如果补给仍然有效返回True，否则返回False
        """
        # 更新存活时间
        self.time_alive += dt
        
        # 检查是否超时
        if self.time_alive >= self.lifetime:
            return False  # 补给已超时
            
        # 更新浮动动画计时器（只用于渲染效果，不影响世界坐标）
        self.bob_timer += dt * self.bob_speed
        
        # 更新碰撞区域位置（跟随浮动效果）
        bob_offset = math.sin(self.bob_timer) * self.bob_amount
        self.rect.centerx = self.world_x
        self.rect.centery = self.world_y + int(bob_offset)
        
        return True  # 补给仍然有效
        
    def on_pickup(self, player):
        """玩家拾取补给时的处理
        
        Args:
            player: 玩家实例
            
        Returns:
            bool: 拾取是否成功
        """
        if hasattr(player, 'health_component'):
            health_comp = player.health_component
            current_health = health_comp.health
            max_health = health_comp.max_health
            
            # 计算恢复量（50%的最大生命值，但不超出最大生命值）
            heal_amount = int(max_health * self.health_percent)
            new_health = min(current_health + heal_amount, max_health)
            actual_heal = new_health - current_health
            
            if actual_heal > 0:
                health_comp.health = new_health
                
                return True  # 拾取成功
        return False  # 未拾取成功
        
    def render(self, screen, camera_x, camera_y, screen_center_x=None, screen_center_y=None):
        """渲染生命补给
        
        Args:
            screen: pygame屏幕对象
            camera_x: 相机X坐标
            camera_y: 相机Y坐标
            screen_center_x: 屏幕中心X坐标
            screen_center_y: 屏幕中心Y坐标
        """
        # 计算屏幕坐标（使用与门相同的坐标系统）
        if screen_center_x is not None and screen_center_y is not None:
            screen_x = screen_center_x + (self.world_x - camera_x)
            screen_y = screen_center_y + (self.world_y - camera_y)
        else:
            screen_x = int(self.world_x - camera_x)
            screen_y = int(self.world_y - camera_y)
        
        # 应用浮动效果（只影响渲染位置，不影响世界坐标）
        bob_offset = math.sin(self.bob_timer) * self.bob_amount
        screen_y += int(bob_offset)
        
        # 检查是否应该闪烁（最后10秒）
        if self.time_alive >= self.blink_start_time:
            blink_alpha = int(255 * (0.5 + 0.5 * math.sin(self.bob_timer * self.blink_speed)))
            # 创建带透明度的表面
            alpha_surface = self.image.copy()
            alpha_surface.set_alpha(blink_alpha)
            screen.blit(alpha_surface, (screen_x - 16, screen_y - 16))
        else:
            # 正常渲染
            screen.blit(self.image, (screen_x - 16, screen_y - 16))
            
        # 调试：绘制红色边框（可选）
        # pygame.draw.rect(screen, (255, 0, 0), (screen_x - 16, screen_y - 16, 32, 32), 1)
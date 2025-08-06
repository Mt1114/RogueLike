import pygame
import math
import random

class DamageNumber:
    """单个伤害数字类"""
    
    def __init__(self, x, y, damage, color=(255, 255, 255), font_size=24):
        """
        初始化伤害数字
        
        Args:
            x: 显示位置的X坐标
            y: 显示位置的Y坐标
            damage: 伤害值
            color: 数字颜色，默认为白色
            font_size: 字体大小
        """
        self.x = x
        self.y = y
        self.damage = damage
        self.color = color
        self.font_size = font_size
        
        # 动画相关
        self.life_timer = 0
        self.life_duration = 1.0  # 显示1秒
        self.fade_start = 0.7  # 0.7秒后开始淡出
        
        # 移动相关
        self.velocity_x = random.uniform(-20, 20)  # 随机水平速度
        self.velocity_y = -50  # 向上移动
        self.gravity = 100  # 重力
        
        # 字体
        self.font = pygame.font.SysFont('simHei', font_size)
        
        # 渲染文本
        self.text_surface = self.font.render(str(damage), True, color)
        
    def update(self, dt):
        """
        更新伤害数字状态
        
        Args:
            dt: 时间增量
        """
        # 更新生命计时器
        self.life_timer += dt
        
        # 更新位置
        self.x += self.velocity_x * dt
        self.y += self.velocity_y * dt
        
        # 应用重力
        self.velocity_y += self.gravity * dt
        
        # 检查是否应该销毁
        return self.life_timer >= self.life_duration
        
    def render(self, screen, camera_x, camera_y):
        """
        渲染伤害数字
        
        Args:
            screen: pygame屏幕对象
            camera_x: 相机X坐标
            camera_y: 相机Y坐标
        """
        # 计算屏幕位置
        screen_x = self.x - camera_x + screen.get_width() // 2
        screen_y = self.y - camera_y + screen.get_height() // 2
        
        # 计算透明度
        alpha = 255
        if self.life_timer > self.fade_start:
            # 开始淡出
            fade_progress = (self.life_timer - self.fade_start) / (self.life_duration - self.fade_start)
            alpha = int(255 * (1 - fade_progress))
        
        # 创建带透明度的表面
        if alpha < 255:
            # 创建临时表面用于设置透明度
            temp_surface = self.text_surface.copy()
            temp_surface.set_alpha(alpha)
            screen.blit(temp_surface, (screen_x, screen_y))
        else:
            screen.blit(self.text_surface, (screen_x, screen_y))

class DamageNumberManager:
    """伤害数字管理器"""
    
    def __init__(self):
        """初始化伤害数字管理器"""
        self.damage_numbers = []
        
        # 不同伤害类型的颜色配置
        self.damage_colors = {
            'normal': (255, 255, 255),    # 普通伤害 - 白色
            'critical': (255, 255, 0),    # 暴击伤害 - 黄色
            'fire': (255, 100, 0),        # 火焰伤害 - 橙色
            'ice': (100, 200, 255),       # 冰冻伤害 - 蓝色
            'poison': (0, 255, 0),        # 毒伤害 - 绿色
            'magic': (255, 0, 255),       # 魔法伤害 - 紫色
        }
        
    def add_damage_number(self, x, y, damage, damage_type='normal', font_size=24):
        """
        添加一个伤害数字
        
        Args:
            x: 显示位置的X坐标
            y: 显示位置的Y坐标
            damage: 伤害值
            damage_type: 伤害类型，用于确定颜色
            font_size: 字体大小
        """
        # 获取颜色
        color = self.damage_colors.get(damage_type, self.damage_colors['normal'])
        
        # 创建伤害数字
        damage_number = DamageNumber(x, y, damage, color, font_size)
        self.damage_numbers.append(damage_number)
        
    def update(self, dt):
        """
        更新所有伤害数字
        
        Args:
            dt: 时间增量
        """
        # 更新所有伤害数字并移除已销毁的
        self.damage_numbers = [num for num in self.damage_numbers if not num.update(dt)]
        
    def render(self, screen, camera_x, camera_y):
        """
        渲染所有伤害数字
        
        Args:
            screen: pygame屏幕对象
            camera_x: 相机X坐标
            camera_y: 相机Y坐标
        """
        for damage_number in self.damage_numbers:
            damage_number.render(screen, camera_x, camera_y)
            
    def clear(self):
        """清空所有伤害数字"""
        self.damage_numbers.clear() 
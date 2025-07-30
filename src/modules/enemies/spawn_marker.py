import pygame
import math

class SpawnMarker:
    def __init__(self, x, y, duration=2.0):
        """创建出生点标记
        
        Args:
            x: 世界坐标系中的x坐标
            y: 世界坐标系中的y坐标
            duration: 标记显示时间（秒）
        """
        self.world_x = x
        self.world_y = y
        self.duration = duration
        self.timer = 0
        self.alpha = 255  # 透明度
        self.size = 40  # 标记大小
        
        # 创建标记表面
        self.surface = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        self._draw_marker()
        
    def _draw_marker(self):
        """绘制红色出生点标记"""
        # 绘制红色圆圈
        center = (self.size // 2, self.size // 2)
        radius = self.size // 2 - 2
        
        # 外圈（深红色）
        pygame.draw.circle(self.surface, (139, 0, 0, self.alpha), center, radius)
        
        # 内圈（亮红色）
        inner_radius = radius - 4
        pygame.draw.circle(self.surface, (255, 0, 0, self.alpha), center, inner_radius)
        
        # 中心点（白色）
        center_radius = 3
        pygame.draw.circle(self.surface, (255, 255, 255, self.alpha), center, center_radius)
        
        # 添加一些装饰性的小点
        for i in range(8):
            angle = i * math.pi / 4
            dot_x = center[0] + (radius - 8) * math.cos(angle)
            dot_y = center[1] + (radius - 8) * math.sin(angle)
            pygame.draw.circle(self.surface, (255, 255, 255, self.alpha), 
                             (int(dot_x), int(dot_y)), 2)
    
    def update(self, dt):
        """更新标记状态"""
        self.timer += dt
        
        # 计算透明度（逐渐消失）
        if self.timer >= self.duration * 0.7:  # 70%时间后开始淡出
            fade_time = self.timer - self.duration * 0.7
            fade_duration = self.duration * 0.3
            self.alpha = int(255 * (1 - fade_time / fade_duration))
            self.alpha = max(0, self.alpha)
            self._draw_marker()  # 重新绘制以更新透明度
        
        return self.timer < self.duration
    
    def render(self, screen, camera_x, camera_y, screen_center_x, screen_center_y):
        """渲染出生点标记"""
        # 计算屏幕位置
        screen_x = screen_center_x + (self.world_x - camera_x) - self.size // 2
        screen_y = screen_center_y + (self.world_y - camera_y) - self.size // 2
        
        # 只渲染在屏幕范围内的标记
        if -self.size <= screen_x <= screen.get_width() + self.size and \
           -self.size <= screen_y <= screen.get_height() + self.size:
            screen.blit(self.surface, (screen_x, screen_y)) 
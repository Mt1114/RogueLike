import pygame
from .resource_manager import resource_manager

class LevelTransition:
    """关卡过渡动画类"""
    
    def __init__(self, screen):
        self.screen = screen
        self.is_active = False
        self.duration = 5.0  # 持续5秒
        self.current_time = 0.0
        self.next_map = None
        
        # 加载背景图片
        self.background_image = None
        self._load_background()
        
        # 字体设置
        self.font = pygame.font.SysFont('simHei', 72)
        
    def _load_background(self):
        """加载背景图片"""
        try:
            self.background_image = resource_manager.load_image('background_ui', 'images/ui/background.png')
            print(f"关卡过渡背景加载状态: {self.background_image is not None}")
        except Exception as e:
            print(f"加载关卡过渡背景失败: {e}")
    
    def start(self, next_map):
        """开始关卡过渡动画
        
        Args:
            next_map: 下一关地图名称
        """
        print(f"开始关卡过渡动画，下一关: {next_map}")
        self.is_active = True
        self.current_time = 0.0
        self.next_map = next_map
    
    def update(self, dt):
        """更新关卡过渡动画"""
        if not self.is_active:
            return
        
        self.current_time += dt
        
        # 5秒后结束动画
        if self.current_time >= self.duration:
            self.is_active = False
            print("关卡过渡动画结束")
            return "next_level"  # 返回进入下一关的信号
    
    def render(self):
        """渲染关卡过渡动画"""
        if not self.is_active:
            return
        
        # 渲染背景
        if self.background_image:
            # 缩放背景到屏幕大小
            scaled_background = pygame.transform.scale(
                self.background_image, 
                (self.screen.get_width(), self.screen.get_height())
            )
            self.screen.blit(scaled_background, (0, 0))
        else:
            # 如果没有背景图片，使用黑色背景
            self.screen.fill((0, 0, 0))
        
        # 计算淡入淡出效果
        fade_progress = self.current_time / self.duration
        
        # 文字淡入淡出效果（前2秒淡入，后2秒淡出，中间1秒保持）
        if fade_progress <= 0.4:  # 前2秒淡入
            alpha = int(255 * (fade_progress / 0.4))
        elif fade_progress >= 0.6:  # 后2秒淡出
            alpha = int(255 * ((1.0 - fade_progress) / 0.4))
        else:  # 中间1秒保持
            alpha = 255
        
        # 渲染"NextLevel"文字
        text_surface = self.font.render("NextLevel", True, (255, 255, 255))
        
        # 创建带透明度的表面
        text_with_alpha = pygame.Surface(text_surface.get_size(), pygame.SRCALPHA)
        text_with_alpha.fill((255, 255, 255, alpha))
        text_surface.blit(text_with_alpha, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        
        # 居中显示文字
        text_rect = text_surface.get_rect(center=(
            self.screen.get_width() // 2,
            self.screen.get_height() // 2
        ))
        self.screen.blit(text_surface, text_rect) 
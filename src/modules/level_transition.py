import pygame
import math

class LevelTransition:
    """关卡切换动画类"""
    
    def __init__(self, screen):
        self.screen = screen
        self.is_active = False
        self.next_map = None
        
        # 动画状态
        self.animation_phase = "fade_in"  # fade_in, show_text, fade_out
        self.animation_timer = 0
        self.total_duration = 5.0  # 总时长5秒
        
        # 各阶段时长
        self.fade_in_duration = 1.0    # 渐入1秒
        self.show_text_duration = 3.0  # 显示文字3秒
        self.fade_out_duration = 1.0   # 渐出1秒
        
        # 透明度
        self.alpha = 0
        self.max_alpha = 255
        
        # 加载背景图片
        self.background_image = None
        self._load_background()
        
        # 字体
        self.font = None
        self._load_font()
        
        # 文字内容
        self.text_lines = [
            "下一关！",
            "准备！"
        ]
        
    def _load_background(self):
        """加载背景图片并自适应屏幕"""
        try:
            from .resource_manager import resource_manager
            # 加载背景图片
            self.background_image = resource_manager.load_image('background', 'images/ui/background.png')
            
            if self.background_image:
                # 获取屏幕尺寸
                screen_width = self.screen.get_width()
                screen_height = self.screen.get_height()
                
                # 缩放背景图片以适应屏幕
                self.background_image = pygame.transform.scale(
                    self.background_image, 
                    (screen_width, screen_height)
                )
                print("关卡切换背景图片加载成功")
            else:
                print("关卡切换背景图片加载失败")
        except Exception as e:
            print(f"无法加载关卡切换背景图片: {e}")
            self.background_image = None
    
    def _load_font(self):
        """加载字体"""
        try:
            # 尝试加载中文字体
            self.font = pygame.font.SysFont('simHei', 48)
        except:
            try:
                # 备用字体
                self.font = pygame.font.SysFont('arial', 48)
            except:
                # 默认字体
                self.font = pygame.font.Font(None, 48)
    
    def start(self, next_map):
        """开始关卡切换动画
        
        Args:
            next_map: 下一关的地图名称
        """
        self.next_map = next_map
        self.is_active = True
        self.animation_phase = "fade_in"
        self.animation_timer = 0
        self.alpha = 0
        print(f"开始关卡切换动画，下一关: {next_map}")
    
    def update(self, dt):
        """更新动画状态
        
        Args:
            dt: 时间增量
            
        Returns:
            str: 动画完成时返回"next_level"，否则返回None
        """
        if not self.is_active:
            return None
        
        self.animation_timer += dt
        
        if self.animation_phase == "fade_in":
            # 渐入阶段
            progress = self.animation_timer / self.fade_in_duration
            self.alpha = int(self.max_alpha * progress)
            
            if self.animation_timer >= self.fade_in_duration:
                self.animation_phase = "show_text"
                self.animation_timer = 0
                self.alpha = self.max_alpha
                
        elif self.animation_phase == "show_text":
            # 显示文字阶段
            if self.animation_timer >= self.show_text_duration:
                self.animation_phase = "fade_out"
                self.animation_timer = 0
                
        elif self.animation_phase == "fade_out":
            # 渐出阶段
            progress = self.animation_timer / self.fade_out_duration
            self.alpha = int(self.max_alpha * (1 - progress))
            
            if self.animation_timer >= self.fade_out_duration:
                # 动画完成
                self.is_active = False
                self.alpha = 0
                return "next_level"
        
        return None
    
    def render(self):
        """渲染关卡切换动画"""
        if not self.is_active:
            return
        
        # 创建覆盖整个屏幕的黑色半透明层
        overlay = pygame.Surface((self.screen.get_width(), self.screen.get_height()))
        overlay.set_alpha(self.alpha)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))
        
        # 如果有背景图片，渲染背景图片
        if self.background_image:
            # 创建带透明度的背景图片
            background_surface = self.background_image.copy()
            background_surface.set_alpha(self.alpha)
            self.screen.blit(background_surface, (0, 0))
        
        # 只在显示文字阶段渲染文字
        if self.animation_phase == "show_text" and self.font:
            # 计算文字位置（屏幕中心）
            screen_width = self.screen.get_width()
            screen_height = self.screen.get_height()
            
            # 渲染文字
            for i, text in enumerate(self.text_lines):
                # 创建文字表面
                text_surface = self.font.render(text, True, (255, 255, 255))
                text_rect = text_surface.get_rect()
                
                # 计算垂直位置（文字垂直居中，两行文字之间有间距）
                total_text_height = len(self.text_lines) * text_rect.height + (len(self.text_lines) - 1) * 20
                start_y = screen_height // 2 - total_text_height // 2
                
                text_rect.centerx = screen_width // 2
                text_rect.y = start_y + i * (text_rect.height + 20)
                
                # 渲染文字
                self.screen.blit(text_surface, text_rect) 
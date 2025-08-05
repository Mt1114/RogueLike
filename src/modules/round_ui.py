import pygame
from .resource_manager import resource_manager

class RoundUI:
    """波次UI显示类，用于显示Round1、Round2、Round3图片"""
    
    def __init__(self, screen):
        self.screen = screen
        self.is_active = False
        self.duration = 5.0  # 持续5秒
        self.current_time = 0.0
        self.current_round = 1
        
        # 加载波次图片
        self.round_images = {}
        self._load_round_images()
        
    def _load_round_images(self):
        """加载波次图片"""
        try:
            self.round_images[1] = resource_manager.load_image('round1_ui', 'images/ui/Round1.png')
            self.round_images[2] = resource_manager.load_image('round2_ui', 'images/ui/Round2.png')
            self.round_images[3] = resource_manager.load_image('round3_ui', 'images/ui/Round3.png')
            
            print(f"波次UI图片加载状态:")
            print(f"  Round1: {self.round_images[1] is not None}")
            print(f"  Round2: {self.round_images[2] is not None}")
            print(f"  Round3: {self.round_images[3] is not None}")
            
        except Exception as e:
            print(f"加载波次UI图片失败: {e}")
    
    def show_round(self, round_number):
        """显示指定波次的UI
        
        Args:
            round_number: 波次编号（1、2、3）
        """
        if round_number not in [1, 2, 3]:
            print(f"无效的波次编号: {round_number}")
            return
        
        print(f"显示波次UI: Round{round_number}")
        self.is_active = True
        self.current_time = 0.0
        self.current_round = round_number
    
    def update(self, dt):
        """更新波次UI"""
        if not self.is_active:
            return
        
        self.current_time += dt
        
        # 5秒后结束动画
        if self.current_time >= self.duration:
            self.is_active = False
            print(f"波次UI结束: Round{self.current_round}")
    
    def render(self):
        """渲染波次UI"""
        if not self.is_active:
            return
        
        # 获取当前波次的图片
        round_image = self.round_images.get(self.current_round)
        if not round_image:
            print(f"波次图片未加载: Round{self.current_round}")
            return
        
        # 计算淡入淡出效果
        fade_progress = self.current_time / self.duration
        
        # 淡入淡出效果（前1秒淡入，后1秒淡出，中间3秒保持）
        if fade_progress <= 0.2:  # 前1秒淡入
            alpha = int(255 * (fade_progress / 0.2))
        elif fade_progress >= 0.8:  # 后1秒淡出
            alpha = int(255 * ((1.0 - fade_progress) / 0.2))
        else:  # 中间3秒保持
            alpha = 255
        
        # 自适应屏幕大小
        screen_width = self.screen.get_width()
        screen_height = self.screen.get_height()
        
        # 计算缩放比例，占满整个屏幕
        img_width, img_height = round_image.get_size()
        scale_x = screen_width / img_width
        scale_y = screen_height / img_height
        scale = max(scale_x, scale_y)  # 使用max确保占满屏幕
        
        # 缩放图片
        scaled_width = int(img_width * scale)
        scaled_height = int(img_height * scale)
        scaled_image = pygame.transform.scale(round_image, (scaled_width, scaled_height))
        
        # 居中显示
        x = (screen_width - scaled_width) // 2-100
        y = (screen_height - scaled_height) // 2-30
        
        # 创建带透明度的表面
        if alpha < 255:
            # 创建临时表面来应用透明度
            temp_surface = pygame.Surface(scaled_image.get_size(), pygame.SRCALPHA)
            temp_surface.fill((255, 255, 255, alpha))
            scaled_image.blit(temp_surface, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        
        # 渲染到屏幕
        self.screen.blit(scaled_image, (x, y)) 
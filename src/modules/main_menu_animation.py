import pygame
import math
from .resource_manager import resource_manager

class MainMenuAnimation:
    """主页动画类 - 实现背景和logo先显示，然后三个按钮淡入浮动进入"""
    
    def __init__(self, screen):
        self.screen = screen
        self.screen_width = screen.get_width()
        self.screen_height = screen.get_height()
        
        # 动画状态
        self.is_playing = True
        self.animation_timer = 0
        self.total_duration = 4.0  # 总动画时长4秒
        
        # 动画阶段
        self.stage = "background"  # background -> logo -> buttons
        self.stage_timer = 0
        
        # 加载资源
        self._load_resources()
        
        # 按钮动画参数
        self.buttons = []
        self._init_buttons()
        
    def _load_resources(self):
        """加载动画所需的资源"""
        # 加载背景
        try:
            self.background = resource_manager.load_image('menu_background', 'images/ui/Home_page.png')
            self.background = pygame.transform.scale(self.background, (self.screen_width, self.screen_height))
        except:
            self.background = None
            
        # 加载logo
        try:
            self.logo = resource_manager.load_image('logo', 'images/ui/logo_white.png')
            # 调整logo大小
            logo_width = 600
            logo_height = 300
            self.logo = pygame.transform.scale(self.logo, (logo_width, logo_height))
        except Exception as e:
            print(f"加载logo图片失败: {e}")
            self.logo = None
            
        # 加载按钮图片
        try:
            self.start_button = resource_manager.load_image('start_button', 'images/ui/Start.png')
            self.options_button = resource_manager.load_image('options_button', 'images/ui/Options.png')
            self.back_button = resource_manager.load_image('back_button', 'images/ui/Back.png')
            
            # 调整按钮大小
            button_width = 300
            button_height = 120
            self.start_button = pygame.transform.scale(self.start_button, (button_width, button_height))
            self.options_button = pygame.transform.scale(self.options_button, (button_width, button_height))
            self.back_button = pygame.transform.scale(self.back_button, (button_width, button_height))
        except Exception as e:
            print(f"加载按钮图片失败: {e}")
            self.start_button = None
            self.options_button = None
            self.back_button = None
    
    def _init_buttons(self):
        """初始化按钮动画参数"""
        button_images = [self.start_button, self.options_button, self.back_button]
        screen_center_x = self.screen_width // 2
        first_button_y = 350
        button_padding = 180
        
        self.buttons = []
        for i, button_img in enumerate(button_images):
            if button_img:
                button_y = first_button_y + i * button_padding
                button_data = {
                    'image': button_img,
                    'target_x': screen_center_x,
                    'target_y': button_y,
                    'current_x': screen_center_x + 400,  # 从右侧进入
                    'current_y': button_y,
                    'alpha': 0,  # 透明度
                    'scale': 0.8,  # 初始缩放
                    'float_offset': 0,  # 浮动偏移
                    'delay': i * 0.3,  # 每个按钮延迟0.3秒
                    'animation_timer': 0
                }
                self.buttons.append(button_data)
    
    def update(self, dt):
        """更新动画"""
        if not self.is_playing:
            return
            
        self.animation_timer += dt
        self.stage_timer += dt
        
        # 阶段控制
        if self.stage == "background":
            if self.stage_timer >= 0.5:  # 背景显示0.5秒
                self.stage = "logo"
                self.stage_timer = 0
        elif self.stage == "logo":
            if self.stage_timer >= 1.5:  # logo显示1.5秒
                self.stage = "buttons"
                self.stage_timer = 0
        elif self.stage == "buttons":
            if self.stage_timer >= 2.0:  # 按钮动画2秒
                self.is_playing = False
        
        # 更新按钮动画
        if self.stage == "buttons":
            for button in self.buttons:
                button['animation_timer'] += dt
                
                if button['animation_timer'] >= button['delay']:
                    # 计算动画进度
                    progress = min((button['animation_timer'] - button['delay']) / 1.0, 1.0)
                    
                    # 位置动画（从右侧滑入）
                    button['current_x'] = button['target_x'] + (400 * (1 - progress))
                    
                    # 透明度动画
                    button['alpha'] = int(255 * progress)
                    
                    # 缩放动画
                    button['scale'] = 0.8 + (0.2 * progress)
                    
                    # 浮动效果
                    button['float_offset'] = math.sin(button['animation_timer'] * 2) * 3
    
    def render(self):
        """渲染动画"""
        # 渲染背景
        if self.background:
            self.screen.blit(self.background, (0, 0))
        else:
            self.screen.fill((0, 0, 0))
        
        # 渲染logo（在logo阶段）
        if self.stage in ["logo", "buttons"] and self.logo:
            # 计算logo透明度
            if self.stage == "logo":
                logo_progress = min(self.stage_timer / 0.5, 1.0)  # 0.5秒淡入
                logo_alpha = int(255 * logo_progress)
            else:
                logo_alpha = 255
            
            # 创建带透明度的logo表面
            logo_surface = self.logo.copy()
            logo_surface.set_alpha(logo_alpha)
            
            # 计算logo位置
            logo_rect = logo_surface.get_rect()
            logo_rect.centerx = self.screen_width // 2 - 700  # 向左移动
            logo_rect.y = 50
            
            # 添加轻微的浮动效果
            float_offset = math.sin(self.stage_timer * 2) * 5
            logo_rect.centery += float_offset
            
            self.screen.blit(logo_surface, logo_rect)
        
        # 渲染按钮（在buttons阶段）
        if self.stage == "buttons":
            for button in self.buttons:
                if button['alpha'] > 0:
                    # 创建带透明度的按钮表面
                    button_surface = button['image'].copy()
                    button_surface.set_alpha(button['alpha'])
                    
                    # 应用缩放
                    scaled_width = int(button['image'].get_width() * button['scale'])
                    scaled_height = int(button['image'].get_height() * button['scale'])
                    scaled_button = pygame.transform.scale(button_surface, (scaled_width, scaled_height))
                    
                    # 计算按钮位置
                    button_rect = scaled_button.get_rect()
                    button_rect.centerx = button['current_x']
                    button_rect.centery = button['current_y'] + button['float_offset']
                    
                    self.screen.blit(scaled_button, button_rect)
    
    def is_finished(self):
        """检查动画是否结束"""
        return not self.is_playing 
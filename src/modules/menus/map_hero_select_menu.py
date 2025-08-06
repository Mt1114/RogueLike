import pygame
from ..resource_manager import resource_manager
from ..utils import FontManager

class MapHeroSelectMenu:
    """英雄选择菜单"""
    
    def __init__(self, screen, on_start_game=None, on_back=None):
        """初始化英雄选择菜单
        
        Args:
            screen: 游戏屏幕
            on_start_game: 开始游戏回调函数，接收地图ID和英雄ID作为参数
            on_back: 返回按钮回调函数
        """
        self.screen = screen
        self.on_start_game = on_start_game
        self.on_back = on_back
        
        # 菜单状态
        self.active = False
        
        # 界面参数
        self.width = screen.get_width()
        self.height = screen.get_height()
        
        # 使用FontManager加载字体
        self.title_font = FontManager.get_font(60)
        self.button_font = FontManager.get_font(36)
        
        # 颜色设置
        self.title_color = (255, 255, 255)
        self.button_color = (255, 255, 255, 100)  # 半透明白色
        self.button_hover_color = (255, 255, 255, 150)  # 悬停时更不透明
        self.button_text_color = (255, 255, 255)
        self.bg_color = (30, 30, 30)
        
        # 计算屏幕中心
        self.screen_center_x = self.screen.get_width() // 2
        self.screen_center_y = self.screen.get_height() // 2
        
        # 确认按钮的尺寸和位置（往上移动200像素）
        self.button_width = 300
        self.button_height = 80
        self.button_rect = pygame.Rect(
            self.screen_center_x - self.button_width // 2,
            self.height - 250,  # 距离底部250像素（原来是350，往下移动100）
            self.button_width,
            self.button_height
        )
        
        # 按钮悬停状态
        self.button_hovered = False
        
        # 加载角色图片
        try:
            self.role1_img = resource_manager.load_image('role1_big', 'images/ui/role1_big.png')
            self.role2_img = resource_manager.load_image('role2_big', 'images/ui/role2_big.png')
            self.p1_img = resource_manager.load_image('p1', 'images/ui/p1.png')
            self.p2_img = resource_manager.load_image('p2', 'images/ui/p2.png')
        except Exception as e:
            print(f"加载角色图片失败: {e}")
            self.role1_img = None
            self.role2_img = None
            self.p1_img = None
            self.p2_img = None
        
        # 加载普通图片
        try:
            print("正在加载英雄选择界面图片: images/ui/background.png")
            self.background_image = resource_manager.load_image('menu_image', 'images/ui/background.png')
            print("英雄选择界面图片加载成功")
        except Exception as e:
            print(f"加载图片失败: {e}")
            self.background_image = None
        
    def show(self):
        """显示菜单"""
        self.active = True
        resource_manager.play_sound("menu_show")
        
    def hide(self):
        """隐藏菜单"""
        self.active = False
        
    def handle_event(self, event):
        """处理事件
        
        Args:
            event: pygame事件
            
        Returns:
            str: 事件处理结果，如"back"、"start_game"等
        """
        if not self.active:
            return None
            
        # 更新按钮悬停状态
        mouse_pos = pygame.mouse.get_pos()
        old_hover = self.button_hovered
        self.button_hovered = self.button_rect.collidepoint(mouse_pos)
        
        # 如果悬停状态改变，播放移动音效
        if old_hover != self.button_hovered and self.button_hovered:
            resource_manager.play_sound("menu_move")
            
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # 鼠标左键点击
            # 检查是否点击了确认按钮
            if self.button_rect.collidepoint(mouse_pos):
                resource_manager.play_sound("menu_select")
                if self.on_start_game:
                    # 直接进入双人模式，默认选择small_map和忍者蛙
                    self.on_start_game("small_map", "ninja_frog")
                return "start_game"
                
        elif event.type == pygame.KEYDOWN:
            if event.key in [pygame.K_RETURN, pygame.K_SPACE]:
                resource_manager.play_sound("menu_select")
                if self.on_start_game:
                    # 直接进入双人模式，默认选择small_map和忍者蛙
                    self.on_start_game("small_map", "ninja_frog")
                return "start_game"
                
        return None
        
    def render(self):
        """渲染菜单"""
        if not self.active:
            return
            
        # 绘制纯色背景
        self.screen.fill(self.bg_color)
        
        # 绘制普通图片（居中显示）
        if self.background_image:
            # 计算图片位置，使其居中显示
            image_rect = self.background_image.get_rect()
            image_rect.center = (self.screen_center_x, self.screen_center_y)
            self.screen.blit(self.background_image, image_rect)
        
       
        
        # 绘制确认按钮（透明）
        button_color = self.button_hover_color if self.button_hovered else self.button_color
        
        # 创建透明按钮表面
        button_surface = pygame.Surface((self.button_width, self.button_height), pygame.SRCALPHA)
        button_surface.fill(button_color)
        self.screen.blit(button_surface, self.button_rect)
        
        # 绘制按钮边框
        border_color = (255, 255, 0) if self.button_hovered else (255, 255, 255)
        pygame.draw.rect(self.screen, border_color, self.button_rect, 2, 10)
        
        # 绘制按钮文本
        button_text = self.button_font.render("确认进入游戏", True, self.button_text_color)
        text_rect = button_text.get_rect(center=self.button_rect.center)
        self.screen.blit(button_text, text_rect) 
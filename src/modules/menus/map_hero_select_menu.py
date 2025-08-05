import pygame
from ..resource_manager import resource_manager
from ..utils import FontManager

class MapHeroSelectMenu:
    """简化的地图和英雄选择菜单"""
    
    def __init__(self, screen, on_start_game=None, on_back=None):
        """初始化地图和英雄选择菜单
        
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
        self.title_font = FontManager.get_font(50)
        self.button_font = FontManager.get_font(48)
        
        # 颜色设置
        self.title_color = (255, 255, 255)
        self.button_color = (80, 80, 190)
        self.button_hover_color = (100, 100, 210)
        self.button_text_color = (255, 255, 255)
        self.bg_color = (30, 30, 30)
        
        # 计算屏幕中心
        self.screen_center_x = self.screen.get_width() // 2
        self.screen_center_y = self.screen.get_height() // 2
        
        # 大矩形按钮的尺寸和位置
        self.button_width = 400
        self.button_height = 120
        self.button_rect = pygame.Rect(
            self.screen_center_x - self.button_width // 2,
            self.screen_center_y - self.button_height // 2,
            self.button_width,
            self.button_height
        )
        
        # 按钮悬停状态
        self.button_hovered = False
        
        # 加载背景图片
        try:
            print("正在加载地图选择界面背景图片:         images/ui/background.png")
            self.background = resource_manager.load_image('menu_background', 'images/ui/background.png')
            self.background = pygame.transform.scale(self.background, (screen.get_width(), screen.get_height()))
            print("地图选择界面背景图片加载成功")
        except Exception as e:
            print(f"加载背景图片失败: {e}")
            self.background = None
        
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
            # 检查是否点击了按钮
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
            
        # 绘制背景
        if self.background:
            self.screen.blit(self.background, (0, 0))
        else:
            # 如果没有背景图片，填充纯色背景
            self.screen.fill(self.bg_color)
        
        # 绘制大矩形按钮
        button_color = self.button_hover_color if self.button_hovered else self.button_color
        pygame.draw.rect(self.screen, button_color, self.button_rect, 0, 15)  # 圆角矩形
        
        # 绘制按钮边框
        border_color = (255, 255, 0) if self.button_hovered else (100, 100, 100)
        pygame.draw.rect(self.screen, border_color, self.button_rect, 3, 15)
        
        # 绘制按钮文本
        button_text = self.button_font.render("进入战斗", True, self.button_text_color)
        text_rect = button_text.get_rect(center=self.button_rect.center)
        self.screen.blit(button_text, text_rect) 
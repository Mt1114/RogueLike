import pygame
from ..resource_manager import resource_manager
from ..utils import FontManager
from .options_menu import OptionsMenu

class MainMenu:
    def __init__(self, screen):
        self.screen = screen
        self.is_active = True
        
        # 菜单选项和对应的动作
        self.options = ["开始新游戏", "游戏介绍", "退出游戏"]
        self.actions = ["start", "options", "quit"]
        self.selected_index = 0
        
        # 创建选项菜单
        self.options_menu = OptionsMenu(screen)
        
        # 加载字体
        self.title_font = FontManager.get_font(74)
        
        # 颜色设置
        self.title_color = (255, 255, 255)
        
        # 计算菜单位置
        self.screen_center_x = self.screen.get_width() // 2
        self.title_y = 100
        self.first_button_y = 350
        self.button_padding = 180
        
        # 存储按钮的矩形区域（用于检测鼠标点击）
        self.button_rects = []
        
        # 加载背景图片
        try:
            self.background = resource_manager.load_image('menu_background', 'images/ui/Home_page.png')
            self.background = pygame.transform.scale(self.background, (screen.get_width(), screen.get_height()))
        except Exception as e:
            
            self.background = None
            
        # 加载按钮图片
        try:
            self.start_button = resource_manager.load_image('start_button', 'images/ui/Start.png')
            self.options_button = resource_manager.load_image('options_button', 'images/ui/Options.png')
            self.quit_button = resource_manager.load_image('quit_button', 'images/ui/Back.png')  # 使用Back.png作为退出按钮
            
            # 调整按钮大小
            button_width = 300  # 放大1.5倍：200 * 1.5 = 300
            button_height = 120  # 放大1.5倍：80 * 1.5 = 120
            self.start_button = pygame.transform.scale(self.start_button, (button_width, button_height))
            self.options_button = pygame.transform.scale(self.options_button, (button_width, button_height))
            self.quit_button = pygame.transform.scale(self.quit_button, (button_width, button_height))
        except Exception as e:
            
            self.start_button = None
            self.options_button = None
            self.quit_button = None
            
        # 加载logo图片
        try:
            self.logo = resource_manager.load_image('logo', 'images/ui/logo_white.png')
            # 调整logo大小
            logo_width = 600
            logo_height = 300
            self.logo = pygame.transform.scale(self.logo, (logo_width, logo_height))
        except Exception as e:
            
            self.logo = None
            
    def handle_event(self, event):
        """处理输入事件"""
        # 如果选项菜单激活，优先处理选项菜单事件
        if self.options_menu.is_active:
            result = self.options_menu.handle_event(event)
            if result == "back_to_main":
                return "back_to_main"
            return None
        
        if event.type == pygame.KEYDOWN:
            if event.key in [pygame.K_UP, pygame.K_w]:
                self.selected_index = (self.selected_index - 1) % len(self.options)
                resource_manager.play_sound("menu_move")
            elif event.key in [pygame.K_DOWN, pygame.K_s]:
                self.selected_index = (self.selected_index + 1) % len(self.options)
                resource_manager.play_sound("menu_select")
            elif event.key in [pygame.K_RETURN, pygame.K_SPACE]:
                resource_manager.play_sound("menu_select")
                return self.actions[self.selected_index]
                
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = pygame.mouse.get_pos()
            for i, rect in enumerate(self.button_rects):
                if rect.collidepoint(mouse_pos):
                    resource_manager.play_sound("menu_select")
                    return self.actions[i]
                    
        elif event.type == pygame.MOUSEMOTION:
            mouse_pos = pygame.mouse.get_pos()
            for i, rect in enumerate(self.button_rects):
                if rect.collidepoint(mouse_pos):
                    if self.selected_index != i:
                        self.selected_index = i
                        resource_manager.play_sound("menu_move")
                    break
                    
        return None
        
    def render(self):
        """渲染主菜单"""
        # 如果选项菜单激活，渲染选项菜单
        if self.options_menu.is_active:
            self.options_menu.render()
            return
        
        # 绘制背景
        if self.background:
            self.screen.blit(self.background, (0, 0))
        else:
            self.screen.fill((0, 0, 0))
            
        # 清空之前的按钮矩形
        self.button_rects.clear()
        
        # 绘制按钮
        buttons = [self.start_button, self.options_button, self.quit_button]
        
        for i, button_img in enumerate(buttons):
            if button_img:
                # 计算按钮位置（垂直居中排列）
                button_y = self.first_button_y + i * self.button_padding
                button_rect = button_img.get_rect(center=(self.screen_center_x, button_y))
                
                # 如果被选中，添加高亮效果
                if i == self.selected_index:
                    # 创建高亮版本的按钮（稍微放大）
                    highlighted_button = pygame.transform.scale(button_img, 
                        (int(button_img.get_width() * 1.1), int(button_img.get_height() * 1.1)))
                    highlighted_rect = highlighted_button.get_rect(center=(self.screen_center_x, button_y))
                    self.screen.blit(highlighted_button, highlighted_rect)
                    self.button_rects.append(highlighted_rect)
                else:
                    self.screen.blit(button_img, button_rect)
                    self.button_rects.append(button_rect)
        
        # 绘制logo（调整位置）
        if self.logo:
            logo_rect = self.logo.get_rect()
            logo_rect.centerx = self.screen_center_x - 700 # 向左移动600像素
            logo_rect.y = 50  # 距离顶部150像素（向下移动100像素）
            self.screen.blit(self.logo, logo_rect)
            
        # 更新显示
        pygame.display.flip() 
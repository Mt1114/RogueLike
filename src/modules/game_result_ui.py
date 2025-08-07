import pygame
from .resource_manager import resource_manager

class GameResultUI:
    """游戏结果UI类，用于显示胜利或失败界面"""
    
    def __init__(self, screen):
        self.screen = screen
        self.is_active = False
        self.is_victory = False
        self.display_time = 5.0  # 显示5秒
        self.current_time = 0.0
        self.show_buttons = False  # 是否显示按钮
        
        # 按钮状态
        self.button_rects = {}
        self.selected_button = 0  # 0: 重新开始, 1: 回到主页
        self.hovered_button = None  # 鼠标悬停的按钮
        
        # 关卡进阶相关
        self.current_map = None  # 当前地图
        self.next_map = None  # 下一关地图
        self.is_final_level = False  # 是否为最终关卡
        
        # 加载图片
        self._load_images()
        
    def _load_images(self):
        """加载胜利和失败图片以及按钮图片"""
        try:
            # 加载胜利/失败图片
            self.win_image = resource_manager.load_image('win_ui', 'images/ui/WIN.png')
            self.lost_image = resource_manager.load_image('lost_ui', 'images/ui/LOST.png')
            
            # 加载按钮图片
            self.again_image = resource_manager.load_image('again_ui', 'images/ui/Again.png')
            self.home_image = resource_manager.load_image('home_ui', 'images/ui/Home_1.png')
            self.give_up_image = resource_manager.load_image('give_up_ui', 'images/ui/GiveUp.png')
            
            print(f"游戏结果UI图片加载状态:")
            print(f"  WIN: {self.win_image is not None}")
            print(f"  LOST: {self.lost_image is not None}")
            print(f"  AGAIN: {self.again_image is not None}")
            print(f"  HOME: {self.home_image is not None}")
            print(f"  GIVE_UP: {self.give_up_image is not None}")
            
        except Exception as e:
            print(f"加载游戏结果UI图片失败: {e}")
    
    def show(self, is_victory=True, current_map=None):
        """显示游戏结果界面
        
        Args:
            is_victory: 是否为胜利
            current_map: 当前地图名称
        """
        
        self.is_active = True
        self.is_victory = is_victory
        self.current_time = 0.0
        self.show_buttons = False
        self.current_map = current_map
        
        # 确定下一关地图
        self._determine_next_map()
        
        # 播放相应的音效
        if is_victory:
            resource_manager.play_sound("victory")
        else:
            resource_manager.play_sound("defeat")
    
    def _determine_next_map(self):
        """确定下一关地图"""
        if not self.is_victory or not self.current_map:
            self.next_map = None
            self.is_final_level = False
            return
        
        # 关卡进阶逻辑
        if self.current_map == "small_map":
            self.next_map = "test2_map"
            self.is_final_level = False
        elif self.current_map == "test2_map":
            self.next_map = "test3_map"
            self.is_final_level = False
        elif self.current_map == "test3_map":
            self.next_map = None
            self.is_final_level = True
        else:
            # 其他地图不进行关卡进阶
            self.next_map = None
            self.is_final_level = False
        
        
    
    def update(self, dt):
        """更新游戏结果UI"""
        if not self.is_active:
            return
        
        self.current_time += dt
        
        # 5秒后显示按钮
        if self.current_time >= self.display_time and not self.show_buttons:
            self.show_buttons = True
            
        
        # 更新鼠标悬停状态（在render中处理，因为button_rects在render时才创建）
        pass
    
    def handle_event(self, event):
        """处理事件"""
        if not self.is_active or not self.show_buttons:
            return None
        
        
        
        # 键盘控制
        if event.type == pygame.KEYDOWN:
            if event.key in [pygame.K_UP, pygame.K_w]:
                self.selected_button = (self.selected_button - 1) % 2
                
                return None
            elif event.key in [pygame.K_DOWN, pygame.K_s]:
                self.selected_button = (self.selected_button + 1) % 2
                
                return None
            elif event.key in [pygame.K_RETURN, pygame.K_SPACE]:
                result = self._get_button_action(self.selected_button)
                
                return result
        
        # 鼠标控制
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = pygame.mouse.get_pos()
            
            
            for button_name, rect in self.button_rects.items():
                
                if rect.collidepoint(mouse_pos):
                    result = self._get_button_action(button_name)
                    
                    return result
                
            
            
        
        return None
    
    def _get_button_action(self, button):
        """获取按钮动作"""
        if isinstance(button, int):
            if button == 0:
                return "restart"
            elif button == 1:
                return "main_menu"
        else:
            if button == "again":
                return "restart"
            elif button == "next_level":
                return "next_level"
            elif button == "home":
                return "main_menu"
        return None
    
    def render(self):
        """渲染游戏结果UI"""
        if not self.is_active:
            return
        
        # 创建半透明覆盖层
        overlay = pygame.Surface((self.screen.get_width(), self.screen.get_height()))
        overlay.set_alpha(128)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))
        
        # 选择要显示的图片
        image = self.win_image if self.is_victory else self.lost_image
        
        if image:
                    # 计算图片位置（居中显示，向右移动70像素）
            image_rect = image.get_rect()
            image_rect.center = (self.screen.get_width() // 2 + 60, self.screen.get_height() // 2-20)
            self.screen.blit(image, image_rect)
        else:
            # 如果图片加载失败，显示文字
            font = pygame.font.SysFont('simHei', 72)
            if self.is_victory:
                text = font.render("胜利！", True, (255, 215, 0))  # 金色
            else:
                text = font.render("失败！", True, (255, 0, 0))  # 红色
            
            text_rect = text.get_rect(center=(self.screen.get_width() // 2 + 70, self.screen.get_height() // 2))
            self.screen.blit(text, text_rect)
        
        # 渲染按钮弹窗
        if self.show_buttons:
            self._render_button_popup()
    
    def _render_button_popup(self):
        """渲染按钮弹窗"""
        # 清空按钮矩形
        self.button_rects.clear()
        
        # 弹窗尺寸和位置
        popup_width = 400
        popup_height = 400
        popup_x = (self.screen.get_width() - popup_width) // 2
        popup_y = (self.screen.get_height() - popup_height) // 2
        
        # 绘制弹窗背景
        popup_rect = pygame.Rect(popup_x, popup_y, popup_width, popup_height)
        pygame.draw.rect(self.screen, (50, 50, 50), popup_rect)
        pygame.draw.rect(self.screen, (100, 100, 100), popup_rect, 3)
        
        # 按钮尺寸和间距
        button_width = 300
        button_height = 150
        button_spacing = 33
        
        # 计算按钮起始位置（在弹窗内居中）
        button_start_x = popup_x + (popup_width - button_width) // 2
        button_start_y = popup_y + 50  # 距离弹窗顶部50像素
        
        # 更新鼠标悬停状态
        mouse_pos = pygame.mouse.get_pos()
        self.hovered_button = None
        
        # 根据关卡状态确定按钮
       
        
        if self.is_victory and self.is_final_level:
            # 胜利且是最终关卡：显示重新开始和回到主页按钮
            button_images = [self.again_image, self.home_image]
            button_names = ["again", "home"]
            
        elif self.is_victory and self.next_map and not self.is_final_level:
            # 胜利且有下一关：不显示按钮，直接进入下一关
            button_images = []
            button_names = []
           
        else:
            # 失败或其他情况：显示重新开始和回到主页按钮
            button_images = [self.again_image, self.home_image]
            button_names = ["again", "home"]
            
        
        for i, (button_img, button_name) in enumerate(zip(button_images, button_names)):
            button_y = button_start_y + i * (button_height + button_spacing)
            
            if button_img:
                # 统一缩放所有按钮到相同尺寸
                scaled_button = pygame.transform.scale(button_img, (button_width, button_height))
                button_rect = scaled_button.get_rect(center=(button_start_x + button_width // 2, button_y + button_height // 2))
               
                
                # 检查鼠标悬停（仅用于调试，不进行高亮）
                if button_rect.collidepoint(mouse_pos):
                    self.hovered_button = button_name
                    
                
                # 统一使用普通渲染，不进行高亮
                self.screen.blit(scaled_button, button_rect)
                self.button_rects[button_name] = button_rect
                
            else:
                # 如果图片加载失败，创建默认按钮
                button_rect = pygame.Rect(button_start_x, button_y, button_width, button_height)
                
                # 检查鼠标悬停（仅用于调试，不进行高亮）
                if button_rect.collidepoint(mouse_pos):
                    self.hovered_button = button_name
                    
                # 统一使用灰色背景，不进行高亮
                pygame.draw.rect(self.screen, (100, 100, 100), button_rect)  # 灰色
                pygame.draw.rect(self.screen, (255, 255, 255), button_rect, 2)
                
                # 添加文字
                font = pygame.font.SysFont('simHei', 24)
                if button_name == "again":
                    text = "重新开始"
                elif button_name == "next_level":
                    text = "下一关"
                elif button_name == "home":
                    text = "回到主页"
                
                text_surface = font.render(text, True, (255, 255, 255))
                text_rect = text_surface.get_rect(center=button_rect.center)
                self.screen.blit(text_surface, text_rect)
                self.button_rects[button_name] = button_rect
               
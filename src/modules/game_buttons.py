import pygame
from .resource_manager import resource_manager

class GameButtons:
    """游戏战斗界面的按钮管理器"""
    
    def __init__(self, screen, game=None):
        self.screen = screen
        self.game = game  # 添加对游戏实例的引用
        self.buttons = {}
        self.button_rects = {}
        self.confirmation_active = False
        self.confirmation_type = None
        self.confirmation_timer = 0
        self.mouse_restriction_disabled = False  # 标记鼠标限制是否被禁用
        
        # 按钮位置（左侧，经验条下方）
        self.button_size = 40
        self.button_margin = 10
        self.start_x = 30  # 距离左边50像素
        self.start_y = 150  # 经验条下方
        
        # 加载按钮图片
        self._load_buttons()
        
    def _load_buttons(self):
        """加载按钮图片"""
        try:
            # 加载按钮图片
            pause_img = resource_manager.load_image('pause_button', 'images/ui/pause.png')
            restart_img = resource_manager.load_image('restart_button', 'images/ui/restart.png')
            home_img = resource_manager.load_image('home_button', 'images/ui/home.png')
            setup_img = resource_manager.load_image('setup_button', 'images/ui/setup.png')
            
            print(f"按钮图片加载状态: pause={pause_img is not None}, restart={restart_img is not None}, home={home_img is not None}, setup={setup_img is not None}")
            
            # 检查每个图片是否成功加载
            if pause_img is None or restart_img is None or home_img is None or setup_img is None:
                print("某些按钮图片加载失败，创建默认按钮")
                # 创建默认的彩色按钮
                self.buttons = {
                    'pause': self._create_default_button('暂停', (255, 0, 0)),
                    'restart': self._create_default_button('重启', (0, 255, 0)),
                    'home': self._create_default_button('主页', (0, 0, 255)),
                    'setup': self._create_default_button('设置', (255, 255, 0))
                }
            else:
                # 调整按钮大小
                self.buttons = {
                    'pause': pygame.transform.scale(pause_img, (self.button_size, self.button_size)),
                    'restart': pygame.transform.scale(restart_img, (self.button_size, self.button_size)),
                    'home': pygame.transform.scale(home_img, (self.button_size, self.button_size)),
                    'setup': pygame.transform.scale(setup_img, (self.button_size, self.button_size))
                }
            print(f"成功加载 {len(self.buttons)} 个按钮")
        except Exception as e:
            print(f"加载游戏按钮图片失败: {e}")
            # 创建默认按钮
            self.buttons = {
                'pause': self._create_default_button('暂停', (255, 0, 0)),
                'restart': self._create_default_button('重启', (0, 255, 0)),
                'home': self._create_default_button('主页', (0, 0, 255)),
                'setup': self._create_default_button('设置', (255, 255, 0))
            }
    
    def _create_default_button(self, text, color):
        """创建默认按钮"""
        button_surface = pygame.Surface((self.button_size, self.button_size))
        button_surface.fill(color)
        
        # 添加边框
        pygame.draw.rect(button_surface, (255, 255, 255), (0, 0, self.button_size, self.button_size), 2)
        
        # 添加文字
        font = pygame.font.SysFont('simHei', 12)
        text_surface = font.render(text, True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=(self.button_size // 2, self.button_size // 2))
        button_surface.blit(text_surface, text_rect)
        
        return button_surface
    
    def handle_event(self, event):
        """处理按钮事件"""
        if self.confirmation_active:
            return self._handle_confirmation(event)
        
        # 处理键盘事件（7890键）
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_7:
                return self._handle_button_click('pause')
            elif event.key == pygame.K_8:
                return self._handle_button_click('restart')
            elif event.key == pygame.K_9:
                return self._handle_button_click('home')
            elif event.key == pygame.K_0:
                return self._handle_button_click('setup')
        
        # 保留鼠标事件作为备选
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = pygame.mouse.get_pos()
            for button_name, rect in self.button_rects.items():
                if rect.collidepoint(mouse_pos):
                    return self._handle_button_click(button_name)
        return None
    
    def _handle_button_click(self, button_name):
        """处理按钮点击"""
        if button_name == 'pause':
            return 'pause'
        elif button_name == 'restart':
            self.confirmation_active = True
            self.confirmation_type = 'restart'
            pygame.mouse.set_visible(True)  # 显示鼠标光标
            # 临时禁用鼠标限制
            self._disable_mouse_restriction()
            return 'confirm_restart'
        elif button_name == 'home':
            self.confirmation_active = True
            self.confirmation_type = 'home'
            pygame.mouse.set_visible(True)  # 显示鼠标光标
            # 临时禁用鼠标限制
            self._disable_mouse_restriction()
            return 'confirm_home'
        elif button_name == 'setup':
            return 'setup'
        return None
    
    def _handle_confirmation(self, event):
        """处理确认对话框"""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = pygame.mouse.get_pos()
            if hasattr(self, 'confirmation_buttons'):
                for button_name, button_rect in self.confirmation_buttons.items():
                    if button_rect.collidepoint(mouse_pos):
                        if button_name == 'yes':
                            # 确认操作
                            if self.confirmation_type == 'restart':
                                self.confirmation_active = False
                                pygame.mouse.set_visible(False)  # 隐藏鼠标光标
                                self._restore_mouse_restriction()  # 恢复鼠标限制
                                return 'restart_confirmed'
                            elif self.confirmation_type == 'home':
                                self.confirmation_active = False
                                pygame.mouse.set_visible(False)  # 隐藏鼠标光标
                                self._restore_mouse_restriction()  # 恢复鼠标限制
                                return 'home_confirmed'
                        elif button_name == 'no':
                            # 取消操作
                            self.confirmation_active = False
                            self.confirmation_type = None
                            pygame.mouse.set_visible(False)  # 隐藏鼠标光标
                            self._restore_mouse_restriction()  # 恢复鼠标限制
                        return None
        
        # 保留键盘支持
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_y:
                # 确认操作
                if self.confirmation_type == 'restart':
                    self.confirmation_active = False
                    pygame.mouse.set_visible(False)  # 隐藏鼠标光标
                    self._restore_mouse_restriction()  # 恢复鼠标限制
                    return 'restart_confirmed'
                elif self.confirmation_type == 'home':
                    self.confirmation_active = False
                    pygame.mouse.set_visible(False)  # 隐藏鼠标光标
                    self._restore_mouse_restriction()  # 恢复鼠标限制
                    return 'home_confirmed'
            elif event.key == pygame.K_n or event.key == pygame.K_ESCAPE:
                # 取消操作
                self.confirmation_active = False
                self.confirmation_type = None
                pygame.mouse.set_visible(False)  # 隐藏鼠标光标
                self._restore_mouse_restriction()  # 恢复鼠标限制
        return None
    
    def update(self, dt):
        """更新确认对话框"""
        # 移除倒计时功能，对话框会一直显示直到用户选择
        pass
    
    def render(self):
        """渲染按钮"""
        # 清空按钮矩形
        self.button_rects.clear()
        
        # 按钮对应的键盘键
        key_mapping = {
            'pause': '7',
            'restart': '8', 
            'home': '9',
            'setup': '0'
        }
        
        # 绘制按钮
        x = self.start_x
        for i, (button_name, button_img) in enumerate(self.buttons.items()):
            button_rect = button_img.get_rect()
            button_rect.topleft = (x, self.start_y)
            self.screen.blit(button_img, button_rect)
            self.button_rects[button_name] = button_rect
            
            # 在按钮下方显示键盘提示
            font = pygame.font.SysFont('simHei', 12)
            key_text = key_mapping.get(button_name, '')
            if key_text:
                text_surface = font.render(key_text, True, (255, 255, 255))
                text_rect = text_surface.get_rect()
                text_rect.centerx = button_rect.centerx
                text_rect.top = button_rect.bottom + 2
                self.screen.blit(text_surface, text_rect)
            
            x += self.button_size + self.button_margin
        
        # 如果确认对话框激活，绘制确认提示
        if self.confirmation_active:
            self._render_confirmation()
    
    def _render_confirmation(self):
        """渲染确认对话框"""
        # 创建半透明背景
        overlay = pygame.Surface((self.screen.get_width(), self.screen.get_height()))
        overlay.set_alpha(128)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))
        
        # 创建确认对话框
        dialog_width = 400
        dialog_height = 250
        dialog_x = (self.screen.get_width() - dialog_width) // 2
        dialog_y = (self.screen.get_height() - dialog_height) // 2
        
        # 绘制对话框背景
        dialog_rect = pygame.Rect(dialog_x, dialog_y, dialog_width, dialog_height)
        pygame.draw.rect(self.screen, (50, 50, 50), dialog_rect)
        pygame.draw.rect(self.screen, (100, 100, 100), dialog_rect, 3)
        
        # 绘制确认文本
        font = pygame.font.SysFont('simHei', 24)
        if self.confirmation_type == 'restart':
            text = "确定要重新开始游戏吗？"
        else:
            text = "确定要返回主菜单吗？"
        
        text_surface = font.render(text, True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=(dialog_x + dialog_width // 2, dialog_y + 60))
        self.screen.blit(text_surface, text_rect)
        
        # 绘制键盘提示
        key_font = pygame.font.SysFont('simHei', 18)
        key_text = "按 Y 确认，按 N 取消"
        key_surface = key_font.render(key_text, True, (200, 200, 200))
        key_rect = key_surface.get_rect(center=(dialog_x + dialog_width // 2, dialog_y + 120))
        self.screen.blit(key_surface, key_rect)
        
        # 绘制按钮
        button_width = 80
        button_height = 40
        button_y = dialog_y + 150
        
        # 是按钮（紫色）
        yes_button_rect = pygame.Rect(dialog_x +80 , button_y, button_width, button_height)
        pygame.draw.rect(self.screen, (128, 0, 128), yes_button_rect)  # 紫色
        pygame.draw.rect(self.screen, (255, 255, 255), yes_button_rect, 2)
        yes_text = font.render("是", True, (255, 255, 255))
        yes_text_rect = yes_text.get_rect(center=yes_button_rect.center)
        self.screen.blit(yes_text, yes_text_rect)
        
        # 否按钮
        no_button_rect = pygame.Rect(dialog_x + 240, button_y, button_width, button_height)
        pygame.draw.rect(self.screen, (255, 0, 0), no_button_rect)
        pygame.draw.rect(self.screen, (255, 255, 255), no_button_rect, 2)
        no_text = font.render("否", True, (255, 255, 255))
        no_text_rect = no_text.get_rect(center=no_button_rect.center)
        self.screen.blit(no_text, no_text_rect)
        
        # 保存按钮矩形用于点击检测
        self.confirmation_buttons = {
            'yes': yes_button_rect,
            'no': no_button_rect
        }
    
    def _disable_mouse_restriction(self):
        """临时禁用鼠标限制"""
        self.mouse_restriction_disabled = True
        # 通知双人系统禁用鼠标限制
        if self.game and hasattr(self.game, 'dual_player_system') and self.game.dual_player_system:
            self.game.dual_player_system.disable_mouse_restriction()
    
    def _restore_mouse_restriction(self):
        """恢复鼠标限制"""
        self.mouse_restriction_disabled = False
        # 通知双人系统恢复鼠标限制
        if self.game and hasattr(self.game, 'dual_player_system') and self.game.dual_player_system:
            self.game.dual_player_system.restore_mouse_restriction() 
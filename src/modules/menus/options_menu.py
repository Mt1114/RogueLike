import pygame
from ..resource_manager import resource_manager
from ..utils import FontManager

class OptionsMenu:
    def __init__(self, screen):
        self.screen = screen
        self.is_active = False
        self.current_image_index = 0
        self.total_images = 12
        
        # 加载所有详情图片
        self.detail_images = []
        self._load_detail_images()
        
        # 字体设置
        self.font = FontManager.get_font(36)
        self.small_font = FontManager.get_font(24)
        
        # 颜色设置
        self.text_color = (255, 255, 255)
        self.background_color = (0, 0, 0, 180)
        
        # 计算屏幕中心
        self.screen_center_x = self.screen.get_width() // 2
        self.screen_center_y = self.screen.get_height() // 2
        
    def _load_detail_images(self):
        """加载所有详情图片"""
        for i in range(1, self.total_images + 1):
            try:
                image_path = f'images/details/{i}.jpg'
                image = resource_manager.load_image(f'detail_{i}', image_path)
                if image:
                    # 调整图片大小以适应屏幕
                    screen_width = self.screen.get_width()
                    screen_height = self.screen.get_height()
                    
                    # 计算缩放比例，保持宽高比
                    img_width, img_height = image.get_size()
                    scale_x = screen_width * 0.8 / img_width
                    scale_y = screen_height * 0.8 / img_height
                    scale = min(scale_x, scale_y)
                    
                    new_width = int(img_width * scale)
                    new_height = int(img_height * scale)
                    
                    scaled_image = pygame.transform.scale(image, (new_width, new_height))
                    self.detail_images.append(scaled_image)
                else:
                    print(f"无法加载图片: {image_path}")
                    # 创建一个占位符图片
                    placeholder = pygame.Surface((400, 300))
                    placeholder.fill((100, 100, 100))
                    self.detail_images.append(placeholder)
            except Exception as e:
                print(f"加载图片 {i} 时出错: {e}")
                # 创建一个占位符图片
                placeholder = pygame.Surface((400, 300))
                placeholder.fill((100, 100, 100))
                self.detail_images.append(placeholder)
    
    def show(self):
        """显示选项菜单"""
        self.is_active = True
        self.current_image_index = 0
    
    def hide(self):
        """隐藏选项菜单"""
        self.is_active = False
    
    def handle_event(self, event):
        """处理输入事件"""
        if not self.is_active:
            return None
            
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # 左键点击
                # 到下一张图
                if self.current_image_index < self.total_images - 1:
                    self.current_image_index += 1
                    resource_manager.play_sound("menu_move")
                else:
                    # 第12张图左键点击返回目录
                    self.hide()
                    resource_manager.play_sound("menu_select")
                    return "back_to_main"
            elif event.button == 3:  # 右键点击
                # 返回上一张图
                if self.current_image_index > 0:
                    self.current_image_index -= 1
                    resource_manager.play_sound("menu_move")
                else:
                    # 第一张图右键点击返回目录
                    self.hide()
                    resource_manager.play_sound("menu_select")
                    return "back_to_main"
        
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT or event.key == pygame.K_a:
                # 返回上一张图
                if self.current_image_index > 0:
                    self.current_image_index -= 1
                    resource_manager.play_sound("menu_move")
                else:
                    # 第一张图按左键返回目录
                    self.hide()
                    resource_manager.play_sound("menu_select")
                    return "back_to_main"
            elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                # 到下一张图
                if self.current_image_index < self.total_images - 1:
                    self.current_image_index += 1
                    resource_manager.play_sound("menu_move")
                else:
                    # 第12张图按右键返回目录
                    self.hide()
                    resource_manager.play_sound("menu_select")
                    return "back_to_main"
            elif event.key == pygame.K_ESCAPE:
                # ESC键返回目录
                self.hide()
                resource_manager.play_sound("menu_select")
                return "back_to_main"
        
        return None
    
    def render(self):
        """渲染选项菜单"""
        if not self.is_active or self.current_image_index >= len(self.detail_images):
            return
        
        # 绘制半透明背景
        overlay = pygame.Surface(self.screen.get_size())
        overlay.set_alpha(180)
        overlay.fill(self.background_color)
        self.screen.blit(overlay, (0, 0))
        
        # 获取当前图片
        current_image = self.detail_images[self.current_image_index]
        
        # 计算图片位置（居中显示）
        image_rect = current_image.get_rect()
        image_rect.center = (self.screen_center_x, self.screen_center_y)
        
        # 绘制图片
        self.screen.blit(current_image, image_rect)
        
        # 绘制页码信息
        page_text = f"{self.current_image_index + 1} / {self.total_images}"
        page_surface = self.font.render(page_text, True, self.text_color)
        page_rect = page_surface.get_rect()
        page_rect.centerx = self.screen_center_x
        page_rect.y = 50
        
        # 绘制页码背景
        page_bg_rect = page_rect.inflate(20, 10)
        pygame.draw.rect(self.screen, (0, 0, 0, 128), page_bg_rect)
        pygame.draw.rect(self.screen, (255, 255, 255), page_bg_rect, 2)
        
        self.screen.blit(page_surface, page_rect)
        
        # 绘制操作提示
        if self.current_image_index == 0:
            # 第一张图
            hint_text = "左键：下一张 | 右键：返回目录"
        elif self.current_image_index == self.total_images - 1:
            # 最后一张图
            hint_text = "左键：返回目录 | 右键：上一张"
        else:
            # 中间的图片
            hint_text = "左键：下一张 | 右键：上一张"
        
        hint_surface = self.small_font.render(hint_text, True, self.text_color)
        hint_rect = hint_surface.get_rect()
        hint_rect.centerx = self.screen_center_x
        hint_rect.y = self.screen.get_height() - 80
        
        # 绘制提示背景
        hint_bg_rect = hint_rect.inflate(20, 10)
        pygame.draw.rect(self.screen, (0, 0, 0, 128), hint_bg_rect)
        pygame.draw.rect(self.screen, (255, 255, 255), hint_bg_rect, 2)
        
        self.screen.blit(hint_surface, hint_rect)

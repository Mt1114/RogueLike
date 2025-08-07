import pygame
import math
from ..resource_manager import resource_manager

class AttackEffect:
    """攻击特效类"""
    
    def __init__(self, image_path, frame_width=64, frame_height=64, frame_count=10):
        """
        初始化攻击特效
        
        Args:
            image_path: 特效图片路径
            frame_width: 单帧宽度
            frame_height: 单帧高度
            frame_count: 总帧数
        """
        self.image_path = image_path
        self.frame_width = frame_width
        self.frame_height = frame_height
        self.frame_count = frame_count
        
        # 加载并分割图片
        self.frames = self._load_and_split_frames()
        
        # 动画状态
        self.is_playing = False
        self.current_frame = 0
        self.animation_timer = 0
        self.frame_duration = 0.03  # 每帧持续时间（秒）
        self.total_duration = self.frame_duration * frame_count
        
        # 特效位置和方向
        self.x = 0
        self.y = 0
        self.direction_x = 0
        self.direction_y = 0
        
    def _load_and_split_frames(self):
        """加载图片并分割成帧"""
        try:
            # 加载原始图片
            original_image = resource_manager.load_image('attack_effect', self.image_path)
            if not original_image:
                print(f"警告：无法加载攻击特效图片: {self.image_path}")
                return []
            
            frames = []
            # 分割图片为多个帧
            for i in range(self.frame_count):
                # 计算当前帧在原始图片中的位置
                frame_x = i * self.frame_width
                frame_y = 0
                
                # 提取当前帧
                frame_rect = pygame.Rect(frame_x, frame_y, self.frame_width, self.frame_height)
                frame = original_image.subsurface(frame_rect)
                frames.append(frame)
            
            return frames
        except Exception as e:
            print(f"错误：分割攻击特效图片失败: {e}")
            return []
    
    def play(self, x, y, direction_x, direction_y):
        """
        播放攻击特效
        
        Args:
            x: 特效X坐标
            y: 特效Y坐标
            direction_x: 方向X分量
            direction_y: 方向Y分量
        """
        self.is_playing = True
        self.current_frame = 0
        self.animation_timer = 0
        self.x = x
        self.y = y
        self.direction_x = direction_x
        self.direction_y = direction_y
    
    def update(self, dt):
        """更新特效动画"""
        if not self.is_playing or not self.frames:
            return
        
        self.animation_timer += dt
        
        # 更新当前帧
        frame_index = int(self.animation_timer / self.frame_duration)
        if frame_index >= self.frame_count:
            # 动画结束
            self.is_playing = False
            return
        
        self.current_frame = min(frame_index, len(self.frames) - 1)
    
    def render(self, screen, camera_x=0, camera_y=0, player_x=None, player_y=None):
        """渲染特效"""
        if not self.is_playing or not self.frames or self.current_frame >= len(self.frames):
            return
        
        # 获取当前帧
        current_frame = self.frames[self.current_frame]
        
        # 如果提供了玩家位置，使用玩家当前位置；否则使用特效的固定位置
        if player_x is not None and player_y is not None:
            # 使用玩家当前位置
            screen_x = player_x - camera_x + screen.get_width() // 2
            screen_y = player_y - camera_y + screen.get_height() // 2
        else:
            # 使用特效的固定位置
            screen_x = self.x - camera_x + screen.get_width() // 2
            screen_y = self.y - camera_y + screen.get_height() // 2
        
        # 计算旋转角度（和枪的旋转逻辑一样）
        angle = math.degrees(math.atan2(-self.direction_y, self.direction_x))
        
        # 旋转特效图像
        rotated_frame = pygame.transform.rotate(current_frame, angle)
        
        # 渲染特效
        frame_rect = rotated_frame.get_rect()
        frame_rect.center = (screen_x, screen_y)
        screen.blit(rotated_frame, frame_rect)
    
    def is_finished(self):
        """检查特效是否播放完毕"""
        return not self.is_playing

class AttackEffectManager:
    """攻击特效管理器"""
    
    def __init__(self):
        self.effects = []
        
        # 预加载攻击特效
        self.knife_effect = AttackEffect(
            'images/attcak/hit_animations/swing02.png',
            frame_width=64,
            frame_height=64,
            frame_count=10
        )
    
    def create_knife_effect(self, x, y, direction_x, direction_y):
        """创建刀攻击特效"""
        effect = AttackEffect(
            'images/attcak/hit_animations/swing02.png',
            frame_width=64,
            frame_height=64,
            frame_count=10
        )
        effect.play(x, y, direction_x, direction_y)
        self.effects.append(effect)
    
    def update(self, dt):
        """更新所有特效"""
        # 更新特效
        for effect in self.effects[:]:
            effect.update(dt)
            if effect.is_finished():
                self.effects.remove(effect)
    
    def render(self, screen, camera_x=0, camera_y=0):
        """渲染所有特效"""
        for effect in self.effects:
            effect.render(screen, camera_x, camera_y) 
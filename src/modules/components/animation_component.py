"""
动画组件
负责管理实体的动画状态和渲染
"""

import pygame
import os
from .base_component import Component

class AnimationComponent(Component):
    """动画组件，处理实体的动画逻辑"""
    
    def __init__(self, owner, animation_data=None):
        """
        初始化动画组件
        
        Args:
            owner: 组件所属的实体
            animation_data: 动画数据字典，格式为 {
                'idle': {'sprite_sheet': 'path', 'frame_count': 11, 'frame_duration': 0.03},
                'run': {...},
                ...
            }
        """
        super().__init__(owner)
        
        # 动画集合
        self.animations = {}
        
        # 当前动画状态
        self.current_animation = 'idle'
        self.current_image = None
        
        # 闪烁效果（用于无敌状态等）
        self.blink_interval = 0.1
        self.blink_timer = 0
        self.visible = True
        self.blinking = False
        
        # 加载动画数据
        if animation_data:
            self.load_animations(animation_data)
    
    def load_animations(self, animation_data):
        """
        加载动画数据
        
        Args:
            animation_data: 动画数据字典
        """
        from ..resource_manager import resource_manager
        
        for anim_name, anim_info in animation_data.items():
            # 检查是否使用单独的帧文件
            if anim_info.get('use_sprite_sheet', True) == False:
                # 使用单独的帧文件
                self._load_separate_frames(anim_name, anim_info)
            else:
                # 使用精灵表
                sprite_sheet = resource_manager.load_spritesheet(
                    f"{anim_name}_sprite", 
                    anim_info['sprite_sheet']
                )
                
                self.animations[anim_name] = resource_manager.create_animation(
                    f"{anim_name}_anim",
                    sprite_sheet,
                    frame_width=anim_info.get('frame_width', 32),
                    frame_height=anim_info.get('frame_height', 32),
                    frame_count=anim_info.get('frame_count', 1),
                    row=anim_info.get('row', 0),
                    col=anim_info.get('col', 0),
                    frame_duration=anim_info.get('frame_duration', 0.1)
                )
    
    def _load_separate_frames(self, anim_name, anim_info):
        """
        加载单独的帧文件
        
        Args:
            anim_name: 动画名称
            anim_info: 动画信息
        """
        from ..resource_manager import resource_manager
        
        frames = []
        frame_count = anim_info.get('frame_count', 1)
        base_path = anim_info['sprite_sheet']
        
        # 获取基础路径（去掉文件名）
        base_dir = os.path.dirname(base_path)
        base_name = os.path.splitext(os.path.basename(base_path))[0]
        
        # 加载所有帧
        for i in range(1, frame_count + 1):
            frame_path = os.path.join(base_dir, f"{base_name}_{i:02d}.png")
            try:
                frame = resource_manager.load_image(f"{anim_name}_frame_{i}", frame_path)
                frames.append(frame)
            except:
                print(f"无法加载帧文件: {frame_path}")
                # 如果加载失败，使用第一帧作为替代
                if i == 1:
                    frame = resource_manager.load_image(f"{anim_name}_frame_{i}", base_path)
                    frames.append(frame)
                else:
                    frames.append(frames[0])  # 使用第一帧作为替代
        
        # 创建动画
        from ..resource_manager import Animation
        self.animations[anim_name] = Animation(
            frames=frames,
            frame_duration=anim_info.get('frame_duration', 0.1),
            loop=True
        )
    
    def set_animation(self, animation_name):
        """
        设置当前动画
        
        Args:
            animation_name: 动画名称
        
        Returns:
            bool: 如果动画改变成功返回True，否则返回False
        """
        if animation_name in self.animations and animation_name != self.current_animation:
            self.current_animation = animation_name
            self.animations[animation_name].reset()
            return True
        return False
    
    def update(self, dt):
        """
        更新动画状态
        
        Args:
            dt: 时间增量（秒）
        """
        if not self.enabled:
            return
            
        # 更新当前动画
        if self.current_animation in self.animations:
            self.animations[self.current_animation].update(dt)
            
        # 更新闪烁效果
        if self.blinking:
            self.blink_timer -= dt
            
            # 更新闪烁状态
            if self.blink_timer <= 0:
                self.visible = not self.visible
                self.blink_timer = self.blink_interval
    
    def get_current_frame(self, flip_x=False):
        """
        获取当前动画帧
        
        Args:
            flip_x: 是否水平翻转图像
            
        Returns:
            Surface: 当前动画帧图像
        """
        if self.current_animation in self.animations:
            current_frame = self.animations[self.current_animation].get_current_frame()
            
            # 根据朝向翻转图像
            if flip_x:
                current_frame = pygame.transform.flip(current_frame, True, False)
                
            return current_frame
            
        return None
    
    def render(self, screen, rect):
        """
        渲染当前动画帧
        
        Args:
            screen: 目标Surface
            rect: 目标位置矩形
        """
        if not self.enabled or (self.blinking and not self.visible):
            return
            
        current_frame = self.get_current_frame()
        if current_frame:
            screen.blit(current_frame, rect)
    
    def start_blinking(self, duration, interval=0.1):
        """
        开始闪烁效果
        
        Args:
            duration: 闪烁持续时间（秒）
            interval: 闪烁间隔（秒）
        """
        self.blinking = True
        self.blink_interval = interval
        self.blink_timer = interval
        self.visible = True
        
        # 设置定时器在指定时间后关闭闪烁
        def stop_blinking():
            self.blinking = False
            self.visible = True
            
        # TODO: 实现定时器功能，或者在上层逻辑中手动关闭闪烁效果
    
    def stop_blinking(self):
        """停止闪烁效果"""
        self.blinking = False
        self.visible = True 
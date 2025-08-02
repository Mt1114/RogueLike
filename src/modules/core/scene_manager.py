"""
场景管理器
负责管理不同场景之间的切换和生命周期
"""

from typing import Dict, Optional, Type
from abc import ABC, abstractmethod
import pygame


class Scene(ABC):
    """场景基类"""
    
    def __init__(self, scene_manager: 'SceneManager'):
        self.scene_manager = scene_manager
        self.screen = scene_manager.screen
        self.game_state = scene_manager.game_state
        self.is_active = False
        
    @abstractmethod
    def handle_event(self, event: pygame.event.Event):
        """处理事件"""
        pass
        
    @abstractmethod
    def update(self, dt: float):
        """更新场景"""
        pass
        
    @abstractmethod
    def render(self, screen: pygame.Surface):
        """渲染场景"""
        pass
        
    def on_enter(self):
        """进入场景时调用"""
        self.is_active = True
        
    def on_exit(self):
        """退出场景时调用"""
        self.is_active = False
        
    def on_pause(self):
        """暂停场景时调用"""
        pass
        
    def on_resume(self):
        """恢复场景时调用"""
        pass


class SceneManager:
    """场景管理器"""
    
    def __init__(self, screen: pygame.Surface, game_state):
        self.screen = screen
        self.game_state = game_state
        self.scenes: Dict[str, Scene] = {}
        self.current_scene: Optional[Scene] = None
        self.scene_stack = []  # 场景栈，用于返回功能
        
    def register_scene(self, scene_name: str, scene: Scene):
        """注册场景"""
        self.scenes[scene_name] = scene
        
    def switch_scene(self, scene_name: str):
        """切换场景"""
        if scene_name not in self.scenes:
            print(f"场景 {scene_name} 不存在")
            return
            
        # 退出当前场景
        if self.current_scene:
            self.current_scene.on_exit()
            
        # 保存当前场景到栈中
        if self.current_scene:
            self.scene_stack.append(self.current_scene)
            
        # 切换到新场景
        self.current_scene = self.scenes[scene_name]
        self.current_scene.on_enter()
        
        # 更新游戏状态
        self.game_state.current_scene = scene_name
        if self.scene_stack:
            self.game_state.previous_scene = self.scene_stack[-1].__class__.__name__
            
    def push_scene(self, scene_name: str):
        """推入场景（不退出当前场景）"""
        if scene_name not in self.scenes:
            print(f"场景 {scene_name} 不存在")
            return
            
        # 暂停当前场景
        if self.current_scene:
            self.current_scene.on_pause()
            self.scene_stack.append(self.current_scene)
            
        # 推入新场景
        self.current_scene = self.scenes[scene_name]
        self.current_scene.on_enter()
        
    def pop_scene(self):
        """弹出场景（返回上一个场景）"""
        if not self.scene_stack:
            print("没有可返回的场景")
            return
            
        # 退出当前场景
        if self.current_scene:
            self.current_scene.on_exit()
            
        # 恢复上一个场景
        self.current_scene = self.scene_stack.pop()
        self.current_scene.on_resume()
        
    def handle_event(self, event: pygame.event.Event):
        """处理事件"""
        if self.current_scene:
            self.current_scene.handle_event(event)
            
    def update(self, dt: float):
        """更新当前场景"""
        if self.current_scene:
            self.current_scene.update(dt)
            
    def render(self, screen: pygame.Surface):
        """渲染当前场景"""
        if self.current_scene:
            self.current_scene.render(screen)
            
    def get_current_scene_name(self) -> Optional[str]:
        """获取当前场景名称"""
        if self.current_scene:
            for name, scene in self.scenes.items():
                if scene == self.current_scene:
                    return name
        return None
        
    def has_scene(self, scene_name: str) -> bool:
        """检查场景是否存在"""
        return scene_name in self.scenes 
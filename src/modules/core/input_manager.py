"""
输入管理器
负责处理键盘、鼠标等输入事件，并提供统一的输入接口
"""

from typing import Dict, Set, Callable, Optional, Tuple
import pygame


class InputAction:
    """输入动作类"""
    
    def __init__(self, name: str, keys: list, mouse_buttons: list = None):
        self.name = name
        self.keys = set(keys) if keys else set()
        self.mouse_buttons = set(mouse_buttons) if mouse_buttons else set()
        self.pressed = False
        self.just_pressed = False
        self.just_released = False
        
    def update(self, pressed_keys: Set[int], mouse_buttons: Tuple[bool, bool, bool]):
        """更新动作状态"""
        was_pressed = self.pressed
        
        # 检查按键
        key_pressed = any(key in pressed_keys for key in self.keys)
        
        # 检查鼠标按钮
        mouse_pressed = any(mouse_buttons[i] for i in self.mouse_buttons)
        
        self.pressed = key_pressed or mouse_pressed
        self.just_pressed = self.pressed and not was_pressed
        self.just_released = not self.pressed and was_pressed


class InputManager:
    """输入管理器"""
    
    def __init__(self):
        self.actions: Dict[str, InputAction] = {}
        self.pressed_keys: Set[int] = set()
        self.mouse_buttons = (False, False, False)  # 左、中、右
        self.mouse_position = (0, 0)
        self.mouse_delta = (0, 0)  # 鼠标移动增量
        self.last_mouse_position = (0, 0)
        
        # 事件回调
        self.event_callbacks: Dict[int, list[Callable]] = {}
        
        # 默认输入映射
        self._setup_default_actions()
        
    def _setup_default_actions(self):
        """设置默认输入动作"""
        # 玩家1控制
        self.add_action("player1_move_up", [pygame.K_w])
        self.add_action("player1_move_down", [pygame.K_s])
        self.add_action("player1_move_left", [pygame.K_a])
        self.add_action("player1_move_right", [pygame.K_d])
        self.add_action("player1_attack", [pygame.K_SPACE])
        self.add_action("player1_melee", [pygame.BUTTONLEFT])
        self.add_action("player1_ranged", [pygame.BUTTONRIGHT])
        
        # 玩家2控制
        self.add_action("player2_move_up", [pygame.K_UP])
        self.add_action("player2_move_down", [pygame.K_DOWN])
        self.add_action("player2_move_left", [pygame.K_LEFT])
        self.add_action("player2_move_right", [pygame.K_RIGHT])
        self.add_action("player2_attack", [pygame.K_KP1])
        self.add_action("player2_melee", [pygame.K_KP2])
        
        # 通用控制
        self.add_action("pause", [pygame.K_ESCAPE])
        self.add_action("toggle_lighting", [pygame.K_b])
        self.add_action("debug_mode", [pygame.K_F1])
        
    def add_action(self, name: str, keys: list = None, mouse_buttons: list = None):
        """添加输入动作"""
        self.actions[name] = InputAction(name, keys, mouse_buttons)
        
    def remove_action(self, name: str):
        """移除输入动作"""
        if name in self.actions:
            del self.actions[name]
            
    def get_action(self, name: str) -> Optional[InputAction]:
        """获取输入动作"""
        return self.actions.get(name)
        
    def is_action_pressed(self, name: str) -> bool:
        """检查动作是否被按下"""
        action = self.get_action(name)
        return action.pressed if action else False
        
    def is_action_just_pressed(self, name: str) -> bool:
        """检查动作是否刚刚被按下"""
        action = self.get_action(name)
        return action.just_pressed if action else False
        
    def is_action_just_released(self, name: str) -> bool:
        """检查动作是否刚刚被释放"""
        action = self.get_action(name)
        return action.just_released if action else False
        
    def get_mouse_position(self) -> Tuple[int, int]:
        """获取鼠标位置"""
        return self.mouse_position
        
    def get_mouse_delta(self) -> Tuple[int, int]:
        """获取鼠标移动增量"""
        return self.mouse_delta
        
    def add_event_callback(self, event_type: int, callback: Callable):
        """添加事件回调"""
        if event_type not in self.event_callbacks:
            self.event_callbacks[event_type] = []
        self.event_callbacks[event_type].append(callback)
        
    def remove_event_callback(self, event_type: int, callback: Callable):
        """移除事件回调"""
        if event_type in self.event_callbacks:
            try:
                self.event_callbacks[event_type].remove(callback)
            except ValueError:
                pass
                
    def handle_event(self, event: pygame.event.Event):
        """处理事件"""
        # 更新按键状态
        if event.type == pygame.KEYDOWN:
            self.pressed_keys.add(event.key)
        elif event.type == pygame.KEYUP:
            self.pressed_keys.discard(event.key)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button <= 3:  # 左、中、右
                self.mouse_buttons = tuple(
                    i == event.button for i in range(1, 4)
                )
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button <= 3:
                self.mouse_buttons = tuple(
                    i != event.button for i in range(1, 4)
                )
        elif event.type == pygame.MOUSEMOTION:
            self.last_mouse_position = self.mouse_position
            self.mouse_position = event.pos
            self.mouse_delta = (
                self.mouse_position[0] - self.last_mouse_position[0],
                self.mouse_position[1] - self.last_mouse_position[1]
            )
            
        # 调用事件回调
        if event.type in self.event_callbacks:
            for callback in self.event_callbacks[event.type]:
                callback(event)
                
    def update(self):
        """更新输入状态"""
        # 更新所有动作的状态
        for action in self.actions.values():
            action.update(self.pressed_keys, self.mouse_buttons)
            
    def reset(self):
        """重置输入状态"""
        self.pressed_keys.clear()
        self.mouse_buttons = (False, False, False)
        self.mouse_delta = (0, 0)
        
        # 重置所有动作状态
        for action in self.actions.values():
            action.pressed = False
            action.just_pressed = False
            action.just_released = False 
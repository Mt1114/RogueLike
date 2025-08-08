"""
输入管理器
负责处理键盘、鼠标等输入事件，并提供统一的输入接口
"""

from typing import Dict, Set, Callable, Optional, Tuple, List
import pygame
import time

class InputAction:
    """输入动作类"""
    
    def __init__(self, name: str, keys: list, mouse_buttons: list = None):
        self.name = name
        self.keys = set(keys) if keys else set()
        self.mouse_buttons = set(mouse_buttons) if mouse_buttons else set()
        
        # 输入状态
        self.pressed = False
        self.just_pressed = False
        self.just_released = False
        
        # 防抖和状态跟踪
        self.last_press_time = 0
        self.last_release_time = 0
        self.debounce_time = 200  # 防抖时间(ms)
        self.release_guard_time = 300  # 释放后保护时间(ms)
        
        # 状态机
        self.state = "idle"  # 状态: idle, pending, active, cooldown
        self.state_start_time = 0
        
        # 按键序列跟踪
        self.key_history = []  # 记录按键时间序列
        
    def update(self, pressed_keys: Set[int], mouse_buttons: Tuple[bool, bool, bool], current_time: int):
        """更新动作状态"""
        # 保存前一状态
        prev_pressed = self.pressed
        prev_state = self.state
        
        # 1. 检测物理输入状态
        key_pressed = any(key in pressed_keys for key in self.keys)
        mouse_pressed = any(mouse_buttons[i] for i in self.mouse_buttons)
        physical_pressed = key_pressed or mouse_pressed
        
        # 2. 状态机更新
        if self.state == "idle":
            if physical_pressed:
                # 记录按键时间并进入待定状态
                self.last_press_time = current_time
                self.state = "pending"
                self.state_start_time = current_time
                # 记录按键历史（最多保留5个）
                self.key_history.append(current_time)
                if len(self.key_history) > 5:
                    self.key_history.pop(0)
        
        elif self.state == "pending":
            if not physical_pressed:
                # 在防抖时间内释放，忽略此按键
                self.state = "idle"
            elif current_time - self.state_start_time >= self.debounce_time:
                # 防抖时间结束，进入激活状态
                self.state = "active"
                self.state_start_time = current_time
        
        elif self.state == "active":
            if not physical_pressed:
                # 释放按键，进入冷却状态
                self.last_release_time = current_time
                self.state = "cooldown"
                self.state_start_time = current_time
        
        elif self.state == "cooldown":
            # 检查是否应该返回空闲状态
            if current_time - self.state_start_time >= self.release_guard_time:
                self.state = "idle"
            elif physical_pressed:
                # 在冷却期内再次按下，返回待定状态
                self.state = "pending"
                self.state_start_time = current_time
        
        # 3. 更新输出状态
        self.pressed = (self.state == "active")
        
        # 处理快速连按问题
        if self.state == "pending" and self.is_rapid_press(current_time):
            # 检测到快速连按模式，强制进入激活状态
            self.state = "active"
            self.state_start_time = current_time
            self.pressed = True
        
        self.just_pressed = self.pressed and not prev_pressed
        self.just_released = not self.pressed and prev_pressed
    
    def is_rapid_press(self, current_time: int) -> bool:
        """检测快速连按模式"""
        if len(self.key_history) < 3:
            return False
        
        # 检查最近3次按键的时间间隔
        intervals = []
        for i in range(1, len(self.key_history)):
            interval = self.key_history[i] - self.key_history[i-1]
            intervals.append(interval)
        
        # 如果最近3次按键都在很短的时间内发生
        if all(interval < 150 for interval in intervals[-2:]):
            return True
        
        return False


class InputManager:
    """输入管理器"""
    
    def __init__(self):
        self.actions: Dict[str, InputAction] = {}
        self.pressed_keys: Set[int] = set()
        self.mouse_buttons = (False, False, False)  # 左、中、右
        self.mouse_position = (0, 0)
        self.mouse_delta = (0, 0)  # 鼠标移动增量
        self.last_mouse_position = (0, 0)
        self.current_time = 0
        
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
        self.add_action("player1_melee", [pygame.BUTTON_LEFT])
        self.add_action("player1_ranged", [pygame.BUTTON_RIGHT])
        
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
                # 创建一个新的元组来更新鼠标按钮状态
                new_buttons = list(self.mouse_buttons)
                new_buttons[event.button - 1] = True
                self.mouse_buttons = tuple(new_buttons)
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button <= 3:
                # 创建一个新的元组来更新鼠标按钮状态
                new_buttons = list(self.mouse_buttons)
                new_buttons[event.button - 1] = False
                self.mouse_buttons = tuple(new_buttons)
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
        # 获取当前时间(毫秒)
        self.current_time = pygame.time.get_ticks()
        
        # 更新所有动作的状态
        for action in self.actions.values():
            action.update(self.pressed_keys, self.mouse_buttons, self.current_time)
            
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
            action.state = "idle"
            action.state_start_time = 0
            action.key_history = []
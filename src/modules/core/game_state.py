"""
游戏状态管理
负责管理游戏的全局状态，包括游戏模式、暂停状态、调试模式等
"""

from enum import Enum
from typing import Optional, Dict, Any


class GameMode(Enum):
    """游戏模式枚举"""
    SINGLE_PLAYER = "single_player"
    DUAL_PLAYER = "dual_player"
    SPLIT_SCREEN = "split_screen"


class GameState:
    """游戏状态管理类"""
    
    def __init__(self):
        # 基础状态
        self.running = True
        self.paused = False
        self.game_over = False
        self.game_victory = False
        self.debug_mode = False
        
        # 游戏模式
        self.game_mode = GameMode.SINGLE_PLAYER
        
        # 场景状态
        self.current_scene = None
        self.previous_scene = None
        
        # 游戏数据
        self.game_time = 0.0
        self.kill_count = 0
        self.level = 1
        self.current_map = None
        
        # 性能监控
        self.fps = 0
        self.fps_timer = 0
        
        # 消息系统
        self.message = ""
        self.message_timer = 0.0
        self.message_duration = 0.0
        
        # 配置数据
        self.config = {}
        
    def update(self, dt: float):
        """更新游戏状态"""
        if not self.paused:
            self.game_time += dt
            
        # 更新消息计时器
        if self.message_timer > 0:
            self.message_timer -= dt
            if self.message_timer <= 0:
                self.message = ""
                
    def set_game_mode(self, mode: GameMode):
        """设置游戏模式"""
        self.game_mode = mode
        
    def is_dual_player(self) -> bool:
        """检查是否为双人模式"""
        return self.game_mode in [GameMode.DUAL_PLAYER, GameMode.SPLIT_SCREEN]
        
    def is_split_screen(self) -> bool:
        """检查是否为分屏模式"""
        return self.game_mode == GameMode.SPLIT_SCREEN
        
    def show_message(self, message: str, duration: float = 3.0):
        """显示消息"""
        self.message = message
        self.message_duration = duration
        self.message_timer = duration
        
    def pause(self):
        """暂停游戏"""
        self.paused = True
        
    def resume(self):
        """恢复游戏"""
        self.paused = False
        
    def toggle_pause(self):
        """切换暂停状态"""
        self.paused = not self.paused
        
    def reset(self):
        """重置游戏状态"""
        self.game_over = False
        self.game_victory = False
        self.paused = False
        self.game_time = 0.0
        self.kill_count = 0
        self.level = 1
        self.message = ""
        self.message_timer = 0.0
        
    def get_state_dict(self) -> Dict[str, Any]:
        """获取状态字典（用于保存）"""
        return {
            'game_time': self.game_time,
            'kill_count': self.kill_count,
            'level': self.level,
            'current_map': self.current_map,
            'game_mode': self.game_mode.value
        }
        
    def load_state_dict(self, state_dict: Dict[str, Any]):
        """从字典加载状态（用于读取）"""
        self.game_time = state_dict.get('game_time', 0.0)
        self.kill_count = state_dict.get('kill_count', 0)
        self.level = state_dict.get('level', 1)
        self.current_map = state_dict.get('current_map')
        mode_value = state_dict.get('game_mode', 'single_player')
        self.game_mode = GameMode(mode_value) 
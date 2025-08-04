"""
游戏引擎 - 重构后的主游戏类
使用新的面向对象架构，更加模块化和可维护
"""

import pygame
import time
from typing import Optional

from .core import GameState, SceneManager, InputManager, RenderManager
from .core.game_state import GameMode
from .scenes import MainMenuScene, GameScene, SplitScreenScene
from .managers import ResourceManager, SaveManager, UpgradeManager


class GameEngine:
    """游戏引擎主类"""
    
    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self.clock = pygame.time.Clock()
        
        # 初始化核心系统
        self.game_state = GameState()
        self.scene_manager = SceneManager(screen, self.game_state)
        self.input_manager = InputManager()
        self.render_manager = RenderManager(screen)
        
        # 初始化管理器
        self.resource_manager = ResourceManager()
        self.save_manager = SaveManager()
        self.upgrade_manager = UpgradeManager()
        
        # 性能监控
        self.fps = 0
        self.frame_count = 0
        self.last_fps_update = time.time()
        
        # 初始化场景
        self._setup_scenes()
        
        # 启动主菜单
        self.scene_manager.switch_scene("main_menu")
        
    def _setup_scenes(self):
        """设置场景"""
        # 创建场景实例
        main_menu_scene = MainMenuScene(self.scene_manager)
        game_scene = GameScene(self.scene_manager)
        split_screen_scene = SplitScreenScene(self.scene_manager)
        
        # 注册场景
        self.scene_manager.register_scene("main_menu", main_menu_scene)
        self.scene_manager.register_scene("game", game_scene)
        self.scene_manager.register_scene("split_screen", split_screen_scene)
        
    def handle_event(self, event: pygame.event.Event):
        """处理事件"""
        # 更新输入管理器
        self.input_manager.handle_event(event)
        
        # 处理通用事件
        if event.type == pygame.QUIT:
            self.game_state.running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.game_state.toggle_pause()
            elif event.key == pygame.K_F1:
                self.game_state.debug_mode = not self.game_state.debug_mode
                self.render_manager.enable_grid = self.game_state.debug_mode
                
        # 将事件传递给场景管理器
        self.scene_manager.handle_event(event)
        
    def update(self, dt: float):
        """更新游戏"""
        # 更新输入管理器
        self.input_manager.update()
        
        # 更新游戏状态
        self.game_state.update(dt)
        
        # 更新场景管理器
        self.scene_manager.update(dt)
        
        # 更新性能监控
        self._update_performance(dt)
        
    def render(self):
        """渲染游戏"""
        # 渲染场景
        self.scene_manager.render(self.screen)
        
        # 渲染调试信息
        if self.game_state.debug_mode:
            self._render_debug_info()
            
        # 更新显示
        pygame.display.flip()
        
    def _update_performance(self, dt: float):
        """更新性能监控"""
        self.frame_count += 1
        current_time = time.time()
        
        if current_time - self.last_fps_update >= 1.0:
            self.fps = self.frame_count
            self.frame_count = 0
            self.last_fps_update = current_time
            
    def _render_debug_info(self):
        """渲染调试信息"""
        font = pygame.font.SysFont('simHei', 24)
        
        # FPS
        fps_text = font.render(f"FPS: {self.fps}", True, (255, 255, 255))
        self.screen.blit(fps_text, (10, 10))
        
        # 当前场景
        scene_name = self.scene_manager.get_current_scene_name() or "None"
        scene_text = font.render(f"Scene: {scene_name}", True, (255, 255, 255))
        self.screen.blit(scene_text, (10, 35))
        
        # 游戏时间
        time_text = font.render(f"Time: {self.game_state.game_time:.1f}s", True, (255, 255, 255))
        self.screen.blit(time_text, (10, 60))
        
        # 游戏模式
        mode_text = font.render(f"Mode: {self.game_state.game_mode.value}", True, (255, 255, 255))
        self.screen.blit(mode_text, (10, 85))
        
    def run(self):
        """运行游戏主循环"""
        while self.game_state.running:
            # 处理事件
            for event in pygame.event.get():
                self.handle_event(event)
                
            # 计算帧时间
            dt = self.clock.tick(60) / 1000.0
            
            # 更新游戏
            self.update(dt)
            
            # 渲染游戏
            self.render()
            
    def start_new_game(self, game_mode: GameMode = GameMode.SINGLE_PLAYER):
        """开始新游戏"""
        self.game_state.set_game_mode(game_mode)
        self.game_state.reset()
        
        if game_mode == GameMode.SPLIT_SCREEN:
            self.scene_manager.switch_scene("split_screen")
        else:
            self.scene_manager.switch_scene("game")
            
    def load_game(self, save_slot: int):
        """加载游戏"""
        save_data = self.save_manager.load_game(save_slot)
        if save_data:
            self.game_state.load_state_dict(save_data)
            self.scene_manager.switch_scene("game")
            
    def save_game(self, save_slot: int):
        """保存游戏"""
        save_data = self.game_state.get_state_dict()
        self.save_manager.save_game(save_slot, save_data)
        
    def quit_game(self):
        """退出游戏"""
        self.game_state.running = False 
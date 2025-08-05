#!/usr/bin/env python3
"""
测试波次UI功能
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

import pygame
from modules.game import Game

def test_round_ui():
    """测试波次UI"""
    pygame.init()
    screen = pygame.display.set_mode((1200, 800))
    pygame.display.set_caption("波次UI测试")
    
    # 创建游戏实例
    game = Game(screen)
    
    # 模拟游戏开始
    game.in_main_menu = False
    game.in_map_hero_select = False
    game.current_map = "small_map"
    
    # 模拟双人模式
    from modules.dual_player_system import DualPlayerSystem
    game.dual_player_system = DualPlayerSystem(screen, game)
    game.player = game.dual_player_system.ninja_frog
    
    # 初始化敌人管理器
    from modules.enemies.enemy_manager import EnemyManager
    game.enemy_manager = EnemyManager()
    game.enemy_manager.game = game
    game.enemy_manager.on_round_start = game._on_round_start
    
    print("测试波次UI...")
    print("按数字键1、2、3来模拟不同波次")
    print("按ESC退出")
    
    # 运行游戏循环
    clock = pygame.time.Clock()
    running = True
    
    while running:
        dt = clock.tick(60) / 1000.0  # 转换为秒
        
        # 处理事件
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_1:
                    print("模拟第1波开始...")
                    game.enemy_manager._start_round(1, "第1波", 2.5, 1.0, 1.0, 24)
                elif event.key == pygame.K_2:
                    print("模拟第2波开始...")
                    game.enemy_manager._start_round(2, "第2波", 1.5, 1.2, 1.2, 40)
                elif event.key == pygame.K_3:
                    print("模拟第3波开始...")
                    game.enemy_manager._start_round(3, "第3波", 1.0, 1.0, 1.5, 120)
        
        # 更新游戏
        game.update(dt)
        
        # 渲染游戏
        game.render()
    
    pygame.quit()

if __name__ == "__main__":
    test_round_ui() 
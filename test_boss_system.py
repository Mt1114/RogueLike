#!/usr/bin/env python3
"""
测试boss系统的基本功能
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

import pygame
from modules.game import Game

def test_boss_system():
    """测试boss系统"""
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Boss系统测试")
    
    # 创建游戏实例
    game = Game(screen)
    
    # 模拟开始游戏
    game._start_game_with_selection("simple_map", "ninja_frog")
    
    print("=== Boss系统测试 ===")
    print(f"游戏时间: {game.game_time}秒")
    print(f"Boss已生成: {game.boss_spawned}")
    print(f"敌人数量: {len(game.enemy_manager.enemies)}")
    
    # 模拟时间流逝到1秒后
    game.game_time = 1.0
    game._update_boss_spawn(0.016)
    
    print(f"\n--- 1秒后 ---")
    print(f"Boss已生成: {game.boss_spawned}")
    print(f"敌人数量: {len(game.enemy_manager.enemies)}")
    
    # 检查是否有boss
    boss_count = 0
    for enemy in game.enemy_manager.enemies:
        if enemy.type == "soul_boss":
            boss_count += 1
            print(f"找到Boss: 血量 {enemy.health}/{enemy.max_health}")
    
    print(f"Boss数量: {boss_count}")
    
    print("\n=== 测试完成 ===")
    pygame.quit()

if __name__ == "__main__":
    test_boss_system() 
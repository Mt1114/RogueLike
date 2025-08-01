#!/usr/bin/env python3
"""
测试钥匙系统的基本功能
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

import pygame
from modules.game import Game

def test_key_system():
    """测试钥匙系统"""
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("钥匙系统测试")
    
    # 创建游戏实例
    game = Game(screen)
    
    # 模拟开始游戏
    game._start_game_with_selection("simple_map", "ninja_frog")
    
    print("=== 钥匙系统测试 ===")
    print(f"玩家初始钥匙数量: {game.player.keys_collected}/{game.player.total_keys_needed}")
    print(f"钥匙管理器状态: 已生成 {game.key_manager.get_total_spawned()} 把钥匙")
    print(f"当前存在的钥匙: {game.key_manager.get_key_count()} 把")
    
    # 模拟时间流逝
    test_times = [0, 90, 210]  # 0秒、1:30、3:30
    for time in test_times:
        print(f"\n--- 游戏时间 {time} 秒 ---")
        game.game_time = time
        game.key_manager.update(0.016, time)  # 16ms的dt
        print(f"已生成钥匙: {game.key_manager.get_total_spawned()}")
        print(f"当前存在钥匙: {game.key_manager.get_key_count()}")
        print(f"物品管理器中的钥匙: {len([item for item in game.item_manager.items if item.item_type == 'key'])}")
    
    print("\n=== 测试完成 ===")
    pygame.quit()

if __name__ == "__main__":
    test_key_system() 
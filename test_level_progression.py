#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试关卡进阶系统
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from modules.game_result_ui import GameResultUI
import pygame

def test_level_progression():
    """测试关卡进阶逻辑"""
    print("=== 测试关卡进阶系统 ===")
    
    # 初始化pygame
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    
    # 创建游戏结果UI
    game_result_ui = GameResultUI(screen)
    
    # 测试不同地图的关卡进阶
    test_maps = ["small_map", "test2_map", "test3_map", "simple_map"]
    
    for map_name in test_maps:
        print(f"\n测试地图: {map_name}")
        game_result_ui.show(is_victory=True, current_map=map_name)
        
        print(f"  当前地图: {game_result_ui.current_map}")
        print(f"  下一关: {game_result_ui.next_map}")
        print(f"  最终关卡: {game_result_ui.is_final_level}")
        
        # 模拟按钮显示
        game_result_ui.show_buttons = True
        game_result_ui._render_button_popup()
        
        # 检查应该显示什么按钮
        if game_result_ui.is_victory and game_result_ui.next_map and not game_result_ui.is_final_level:
            print("  ✓ 应该显示下一关按钮")
        elif game_result_ui.is_victory and game_result_ui.is_final_level:
            print("  ✓ 应该只显示回到主页按钮（最终关卡）")
        else:
            print("  ✓ 应该显示重新开始和回到主页按钮")

if __name__ == "__main__":
    test_level_progression() 
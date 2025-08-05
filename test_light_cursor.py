#!/usr/bin/env python3
"""
测试鼠标光标和电量图标功能
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

import pygame
from modules.game import Game

def test_light_cursor():
    """测试鼠标光标和电量图标"""
    pygame.init()
    screen = pygame.display.set_mode((1200, 800))
    pygame.display.set_caption("鼠标光标和电量图标测试")
    
    # 创建游戏实例
    game = Game(screen)
    
    # 模拟游戏开始
    game.in_main_menu = False
    game.in_map_hero_select = False
    game.showing_main_menu_animation = False
    game.current_map = "small_map"
    
    # 模拟双人模式
    from modules.dual_player_system import DualPlayerSystem
    game.dual_player_system = DualPlayerSystem(screen, game)
    game.player = game.dual_player_system.ninja_frog
    
    # 设置鼠标光标
    if game.light_cursor:
        pygame.mouse.set_visible(False)
        print("设置战斗鼠标光标")
    
    print("测试鼠标光标和电量图标...")
    print("移动鼠标查看自定义光标")
    print("观察右上角的电量图标")
    print("按ESC退出")
    
    # 运行测试循环
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
        
        # 更新游戏
        game.update(dt)
        
        # 渲染游戏
        game.render()
    
    # 恢复默认鼠标光标
    pygame.mouse.set_visible(True)
    pygame.quit()

if __name__ == "__main__":
    test_light_cursor() 
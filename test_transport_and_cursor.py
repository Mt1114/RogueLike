#!/usr/bin/env python3
"""
测试传送道具图标和鼠标光标修复
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

import pygame
from modules.game import Game

def test_transport_and_cursor():
    """测试传送道具图标和鼠标光标修复"""
    pygame.init()
    screen = pygame.display.set_mode((1200, 800))
    pygame.display.set_caption("传送道具图标和鼠标光标测试")
    
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
    
    # 初始化传送道具管理器
    from modules.items.teleport_manager import TeleportManager
    game.teleport_manager = TeleportManager(game.map_manager)
    
    # 生成一个传送道具
    game.teleport_manager.spawn_teleport_item()
    
    # 设置鼠标光标
    if game.light_cursor:
        pygame.mouse.set_visible(False)
        print("设置战斗鼠标光标")
    
    print("测试传送道具图标和鼠标光标...")
    print("观察地图中的传送道具图标")
    print("移动鼠标查看自定义光标")
    print("按1模拟游戏失败，按2模拟游戏胜利")
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
                elif event.key == pygame.K_1:
                    # 模拟游戏失败
                    print("模拟游戏失败...")
                    game.game_over = True
                    game.game_result_ui.show(is_victory=False)
                    pygame.mouse.set_visible(True)
                elif event.key == pygame.K_2:
                    # 模拟游戏胜利
                    print("模拟游戏胜利...")
                    game.game_victory = True
                    game.current_map = "test3_map"
                    game.game_result_ui.show(is_victory=True, current_map=game.current_map)
                    pygame.mouse.set_visible(True)
        
        # 更新游戏
        game.update(dt)
        
        # 渲染游戏
        game.render()
    
    # 恢复默认鼠标光标
    pygame.mouse.set_visible(True)
    pygame.quit()

if __name__ == "__main__":
    test_transport_and_cursor() 
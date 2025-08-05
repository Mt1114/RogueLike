#!/usr/bin/env python3
"""
测试关卡过渡动画功能
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

import pygame
from modules.game import Game

def test_level_transition():
    """测试关卡过渡动画"""
    pygame.init()
    screen = pygame.display.set_mode((1200, 800))
    pygame.display.set_caption("关卡过渡动画测试")
    
    # 创建游戏实例
    game = Game(screen)
    
    # 模拟游戏胜利状态
    game.current_map = "small_map"
    game.game_victory = True
    game.game_over = False
    
    print("测试关卡过渡动画...")
    print("当前地图: small_map")
    print("预期下一关: test2_map")
    
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
                elif event.key == pygame.K_SPACE:
                    # 按空格键模拟游戏胜利
                    print("模拟游戏胜利...")
                    game.game_victory = True
                    game.game_over = False
        
        # 更新游戏
        game.update(dt)
        
        # 渲染游戏
        game.render()
    
    pygame.quit()

if __name__ == "__main__":
    test_level_transition() 
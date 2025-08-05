#!/usr/bin/env python3
"""
测试忍者蛙穿墙技能图标
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

import pygame
from modules.player import Player

def test_phase_icon():
    """测试穿墙技能图标"""
    pygame.init()
    screen = pygame.display.set_mode((1200, 800))
    pygame.display.set_caption("穿墙技能图标测试")
    
    # 创建忍者蛙
    ninja_frog = Player(600, 400, hero_type="ninja_frog")
    
    print("测试忍者蛙穿墙技能图标...")
    print("按空格键激活穿墙技能")
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
                elif event.key == pygame.K_SPACE:
                    # 激活穿墙技能
                    print("激活穿墙技能...")
                    ninja_frog.activate_phase_through_walls()
        
        # 更新忍者蛙
        ninja_frog.update(dt)
        
        # 清屏
        screen.fill((0, 0, 0))
        
        # 渲染忍者蛙
        ninja_frog.render(screen)
        
        # 渲染穿墙技能CD
        ninja_frog.render_phase_cooldown(screen)
        
        # 更新显示
        pygame.display.flip()
    
    pygame.quit()

if __name__ == "__main__":
    test_phase_icon() 
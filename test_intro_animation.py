#!/usr/bin/env python3
"""
测试修改后的进场动画
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

import pygame
from modules.intro_animation import IntroAnimation

def test_intro_animation():
    """测试进场动画"""
    pygame.init()
    screen = pygame.display.set_mode((1200, 800))
    pygame.display.set_caption("进场动画测试")
    
    # 创建进场动画
    intro_animation = IntroAnimation(screen)
    
    print("测试修改后的进场动画...")
    print("观察像素块从屏幕边框飞向logo的过程")
    print("拼装时间已延长到5秒")
    print("按ESC跳过动画")
    
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
        
        # 更新动画
        intro_animation.update(dt)
        
        # 渲染动画
        intro_animation.render()
        
        # 更新显示
        pygame.display.flip()
        
        # 检查动画是否结束
        if intro_animation.is_finished():
            print("进场动画结束")
            break
    
    pygame.quit()

if __name__ == "__main__":
    test_intro_animation() 
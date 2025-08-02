#!/usr/bin/env python3
"""
测试神秘剑士临时光源的消失机制
"""

import pygame
import sys
import os

# 添加src目录到路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from modules.game import Game
from modules.dual_player_system import DualPlayerSystem

def main():
    # 初始化pygame
    pygame.init()
    
    # 创建屏幕
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("测试神秘剑士临时光源消失")
    
    # 创建游戏实例
    game = Game(screen)
    
    # 创建双角色系统
    dual_system = DualPlayerSystem(screen, game)
    
    # 游戏循环
    clock = pygame.time.Clock()
    running = True
    
    print("测试说明：")
    print("1. 按数字键盘的2、4、6、8键来触发神秘剑士的攻击")
    print("2. 观察神秘剑士周围的临时光源是否在0.5秒后消失")
    print("3. 光源应该只在攻击时出现，然后逐渐消失")
    print("4. 按ESC键退出")
    
    while running:
        dt = clock.tick(60) / 1000.0  # 转换为秒
        
        # 处理事件
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key in [pygame.K_KP2, pygame.K_KP4, pygame.K_KP6, pygame.K_KP8]:
                    # 触发神秘剑士攻击
                    dual_system.handle_event(event)
                    print(f"触发攻击，临时光源激活，剩余时间: {dual_system.mystic_flashlight_timer:.2f}秒")
            else:
                dual_system.handle_event(event)
        
        # 更新系统
        dual_system.update(dt)
        
        # 检查临时光源状态
        if dual_system.mystic_flashlight_active:
            print(f"临时光源活跃中，剩余时间: {dual_system.mystic_flashlight_timer:.2f}秒")
        elif dual_system.mystic_flashlight_timer <= 0 and dual_system.mystic_flashlight_active == False:
            print("临时光源已消失")
        
        # 渲染
        screen.fill((0, 0, 0))  # 黑色背景
        
        # 渲染双角色系统
        dual_system.render(screen, 0, 0)
        dual_system.render_weapons(screen, 0, 0)
        
        # 显示调试信息
        font = pygame.font.Font(None, 24)
        debug_text = f"临时光源: {'活跃' if dual_system.mystic_flashlight_active else '关闭'}"
        if dual_system.mystic_flashlight_active:
            debug_text += f" | 剩余时间: {dual_system.mystic_flashlight_timer:.2f}s"
        
        text_surface = font.render(debug_text, True, (255, 255, 255))
        screen.blit(text_surface, (10, 10))
        
        pygame.display.flip()
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main() 
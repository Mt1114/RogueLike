#!/usr/bin/env python3
"""
测试神秘剑士永久性圆形光源
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
    pygame.display.set_caption("测试神秘剑士永久性圆形光源")
    
    # 创建游戏实例
    game = Game(screen)
    
    # 创建双角色系统
    dual_system = DualPlayerSystem(screen, game)
    
    # 游戏循环
    clock = pygame.time.Clock()
    running = True
    
    print("测试说明：")
    print("1. 神秘剑士现在有一个永久性的圆形光源")
    print("2. 忍者蛙有扇形光源，方向跟随鼠标")
    print("3. 两个光源同时存在，都能去除黑暗")
    print("4. 使用WASD移动忍者蛙，方向键移动神秘剑士")
    print("5. 使用数字键盘2、4、6、8键让神秘剑士攻击")
    print("6. 按ESC键退出")
    
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
                    print(f"神秘剑士攻击，方向: {dual_system.mystic_attack_direction}")
            else:
                dual_system.handle_event(event)
        
        # 更新系统
        dual_system.update(dt)
        
        # 渲染
        screen.fill((0, 0, 0))  # 黑色背景
        
        # 渲染双角色系统
        dual_system.render(screen, 0, 0)
        dual_system.render_weapons(screen, 0, 0)
        
        # 显示调试信息
        font = pygame.font.Font(None, 24)
        debug_text = f"神秘剑士永久光源: 活跃 | 忍者蛙扇形光源: 活跃"
        
        text_surface = font.render(debug_text, True, (255, 255, 255))
        screen.blit(text_surface, (10, 10))
        
        # 显示角色位置信息
        ninja_pos = f"忍者蛙: ({dual_system.ninja_frog.world_x:.0f}, {dual_system.ninja_frog.world_y:.0f})"
        mystic_pos = f"神秘剑士: ({dual_system.mystic_swordsman.world_x:.0f}, {dual_system.mystic_swordsman.world_y:.0f})"
        
        ninja_text = font.render(ninja_pos, True, (255, 255, 255))
        mystic_text = font.render(mystic_pos, True, (255, 255, 255))
        
        screen.blit(ninja_text, (10, 35))
        screen.blit(mystic_text, (10, 60))
        
        pygame.display.flip()
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main() 
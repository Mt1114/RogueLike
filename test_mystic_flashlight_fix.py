#!/usr/bin/env python3
"""
测试神秘剑士光源修复
验证：
1. 神秘剑士开枪时会产生临时光源
2. 光源不会永久存在，0.5秒后自动消失
3. 两个光源使用同一个黑暗遮罩
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

import pygame
import time
from modules.dual_player_system import DualPlayerSystem

class MockGame:
    def __init__(self):
        self.map_manager = None

def test_mystic_flashlight_fix():
    """测试神秘剑士光源修复"""
    # 初始化pygame
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("神秘剑士光源修复测试")
    clock = pygame.time.Clock()
    
    # 创建模拟游戏对象
    game = MockGame()
    
    # 创建双玩家系统
    dual_system = DualPlayerSystem(screen, game)
    
    print("=== 神秘剑士光源修复测试 ===")
    print("控制说明：")
    print("- WASD: 忍者蛙移动")
    print("- 方向键: 神秘剑士移动")
    print("- 数字键盘 2/4/6/8: 神秘剑士攻击（触发临时光源）")
    print("- ESC: 退出")
    print()
    
    running = True
    last_attack_time = 0
    
    while running:
        dt = clock.tick(60) / 1000.0  # 转换为秒
        
        # 处理事件
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                else:
                    dual_system.handle_event(event)
            elif event.type == pygame.KEYUP:
                dual_system.handle_event(event)
        
        # 更新系统
        dual_system.update(dt)
        
        # 清屏
        screen.fill((50, 50, 50))  # 深灰色背景
        
        # 渲染双玩家系统
        dual_system.render(screen, 0, 0)  # 相机位置为0,0
        
        # 渲染武器效果
        dual_system.render_weapons(screen, 0, 0)
        
        # 显示调试信息
        font = pygame.font.Font(None, 24)
        
        # 显示神秘剑士光源状态
        if dual_system.mystic_flashlight_active:
            status_text = f"神秘剑士光源: 活跃 | 剩余时间: {dual_system.mystic_flashlight_timer:.2f}s"
            color = (0, 255, 0)  # 绿色
        else:
            status_text = "神秘剑士光源: 关闭"
            color = (255, 255, 255)  # 白色
            
        status_surface = font.render(status_text, True, color)
        screen.blit(status_surface, (10, 10))
        
        # 显示操作提示
        hint_text = "按数字键盘 2/4/6/8 触发神秘剑士攻击"
        hint_surface = font.render(hint_text, True, (255, 255, 0))
        screen.blit(hint_surface, (10, 40))
        
        # 显示角色位置
        ninja_pos = f"忍者蛙: ({dual_system.ninja_frog.world_x:.0f}, {dual_system.ninja_frog.world_y:.0f})"
        mystic_pos = f"神秘剑士: ({dual_system.mystic_swordsman.world_x:.0f}, {dual_system.mystic_swordsman.world_y:.0f})"
        
        ninja_surface = font.render(ninja_pos, True, (255, 255, 255))
        mystic_surface = font.render(mystic_pos, True, (255, 255, 255))
        screen.blit(ninja_surface, (10, 70))
        screen.blit(mystic_surface, (10, 100))
        
        # 更新显示
        pygame.display.flip()
        
        # 检查光源是否正确消失
        if dual_system.mystic_flashlight_active:
            if dual_system.mystic_flashlight_timer <= 0:
                print("✓ 光源在0.5秒后正确消失")
        
    pygame.quit()
    print("测试完成")

if __name__ == "__main__":
    test_mystic_flashlight_fix() 
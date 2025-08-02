#!/usr/bin/env python3
import pygame
import sys
import os

# 添加src目录到路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from modules.dual_player_system import DualPlayerSystem
from modules.game import Game

def test_mystic_fixed():
    """测试修复后的神秘剑士攻击功能"""
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("神秘剑士攻击测试 - 修复版")
    clock = pygame.time.Clock()
    
    # 创建游戏实例
    game = Game(screen)
    
    # 创建双角色系统
    dual_system = DualPlayerSystem(screen, game)
    
    print("=== 神秘剑士攻击测试 - 修复版 ===")
    print("使用数字键盘 2,4,6,8 测试神秘剑士攻击")
    print("2=下, 4=左, 6=右, 8=上")
    print("按ESC退出")
    
    running = True
    attack_count = 0
    
    while running:
        dt = clock.tick(60) / 1000.0
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key in [pygame.K_KP2, pygame.K_KP4, pygame.K_KP6, pygame.K_KP8]:
                    attack_count += 1
                    print(f"\n=== 攻击测试 {attack_count} ===")
                    print(f"按键: {event.key}")
                    
                    # 检查攻击后的武器状态
                    for weapon in dual_system.mystic_swordsman.weapons:
                        if hasattr(weapon, 'attack_timer'):
                            print(f"武器 {weapon.type} 攻击计时器: {weapon.attack_timer}")
                        if hasattr(weapon, 'ammo'):
                            print(f"武器 {weapon.type} 弹药: {weapon.ammo}")
                        if hasattr(weapon, 'projectiles'):
                            print(f"武器 {weapon.type} 投射物数量: {len(weapon.projectiles)}")
            
            # 处理所有事件（包括攻击）
            dual_system.handle_event(event)
        
        # 更新
        dual_system.update(dt)
        
        # 渲染
        screen.fill((50, 50, 50))
        
        # 渲染双角色系统
        dual_system.render(screen, 0, 0)
        dual_system.render_weapons(screen, 0, 0)
        
        # 显示调试信息
        font = pygame.font.Font(None, 20)
        texts = [
            "神秘剑士攻击测试 - 修复版",
            "数字键盘: 2=下, 4=左, 6=右, 8=上",
            f"攻击测试次数: {attack_count}",
            f"神秘剑士武器数量: {len(dual_system.mystic_swordsman.weapons)}",
            "按ESC退出"
        ]
        
        for i, text in enumerate(texts):
            text_surface = font.render(text, True, (255, 255, 255))
            screen.blit(text_surface, (10, 10 + i * 25))
        
        pygame.display.flip()
    
    pygame.quit()

if __name__ == "__main__":
    test_mystic_fixed() 
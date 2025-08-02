#!/usr/bin/env python3
import pygame
import sys
import os

# 添加src目录到路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from modules.dual_player_system import DualPlayerSystem
from modules.game import Game

def debug_mystic_weapons():
    """调试神秘剑士的武器系统"""
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("神秘剑士武器调试")
    clock = pygame.time.Clock()
    
    # 创建游戏实例
    game = Game(screen)
    
    # 创建双角色系统
    dual_system = DualPlayerSystem(screen, game)
    
    print("=== 神秘剑士武器调试信息 ===")
    print(f"神秘剑士武器数量: {len(dual_system.mystic_swordsman.weapons)}")
    
    # 检查武器管理器状态
    weapon_manager = dual_system.mystic_swordsman.weapon_manager
    print(f"武器管理器启用状态: {weapon_manager.enabled}")
    print(f"武器管理器武器列表: {[w.type for w in weapon_manager.weapons]}")
    
    # 检查每个武器的详细信息
    for i, weapon in enumerate(dual_system.mystic_swordsman.weapons):
        print(f"\n武器 {i+1}:")
        print(f"  类型: {weapon.type}")
        print(f"  类名: {type(weapon).__name__}")
        print(f"  攻击间隔: {getattr(weapon, 'attack_interval', 'N/A')}")
        print(f"  攻击计时器: {getattr(weapon, 'attack_timer', 'N/A')}")
        print(f"  弹药: {getattr(weapon, 'ammo', 'N/A')}")
        print(f"  是否为近战: {getattr(weapon, 'is_melee', 'N/A')}")
    
    # 手动添加武器测试
    print("\n=== 手动添加武器测试 ===")
    dual_system.mystic_swordsman.add_weapon("bullet")
    dual_system.mystic_swordsman.add_weapon("knife")
    
    print(f"添加武器后数量: {len(dual_system.mystic_swordsman.weapons)}")
    for weapon in dual_system.mystic_swordsman.weapons:
        print(f"  - {weapon.type}")
    
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
                    
                    # 直接测试武器攻击
                    print("直接调用武器管理器攻击...")
                    dual_system.mystic_swordsman.weapon_manager.manual_attack(screen)
                    
                    # 检查攻击后的武器状态
                    for weapon in dual_system.mystic_swordsman.weapons:
                        if hasattr(weapon, 'attack_timer'):
                            print(f"武器 {weapon.type} 攻击计时器: {weapon.attack_timer}")
                        if hasattr(weapon, 'ammo'):
                            print(f"武器 {weapon.type} 弹药: {weapon.ammo}")
                
                # 测试鼠标攻击
                elif event.key == pygame.K_SPACE:
                    print("\n=== 空格键测试鼠标攻击 ===")
                    dual_system.mystic_swordsman.weapon_manager.manual_attack(screen)
            
            # 处理其他事件
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
            f"神秘剑士武器数量: {len(dual_system.mystic_swordsman.weapons)}",
            "数字键盘: 2,4,6,8 测试攻击",
            "空格键: 测试鼠标攻击",
            f"攻击测试次数: {attack_count}",
            "按ESC退出"
        ]
        
        for i, text in enumerate(texts):
            text_surface = font.render(text, True, (255, 255, 255))
            screen.blit(text_surface, (10, 10 + i * 25))
        
        pygame.display.flip()
    
    pygame.quit()

if __name__ == "__main__":
    debug_mystic_weapons() 
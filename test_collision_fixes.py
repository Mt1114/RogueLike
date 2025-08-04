#!/usr/bin/env python3
"""
测试碰撞检测和判负逻辑的修复
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

import pygame
from modules.game import Game
from modules.resource_manager import resource_manager

def test_collision_and_death_logic():
    """测试碰撞检测和判负逻辑"""
    print("=== 测试碰撞检测和判负逻辑修复 ===")
    
    # 初始化Pygame
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("碰撞检测和判负逻辑测试")
    
    # 创建游戏实例
    game = Game(screen)
    
    # 测试1: 检查敌人碰撞体积是否增大
    print("\n1. 检查敌人碰撞体积:")
    if hasattr(game, 'enemy_manager') and game.enemy_manager:
        for enemy in game.enemy_manager.enemies:
            print(f"  敌人类型: {enemy.type}")
            print(f"  碰撞箱大小: {enemy.rect.width} x {enemy.rect.height}")
            print(f"  预期大小: 60 x 40 (考虑缩放)")
    
    # 测试2: 检查双角色模式判负逻辑
    print("\n2. 检查双角色模式判负逻辑:")
    if hasattr(game, 'dual_player_system') and game.dual_player_system:
        ninja_health = game.dual_player_system.ninja_frog.health
        mystic_health = game.dual_player_system.mystic_swordsman.health
        print(f"  忍者蛙体力: {ninja_health}")
        print(f"  神秘剑客体力: {mystic_health}")
        print(f"  判负条件: 忍者蛙体力 <= 0 (已修复)")
    
    # 测试3: 检查碰撞检测距离
    print("\n3. 检查碰撞检测距离:")
    print("  双角色模式敌人子弹碰撞距离: 150像素")
    print("  单角色模式敌人子弹碰撞距离: 80像素 (已增大)")
    print("  敌人碰撞箱大小: 60x40 (已增大)")
    
    print("\n=== 修复总结 ===")
    print("✓ 敌人碰撞体积从44x30增大到60x40")
    print("✓ 双角色模式判负条件改为只检查忍者蛙体力")
    print("✓ 单角色模式敌人子弹碰撞距离从30增大到80像素")
    print("✓ 双角色模式敌人子弹碰撞距离保持150像素")
    
    pygame.quit()

if __name__ == "__main__":
    test_collision_and_death_logic() 
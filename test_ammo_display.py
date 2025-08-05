import pygame
import sys
import os

# 添加src目录到路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from modules.game import Game

def test_ammo_display():
    """测试双人模式下的弹药显示"""
    pygame.init()
    screen = pygame.display.set_mode((1200, 800))
    pygame.display.set_caption("弹药显示测试")
    
    # 创建游戏实例
    game = Game(screen)
    
    # 启动双人模式（使用地图1，英雄2）
    game._start_game_with_selection("test1_map.tmx", "role2")
    
    clock = pygame.time.Clock()
    running = True
    
    print("双人模式弹药显示测试")
    print("按U键进行远程攻击（消耗弹药）")
    print("按R键重置弹药")
    print("按ESC退出")
    
    while running:
        dt = clock.tick(60) / 1000.0
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_u:
                    # 进行远程攻击
                    if game.dual_player_system and game.dual_player_system.mystic_swordsman:
                        # 确保是远程模式
                        game.dual_player_system.mystic_swordsman.is_ranged_mode = True
                        # 触发远程攻击
                        game.dual_player_system.mystic_swordsman.weapon_manager.manual_attack(screen)
                        print("执行远程攻击")
                elif event.key == pygame.K_r:
                    # 重置弹药
                    if game.dual_player_system and game.dual_player_system.mystic_swordsman:
                        for weapon in game.dual_player_system.mystic_swordsman.weapon_manager.weapons:
                            if hasattr(weapon, 'ammo'):
                                weapon.ammo = weapon.max_ammo
                        print("重置弹药")
        
        # 更新游戏
        game.update(dt)
        
        # 渲染游戏
        game.render()
        
        # 显示当前弹药信息
        if game.dual_player_system and game.dual_player_system.mystic_swordsman:
            for weapon in game.dual_player_system.mystic_swordsman.weapon_manager.weapons:
                if hasattr(weapon, 'ammo') and not weapon.is_melee:
                    print(f"当前弹药: {weapon.ammo}/{weapon.max_ammo}")
                    break
        
        pygame.display.flip()
    
    pygame.quit()

if __name__ == "__main__":
    test_ammo_display() 
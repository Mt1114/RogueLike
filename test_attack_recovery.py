import pygame
import sys
import os

# 添加src目录到路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from modules.game import Game

def test_attack_recovery():
    """测试攻击后摇功能"""
    pygame.init()
    screen = pygame.display.set_mode((1200, 800))
    pygame.display.set_caption("攻击后摇测试")
    
    # 创建游戏实例
    game = Game(screen)
    
    # 启动双人模式（使用地图1，英雄2）
    game._start_game_with_selection("test1_map.tmx", "role2")
    
    clock = pygame.time.Clock()
    running = True
    
    print("攻击后摇测试")
    print("按U键进行远程攻击（0.5秒后摇）")
    print("按K键进行近战攻击（0.3秒后摇）")
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
                elif event.key == pygame.K_k:
                    # 进行近战攻击
                    if game.dual_player_system and game.dual_player_system.mystic_swordsman:
                        # 确保是近战模式
                        game.dual_player_system.mystic_swordsman.is_ranged_mode = False
                        # 触发近战攻击
                        game.dual_player_system.mystic_swordsman.weapon_manager.melee_attack(screen)
                        print("执行近战攻击")
        
        # 更新游戏
        game.update(dt)
        
        # 渲染游戏
        game.render()
        
        # 显示武器状态信息
        if game.dual_player_system and game.dual_player_system.mystic_swordsman:
            for weapon in game.dual_player_system.mystic_swordsman.weapon_manager.weapons:
                if hasattr(weapon, 'is_in_recovery'):
                    recovery_status = "后摇中" if weapon.is_in_recovery else "可攻击"
                    recovery_time = f"{weapon.attack_recovery_timer:.2f}/{weapon.attack_recovery_duration:.2f}" if weapon.is_in_recovery else "0.00/0.00"
                    print(f"武器: {weapon.type}, 状态: {recovery_status}, 后摇时间: {recovery_time}")
        
        pygame.display.flip()
    
    pygame.quit()

if __name__ == "__main__":
    test_attack_recovery() 
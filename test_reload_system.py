import pygame
import sys
import os

# 添加src目录到路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from modules.game import Game

def test_reload_system():
    """测试装弹系统"""
    pygame.init()
    screen = pygame.display.set_mode((1200, 800))
    pygame.display.set_caption("装弹系统测试")
    
    # 创建游戏实例
    game = Game(screen)
    
    # 启动双人模式（使用地图1，英雄2）
    game._start_game_with_selection("test1_map.tmx", "role2")
    
    clock = pygame.time.Clock()
    running = True
    
    print("装弹系统测试")
    print("按U键进行远程攻击（每30发子弹后装弹2秒）")
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
                                if hasattr(weapon, 'shots_fired'):
                                    weapon.shots_fired = 0
                                if hasattr(weapon, 'is_reloading'):
                                    weapon.is_reloading = False
                        print("重置弹药")
        
        # 更新游戏
        game.update(dt)
        
        # 渲染游戏
        game.render()
        
        # 显示武器状态信息
        if game.dual_player_system and game.dual_player_system.mystic_swordsman:
            for weapon in game.dual_player_system.mystic_swordsman.weapon_manager.weapons:
                if hasattr(weapon, 'type') and weapon.type == 'bullet':
                    reload_status = "装弹中" if hasattr(weapon, 'is_reloading') and weapon.is_reloading else "正常"
                    shots_info = f"已发射: {getattr(weapon, 'shots_fired', 0)}/30" if hasattr(weapon, 'shots_fired') else ""
                    reload_time = f"装弹时间: {getattr(weapon, 'reload_timer', 0):.1f}/2.0" if hasattr(weapon, 'is_reloading') and weapon.is_reloading else ""
                    print(f"子弹武器 - 状态: {reload_status}, {shots_info}, {reload_time}")
        
        pygame.display.flip()
    
    pygame.quit()

if __name__ == "__main__":
    test_reload_system() 
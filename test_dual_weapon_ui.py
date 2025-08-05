import pygame
import sys
import os

# 添加src目录到路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from modules.game import Game

def test_dual_weapon_ui():
    """测试双人模式下的武器选择UI"""
    pygame.init()
    screen = pygame.display.set_mode((1200, 800))
    pygame.display.set_caption("双人武器选择UI测试")
    
    # 创建游戏实例
    game = Game(screen)
    
    # 启动双人模式（使用地图1，英雄2）
    game._start_game_with_selection("test1_map.tmx", "role2")
    
    clock = pygame.time.Clock()
    running = True
    
    print("双人模式武器选择UI测试")
    print("按空格键切换武器模式")
    print("按R键重置神秘剑士血量")
    print("按N键重置忍者蛙血量")
    print("按ESC退出")
    
    while running:
        dt = clock.tick(60) / 1000.0
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_SPACE:
                    # 切换神秘剑士的武器模式
                    if game.dual_player_system and game.dual_player_system.mystic_swordsman:
                        game.dual_player_system.mystic_swordsman.is_ranged_mode = not game.dual_player_system.mystic_swordsman.is_ranged_mode
                        mode = "远程" if game.dual_player_system.mystic_swordsman.is_ranged_mode else "近战"
                        print(f"武器模式切换为: {mode}")
                elif event.key == pygame.K_r:
                    # 重置神秘剑士血量
                    if game.dual_player_system and game.dual_player_system.mystic_swordsman:
                        game.dual_player_system.mystic_swordsman.health = 50
                        print("神秘剑士血量重置为50")
                elif event.key == pygame.K_n:
                    # 重置忍者蛙血量
                    if game.dual_player_system and game.dual_player_system.ninja_frog:
                        game.dual_player_system.ninja_frog.health = 30
                        print("忍者蛙血量重置为30")
        
        # 更新游戏
        game.update(dt)
        
        # 渲染游戏
        game.render()
        
        pygame.display.flip()
    
    pygame.quit()

if __name__ == "__main__":
    test_dual_weapon_ui() 
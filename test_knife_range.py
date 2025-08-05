import pygame
import sys
import os
import math

# 添加src目录到路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from modules.game import Game
from modules.enemies.enemy import Enemy

def test_knife_range():
    """测试刀近战攻击范围"""
    pygame.init()
    screen = pygame.display.set_mode((1200, 800))
    pygame.display.set_caption("刀近战攻击范围测试")
    
    # 创建游戏实例
    game = Game(screen)
    
    # 启动双人模式（使用地图1，英雄2）
    game._start_game_with_selection("test1_map.tmx", "role2")
    
    # 创建一些测试敌人
    test_enemies = []
    for i in range(5):
        enemy = Enemy(600 + i * 100, 400, "slime")
        test_enemies.append(enemy)
        game.enemy_manager.enemies.add(enemy)
    
    clock = pygame.time.Clock()
    running = True
    
    print("刀近战攻击范围测试")
    print("按空格键进行近战攻击")
    print("按R键重置敌人位置")
    print("按ESC退出")
    print("攻击范围已从80像素增加到95像素")
    
    while running:
        dt = clock.tick(60) / 1000.0
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_SPACE:
                    # 进行近战攻击
                    if game.dual_player_system and game.dual_player_system.mystic_swordsman:
                        # 确保是近战模式
                        game.dual_player_system.mystic_swordsman.is_ranged_mode = False
                        # 触发近战攻击
                        game.dual_player_system.mystic_swordsman.weapon_manager.melee_attack(screen)
                        print("执行近战攻击")
                elif event.key == pygame.K_r:
                    # 重置敌人位置
                    for i, enemy in enumerate(test_enemies):
                        enemy.rect.x = 600 + i * 100
                        enemy.rect.y = 400
                        enemy.health = enemy.max_health
                    print("重置敌人位置")
        
        # 更新游戏
        game.update(dt)
        
        # 渲染游戏
        game.render()
        
        # 绘制攻击范围指示器
        if game.dual_player_system and game.dual_player_system.mystic_swordsman:
            player = game.dual_player_system.mystic_swordsman
            screen_x = player.world_x - game.camera_x + screen.get_width() // 2
            screen_y = player.world_y - game.camera_y + screen.get_height() // 2
            
            # 绘制攻击范围圆圈（95像素）
            pygame.draw.circle(screen, (255, 0, 0), (int(screen_x), int(screen_y)), 95, 2)
            
            # 绘制原来的攻击范围圆圈（80像素）作为对比
            pygame.draw.circle(screen, (255, 255, 0), (int(screen_x), int(screen_y)), 80, 1)
        
        pygame.display.flip()
    
    pygame.quit()

if __name__ == "__main__":
    test_knife_range() 
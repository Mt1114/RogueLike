import sys
import os

# 添加项目路径
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))

from modules.player import Player
from modules.enemies.enemy_manager import EnemyManager

def test_simple_death():
    """简单测试敌人死亡处理"""
    # 初始化pygame显示
    import pygame
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    
    # 创建玩家
    player = Player(400, 300, "ninja_frog")
    
    # 创建敌人管理器
    enemy_manager = EnemyManager()
    enemy_manager.set_map_boundaries(0, 0, 2000, 2000)
    
    # 创建一个测试敌人
    test_enemy = enemy_manager.spawn_enemy('ghost', 500, 300)
    
    print(f"初始状态:")
    print(f"  玩家经验值: {player.experience}")
    print(f"  玩家等级: {player.level}")
    print(f"  敌人数量: {len(enemy_manager.enemies)}")
    print(f"  敌人生命值: {test_enemy.health}")
    print(f"  敌人存活: {test_enemy.alive()}")
    
    # 模拟敌人死亡
    print(f"\n模拟敌人死亡:")
    test_enemy.health = 0
    test_enemy._alive = False
    
    print(f"  死亡后敌人存活: {test_enemy.alive()}")
    
    # 模拟游戏主循环的死亡处理
    if not test_enemy.alive():
        print(f"  处理死亡逻辑:")
        if hasattr(test_enemy, 'config') and 'exp_value' in test_enemy.config:
            exp_reward = test_enemy.config['exp_value']
            player.add_experience(exp_reward)
            print(f"    击杀 {test_enemy.type} 获得 {exp_reward} 经验值")
        
        enemy_manager.remove_enemy(test_enemy)
        print(f"    移除敌人")
    
    print(f"\n最终状态:")
    print(f"  玩家经验值: {player.experience}")
    print(f"  玩家等级: {player.level}")
    print(f"  敌人数量: {len(enemy_manager.enemies)}")
    print(f"  敌人存活: {test_enemy.alive() if test_enemy in enemy_manager.enemies else '已移除'}")

if __name__ == "__main__":
    test_simple_death() 
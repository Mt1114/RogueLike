import pygame
import sys
import time
from src.modules.game import Game

def test_key_round_system():
    """测试钥匙按波次生成的系统"""
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("钥匙波次系统测试")
    
    # 创建游戏实例
    game = Game(screen)
    
    # 模拟开始游戏（选择地图和英雄）
    game.in_main_menu = False
    game.in_map_hero_select = False
    game.load_map("test1_map.tmx")
    
    # 创建双人系统
    from src.modules.dual_player_system import DualPlayerSystem
    game.dual_player_system = DualPlayerSystem(screen, game)
    game.player = game.dual_player_system.ninja_frog
    
    # 初始化游戏管理器
    from src.modules.enemies.enemy_manager import EnemyManager
    from src.modules.items.item_manager import ItemManager
    game.enemy_manager = EnemyManager()
    game.enemy_manager.game = game
    game.item_manager = ItemManager()
    
    # 初始化钥匙管理器
    from src.modules.items.key_manager import KeyManager
    game.key_manager = KeyManager(game)
    
    print("开始测试钥匙波次系统...")
    print("波次时间安排:")
    print("- 第1波: 0:00-0:30")
    print("- 第2波: 1:30-3:00") 
    print("- 第3波: 4:00-5:00")
    
    # 模拟游戏时间流逝
    for i in range(300):  # 测试5分钟
        dt = 1.0  # 1秒时间增量
        game.game_time += dt
        
        # 更新敌人管理器（触发波次系统）
        if game.enemy_manager:
            game.enemy_manager.update(dt, game.player)
        
        # 更新钥匙管理器
        if game.key_manager:
            game.key_manager.update(dt, game.game_time)
        
        # 显示当前状态
        minutes = int(game.game_time // 60)
        seconds = int(game.game_time % 60)
        current_round = game.enemy_manager.current_round if game.enemy_manager else 0
        keys_spawned = len(game.key_manager.round_keys_spawned) if game.key_manager else 0
        
        print(f"时间: {minutes:02d}:{seconds:02d}, 当前波次: {current_round}, 已生成钥匙: {keys_spawned}")
        
        # 每30秒检查一次
        if i % 30 == 0:
            print(f"--- 30秒检查点 ---")
            print(f"钥匙管理器状态: 已生成 {keys_spawned} 把钥匙")
            print(f"当前存在的钥匙: {game.key_manager.get_key_count()} 把")
            print(f"波次钥匙记录: {game.key_manager.round_keys_spawned}")
            print()
        
        time.sleep(0.1)  # 减慢测试速度
    
    print("测试完成！")
    pygame.quit()

if __name__ == "__main__":
    test_key_round_system() 
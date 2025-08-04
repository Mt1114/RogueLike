#!/usr/bin/env python3
"""
双角色系统测试
测试忍者蛙和神秘剑士的独立控制和距离限制
"""

import pygame
import sys
import os

# 添加src目录到路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from modules.game import Game

def main():
    """主函数"""
    # 初始化Pygame
    pygame.init()
    
    # 设置窗口
    screen_width = 1200
    screen_height = 800
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("双角色系统测试")
    
    # 创建游戏实例
    game = Game(screen)
    
    # 直接启动双角色模式（跳过菜单选择）
    game.in_main_menu = False
    game.in_map_hero_select = False
    game.game_over = False
    game.game_victory = False
    game.paused = False
    
    # 加载地图
    game.load_map("simple_map")
    
    # 获取地图尺寸
    map_width, map_height = game.map_manager.get_map_size()
    
    # 创建双角色系统
    from modules.dual_player_system import DualPlayerSystem
    game.dual_player_system = DualPlayerSystem(screen, game)
    
    # 设置两个角色的世界坐标为地图中心
    center_x = map_width // 2
    center_y = map_height // 2
    
    # 忍者蛙稍微偏左，神秘剑士稍微偏右
    game.dual_player_system.ninja_frog.world_x = center_x - 100
    game.dual_player_system.ninja_frog.world_y = center_y
    game.dual_player_system.mystic_swordsman.world_x = center_x + 100
    game.dual_player_system.mystic_swordsman.world_y = center_y
    
    # 为了兼容性，设置player为忍者蛙（主要角色）
    game.player = game.dual_player_system.ninja_frog
    
    # 初始化游戏管理器
    from modules.enemies.enemy_manager import EnemyManager
    from modules.items.item_manager import ItemManager
    from modules.items.ammo_supply_manager import AmmoSupplyManager
    from modules.items.health_supply_manager import HealthSupplyManager
    
    game.enemy_manager = EnemyManager()
    game.enemy_manager.set_difficulty("normal")
    game.item_manager = ItemManager()
    game.ammo_supply_manager = AmmoSupplyManager(game)
    game.health_supply_manager = HealthSupplyManager(game)
    
    # 初始化钥匙管理器
    from modules.items.key_manager import KeyManager
    game.key_manager = KeyManager(game)
    
    # 生成逃生门
    from modules.items.escape_door import EscapeDoor
    door_x = map_width - 100
    door_y = 100
    game.escape_door = EscapeDoor(door_x, door_y)
    
    # 设置边界
    game._set_map_boundaries()
    
    # 初始化玩家移动组件的碰撞数据
    if game.map_manager and game.map_manager.current_map:
        walls = game.map_manager.get_collision_tiles()
        tile_width, tile_height = game.map_manager.get_tile_size()
        
        # 设置两个角色的碰撞数据
        if game.dual_player_system:
            if hasattr(game.dual_player_system.ninja_frog, 'movement'):
                game.dual_player_system.ninja_frog.movement.set_collision_tiles(walls, tile_width, tile_height)
            if hasattr(game.dual_player_system.mystic_swordsman, 'movement'):
                game.dual_player_system.mystic_swordsman.movement.set_collision_tiles(walls, tile_width, tile_height)
    
    # 初始化小地图
    from modules.minimap import Minimap
    game.minimap = Minimap(map_width, map_height, screen_width, screen_height)
    
    # 重置游戏状态
    game.game_time = 0
    game.kill_num = 0
    game.level = 1
    

    
    # 设置相机位置为两个角色的中心位置
    center_x, center_y = game.dual_player_system.get_center_position()
    game.camera_x = center_x
    game.camera_y = center_y
    
    # 播放背景音乐
    from modules.resource_manager import resource_manager
    resource_manager.play_music("background", loops=-1)
    
    # 游戏主循环
    clock = pygame.time.Clock()
    running = True
    
    print("双角色系统测试开始！")
    print("控制说明：")
    print("忍者蛙：WASD移动，鼠标控制光源方向")
    print("神秘剑士：方向键移动，数字键盘2486攻击")
    print("两个角色不能离得太远，会自动限制距离")
    
    while running:
        dt = clock.tick(60) / 1000.0  # 转换为秒
        
        # 处理事件
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                    
            # 处理游戏事件
            game.handle_event(event)
        
        # 更新游戏
        game.update(dt)
        
        # 渲染游戏
        game.render()
        
        # 显示控制说明
        font = pygame.font.Font(None, 24)
        instructions = [
            "忍者蛙: WASD移动, 鼠标控制光源",
            "神秘剑士: 方向键移动, 数字键2486攻击",
            "ESC退出"
        ]
        
        for i, instruction in enumerate(instructions):
            text_surface = font.render(instruction, True, (255, 255, 255))
            screen.blit(text_surface, (10, 10 + i * 25))
        
        # 显示角色状态
        ninja_health = game.dual_player_system.ninja_frog.health
        mystic_health = game.dual_player_system.mystic_swordsman.health
        
        ninja_text = font.render(f"忍者蛙生命: {ninja_health}", True, (0, 255, 0))
        mystic_text = font.render(f"神秘剑士生命: {mystic_health}", True, (255, 0, 0))
        
        screen.blit(ninja_text, (10, screen_height - 60))
        screen.blit(mystic_text, (10, screen_height - 35))
        
        pygame.display.flip()
    
    # 清理
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main() 
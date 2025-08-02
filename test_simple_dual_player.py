#!/usr/bin/env python3
"""
简单双角色系统测试
只测试基本的双角色控制和渲染
"""

import pygame
import sys
import os

# 添加src目录到路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def main():
    """主函数"""
    # 初始化Pygame
    pygame.init()
    
    # 设置窗口
    screen_width = 1200
    screen_height = 800
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("简单双角色系统测试")
    
    # 创建游戏实例
    from modules.game import Game
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
    
    # 设置相机位置为两个角色的中心位置
    center_x, center_y = game.dual_player_system.get_center_position()
    game.camera_x = center_x
    game.camera_y = center_y
    
    # 游戏主循环
    clock = pygame.time.Clock()
    running = True
    
    print("简单双角色系统测试开始！")
    print("控制说明：")
    print("忍者蛙：WASD移动，鼠标控制光源方向")
    print("神秘剑士：方向键移动，数字键盘2486攻击")
    print("两个角色不能离得太远，会自动限制距离")
    print("ESC退出")
    
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
        
        # 显示角色位置信息
        ninja_pos = font.render(f"忍者蛙: ({game.dual_player_system.ninja_frog.world_x:.0f}, {game.dual_player_system.ninja_frog.world_y:.0f})", True, (0, 255, 0))
        mystic_pos = font.render(f"神秘剑士: ({game.dual_player_system.mystic_swordsman.world_x:.0f}, {game.dual_player_system.mystic_swordsman.world_y:.0f})", True, (255, 0, 0))
        
        screen.blit(ninja_pos, (10, screen_height - 90))
        screen.blit(mystic_pos, (10, screen_height - 65))
        
        pygame.display.flip()
    
    # 清理
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main() 
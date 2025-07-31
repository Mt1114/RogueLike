import pygame
import sys
import os
import time

# 添加项目路径
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))

from modules.player import Player
from modules.enemies.enemy_manager import EnemyManager

def test_round_exp_system():
    """测试新的波次系统和经验值系统"""
    pygame.init()
    screen = pygame.display.set_mode((1200, 800))
    pygame.display.set_caption("波次和经验值系统测试")
    
    # 创建玩家
    player = Player(600, 400, "ninja_frog")
    
    # 创建敌人管理器
    enemy_manager = EnemyManager()
    enemy_manager.set_map_boundaries(0, 0, 2000, 2000)
    
    # 字体
    font = pygame.font.Font(None, 24)
    
    clock = pygame.time.Clock()
    running = True
    
    # 时间控制
    time_scale = 1.0  # 时间加速倍数
    paused = False
    
    # 记录初始状态
    initial_exp = player.experience
    initial_level = player.level
    
    while running:
        dt = clock.tick(60) / 1000.0
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_SPACE:
                    paused = not paused
                elif event.key == pygame.K_1:
                    time_scale = 1.0
                elif event.key == pygame.K_2:
                    time_scale = 2.0
                elif event.key == pygame.K_3:
                    time_scale = 5.0
                elif event.key == pygame.K_4:
                    time_scale = 10.0
        
        if not paused:
            actual_dt = dt * time_scale
            player.update(actual_dt)
            player.update_weapons(actual_dt)
            enemy_manager.update(actual_dt, player)
        
        # 清屏
        screen.fill((30, 30, 30))
        
        # 渲染玩家
        player.render(screen)
        
        # 渲染武器和投射物
        player.render_weapons(screen, 0, 0)
        
        # 渲染敌人管理器
        enemy_manager.render(screen, 0, 0, screen.get_width() // 2, screen.get_height() // 2)
        
        # 显示信息
        game_time = enemy_manager.game_time
        minutes = int(game_time // 60)
        seconds = int(game_time % 60)
        
        info_text = [
            "波次和经验值系统测试",
            "",
            "波次安排:",
            "Round 1: 0:00-0:30 (5秒生成一个，总共24个)",
            "休息期: 0:30-1:30",
            "Round 2: 1:30-3:00 (3秒生成一个，总共40个)",
            "休息期: 3:00-4:00",
            "Round 3: 4:00-5:00 (2秒生成一个，总共120个)",
            "游戏结束: 5:00后",
            "",
            "经验值系统:",
            "10级前: 每5个敌人升一级",
            "10级后: 每10个敌人升一级",
            "",
            "控制:",
            "空格: 暂停/继续",
            "1-4: 时间加速 (1x, 2x, 5x, 10x)",
            "ESC: 退出"
        ]
        
        for i, text in enumerate(info_text):
            text_surface = font.render(text, True, (255, 255, 255))
            screen.blit(text_surface, (10, 10 + i * 25))
        
        # 显示当前状态
        status_text = [
            f"游戏时间: {minutes:02d}:{seconds:02d}",
            f"时间加速: {time_scale}x",
            f"当前波次: {enemy_manager.current_round}",
            f"生成间隔: {enemy_manager.spawn_interval:.1f}秒",
            f"敌人数量: {len(enemy_manager.enemies)}",
            f"已生成敌人: {getattr(enemy_manager, 'enemies_spawned_this_round', 0)}",
            f"最大敌人数: {getattr(enemy_manager, 'max_enemies_for_round', '无限制')}",
            f"状态: {'暂停' if paused else '运行中'}"
        ]
        
        for i, text in enumerate(status_text):
            color = (0, 255, 0) if not paused else (255, 255, 0)
            text_surface = font.render(text, True, color)
            screen.blit(text_surface, (10, 400 + i * 25))
        
        # 显示经验值信息
        exp_info = [
            f"当前等级: {player.level}",
            f"当前经验值: {player.experience}",
            f"下一级所需: {player.exp_to_next_level}",
            f"经验值变化: {player.experience - initial_exp}",
            f"等级变化: {player.level - initial_level}",
            f"经验倍率: {player.progression.exp_multiplier:.2f}"
        ]
        
        for i, text in enumerate(exp_info):
            text_surface = font.render(text, True, (255, 255, 0))
            screen.blit(text_surface, (10, 600 + i * 25))
        
        # 显示升级进度
        if player.level < 10:
            enemies_needed = 5 - (player.experience // 20)
            progress_text = f"10级前进度: 还需{enemies_needed}个敌人升级"
        else:
            enemies_needed = 10 - (player.experience // 20)
            progress_text = f"10级后进度: 还需{enemies_needed}个敌人升级"
        
        progress_surface = font.render(progress_text, True, (0, 255, 255))
        screen.blit(progress_surface, (10, 750))
        
        pygame.display.flip()
    
    pygame.quit()
    
    # 打印最终结果
    final_exp = player.experience
    final_level = player.level
    print(f"\n=== 波次和经验值系统测试结果 ===")
    print(f"初始等级: {initial_level}")
    print(f"最终等级: {final_level}")
    print(f"等级变化: {final_level - initial_level}")
    print(f"初始经验值: {initial_exp}")
    print(f"最终经验值: {final_exp}")
    print(f"经验值变化: {final_exp - initial_exp}")
    
    # 计算击杀效率
    if final_level > initial_level:
        exp_gained = final_exp - initial_exp + (final_level - initial_level) * 100
        enemies_killed = exp_gained // 20
        print(f"估计击杀敌人数: {enemies_killed}")
        print(f"平均每级击杀数: {enemies_killed / (final_level - initial_level):.1f}")

if __name__ == "__main__":
    test_round_exp_system() 
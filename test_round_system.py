import pygame
import sys
import os
import math

# 添加项目路径
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))

from modules.player import Player
from modules.enemies.enemy_manager import EnemyManager

def test_round_system():
    """测试波次系统"""
    pygame.init()
    screen = pygame.display.set_mode((1200, 800))
    pygame.display.set_caption("波次系统测试")
    
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
            # 更新游戏时间（加速）
            actual_dt = dt * time_scale
            
            # 更新玩家和敌人管理器
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
        time_text = f"游戏时间: {minutes:02d}:{seconds:02d}"
        
        info_text = [
            "波次系统测试",
            "",
            "波次安排:",
            "Round 1: 0:00-0:30 (正常)",
            "休息期: 0:30-1:30",
            "Round 2: 1:30-3:00 (速度+50%, 属性+20%)",
            "休息期: 3:00-4:00",
            "Round 3: 4:00-5:00 (速度+100%, 攻击+50%)",
            "游戏结束: 5:00后",
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
            f"状态: {'暂停' if paused else '运行中'}"
        ]
        
        for i, text in enumerate(status_text):
            color = (0, 255, 0) if not paused else (255, 255, 0)
            text_surface = font.render(text, True, color)
            screen.blit(text_surface, (10, 400 + i * 25))
        
        # 显示波次属性
        if hasattr(enemy_manager, 'health_multiplier') and hasattr(enemy_manager, 'damage_multiplier'):
            attr_text = [
                f"生命值倍数: {enemy_manager.health_multiplier:.1f}",
                f"攻击力倍数: {enemy_manager.damage_multiplier:.1f}"
            ]
            
            for i, text in enumerate(attr_text):
                text_surface = font.render(text, True, (255, 255, 0))
                screen.blit(text_surface, (10, 550 + i * 25))
        
        # 显示武器信息
        weapon_info = []
        for i, weapon in enumerate(player.weapons):
            if hasattr(weapon, 'ammo'):
                weapon_info.append(f"武器{i+1}: {weapon.type} (子弹: {weapon.ammo}/{weapon.max_ammo})")
            else:
                weapon_info.append(f"武器{i+1}: {weapon.type} (等级{weapon.level})")
        
        for i, text in enumerate(weapon_info):
            text_surface = font.render(text, True, (0, 255, 255))
            screen.blit(text_surface, (10, 600 + i * 25))
        
        pygame.display.flip()
    
    pygame.quit()

if __name__ == "__main__":
    test_round_system() 
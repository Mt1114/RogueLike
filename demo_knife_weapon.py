import pygame
import sys
import os
import math

# 添加项目路径
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))

from modules.weapons.types.knife import Knife
from modules.player import Player

def demo_knife_weapon():
    """演示刀武器功能"""
    pygame.init()
    screen = pygame.display.set_mode((1200, 800))
    pygame.display.set_caption("刀武器演示")
    
    # 创建玩家
    player = Player(600, 400, "ninja_frog")
    
    # 添加刀武器
    player.add_weapon('knife')
    
    # 字体
    font = pygame.font.Font(None, 24)
    
    clock = pygame.time.Clock()
    running = True
    
    # 演示信息
    demo_info = [
        "刀武器演示",
        "",
        "功能特性:",
        "- 武器图像: knife_32x32.png",
        "- 攻击特效: swing02.png",
        "- 左键: 远程投掷飞刀",
        "- 右键: 近战攻击",
        "- 攻击特效动画",
        "- 飞刀旋转和缩放动画",
        "",
        "控制:",
        "鼠标左键: 远程攻击",
        "鼠标右键: 近战攻击",
        "ESC: 退出"
    ]
    
    while running:
        dt = clock.tick(60) / 1000.0
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # 左键远程攻击
                    # 处理玩家事件（包括射击）
                    player.handle_event(event)
                    print("左键远程攻击！")
                elif event.button == 3:  # 右键近战攻击
                    # 处理玩家事件（包括近战攻击）
                    player.handle_event(event)
                    print("右键近战攻击！")
        
        # 更新玩家和武器
        player.update(dt)
        player.update_weapons(dt)
        
        # 清屏
        screen.fill((30, 30, 30))
        
        # 渲染玩家
        player.render(screen)
        
        # 渲染武器和投射物
        player.render_weapons(screen, 0, 0)
        
        # 显示演示信息
        for i, text in enumerate(demo_info):
            text_surface = font.render(text, True, (255, 255, 255))
            screen.blit(text_surface, (10, 10 + i * 25))
        
        # 显示投射物数量
        for weapon in player.weapons:
            if hasattr(weapon, 'projectiles'):
                projectile_count = len(weapon.projectiles)
                count_text = font.render(f"活跃飞刀: {projectile_count}", True, (0, 255, 0))
                screen.blit(count_text, (10, 400))
        
        # 显示鼠标位置
        mouse_x, mouse_y = pygame.mouse.get_pos()
        mouse_text = font.render(f"鼠标位置: ({mouse_x}, {mouse_y})", True, (255, 255, 0))
        screen.blit(mouse_text, (10, 430))
        
        # 显示武器信息
        weapon_info = [
            f"武器类型: {player.weapons[0].type if player.weapons else '无'}",
            f"武器等级: {player.weapons[0].level if player.weapons else 0}",
            f"攻击速度: {player.weapons[0].current_stats.get('attack_speed', 0):.1f}" if player.weapons else "攻击速度: 0"
        ]
        
        for i, text in enumerate(weapon_info):
            text_surface = font.render(text, True, (0, 255, 255))
            screen.blit(text_surface, (10, 460 + i * 25))
        
        pygame.display.flip()
    
    pygame.quit()

if __name__ == "__main__":
    demo_knife_weapon() 
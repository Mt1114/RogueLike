import pygame
import sys
import os
import math

# 添加项目路径
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))

from modules.weapons.types.bullet import BulletWeapon
from modules.player import Player

def demo_gun_weapon():
    """演示枪械武器功能"""
    pygame.init()
    screen = pygame.display.set_mode((1200, 800))
    pygame.display.set_caption("枪械武器演示")
    
    # 创建玩家（现在会自动获得手枪作为初始武器）
    player = Player(600, 400, "ninja_frog")
    
    # 字体
    font = pygame.font.Font(None, 24)
    
    clock = pygame.time.Clock()
    running = True
    
    # 演示信息
    demo_info = [
        "枪械武器演示",
        "",
        "功能特性:",
        "- 初始武器：手枪 (gun.png)",
        "- 左键射击",
        "- 鼠标方向瞄准",
        "- 快速子弹飞行 (600-800速度)",
        "- 武器上抬30度",
        "- 子弹投射物 (bullet_8x8.png)",
        "",
        "控制:",
        "鼠标左键: 射击",
        "鼠标: 瞄准方向",
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
                if event.button == 1:  # 左键射击
                    # 处理玩家事件（包括射击）
                    player.handle_event(event)
                    print("左键射击！")
        
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
                count_text = font.render(f"活跃子弹: {projectile_count}", True, (0, 255, 0))
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
    demo_gun_weapon() 
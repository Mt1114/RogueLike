import pygame
import sys
import os
import math

# 添加项目路径
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))

from modules.weapons.types.bullet import BulletWeapon
from modules.player import Player

def demo_bullet_weapon():
    """演示子弹武器功能"""
    pygame.init()
    screen = pygame.display.set_mode((1200, 800))
    pygame.display.set_caption("子弹武器演示")
    
    # 创建玩家
    player = Player(600, 400, "ninja_frog")
    
    # 添加子弹武器
    player.add_weapon('bullet')
    
    # 字体
    font = pygame.font.Font(None, 24)
    
    clock = pygame.time.Clock()
    running = True
    
    # 演示信息
    demo_info = [
        "子弹武器演示",
        "",
        "功能特性:",
        "- 武器上抬30度射击",
        "- 直线飞行的子弹",
        "- 支持穿透敌人",
        "- 平滑的旋转动画",
        "",
        "控制:",
        "空格键: 发射子弹",
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
                elif event.key == pygame.K_SPACE:
                    # 空格键发射子弹
                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    screen_center_x = screen.get_width() // 2
                    screen_center_y = screen.get_height() // 2
                    
                    # 计算方向
                    direction_x = mouse_x - screen_center_x
                    direction_y = mouse_y - screen_center_y
                    
                    # 标准化方向向量
                    length = math.sqrt(direction_x**2 + direction_y**2)
                    if length > 0:
                        direction_x /= length
                        direction_y /= length
                        
                        # 发射子弹
                        for weapon in player.weapons:
                            if weapon.type == 'bullet':
                                weapon._perform_attack(direction_x, direction_y)
                                print(f"发射子弹！方向: ({direction_x:.2f}, {direction_y:.2f})")
        
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
                screen.blit(count_text, (10, 300))
        
        # 显示鼠标位置
        mouse_x, mouse_y = pygame.mouse.get_pos()
        mouse_text = font.render(f"鼠标位置: ({mouse_x}, {mouse_y})", True, (255, 255, 0))
        screen.blit(mouse_text, (10, 330))
        
        pygame.display.flip()
    
    pygame.quit()

if __name__ == "__main__":
    demo_bullet_weapon() 
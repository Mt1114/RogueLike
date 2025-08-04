import pygame
import sys
import os
import math

# 添加src目录到路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from modules.weapons.types.bullet import BulletWeapon
from modules.player import Player

# 初始化Pygame
pygame.init()

# 创建屏幕
screen_width = 1200
screen_height = 800
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("扇形子弹测试")

# 创建模拟玩家
class MockPlayer:
    def __init__(self):
        self.world_x = screen_width // 2
        self.world_y = screen_height // 2
        self.hero_type = "role2"  # 神秘剑客

player = MockPlayer()

# 创建子弹武器
bullet_weapon = BulletWeapon(player)

# 游戏主循环
clock = pygame.time.Clock()
running = True

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
                bullet_weapon.manual_attack(screen)
    
    # 更新武器
    bullet_weapon.update(dt)
    
    # 清屏
    screen.fill((50, 50, 50))
    
    # 绘制玩家位置
    pygame.draw.circle(screen, (0, 255, 0), (player.world_x, player.world_y), 10)
    
    # 渲染武器和子弹
    bullet_weapon.render(screen, 0, 0)
    
    # 显示信息
    font = pygame.font.Font(None, 36)
    info_text = f"子弹数量: {bullet_weapon.ammo}"
    text_surface = font.render(info_text, True, (255, 255, 255))
    screen.blit(text_surface, (10, 10))
    
    instruction_text = "点击鼠标左键进行扇形射击"
    instruction_surface = font.render(instruction_text, True, (255, 255, 255))
    screen.blit(instruction_surface, (10, 50))
    
    pygame.display.flip()

pygame.quit()
sys.exit() 
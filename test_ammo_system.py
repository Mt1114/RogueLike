import pygame
import sys
import os
import math

# 添加项目路径
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))

from modules.player import Player
from modules.items.ammo_supply import AmmoSupply

def test_ammo_system():
    """测试子弹系统"""
    pygame.init()
    screen = pygame.display.set_mode((1200, 800))
    pygame.display.set_caption("子弹系统测试")
    
    # 创建玩家（会自动获得手枪和刀）
    player = Player(600, 400, "ninja_frog")
    
    # 创建一些弹药补给
    ammo_supplies = [
        AmmoSupply(200, 200),
        AmmoSupply(400, 300),
        AmmoSupply(800, 500),
        AmmoSupply(1000, 200)
    ]
    
    # 字体
    font = pygame.font.Font(None, 24)
    
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
                if event.button == 1:  # 左键远程攻击
                    # 处理玩家事件（包括射击）
                    player.handle_event(event)
                    print("左键远程攻击（手枪）！")
                elif event.button == 3:  # 右键近战攻击
                    # 处理玩家事件（包括近战攻击）
                    player.handle_event(event)
                    print("右键近战攻击（刀）！")
        
        # 更新玩家和武器
        player.update(dt)
        player.update_weapons(dt)
        
        # 更新投射物
        for weapon in player.weapons:
            if hasattr(weapon, 'projectiles'):
                for projectile in weapon.projectiles:
                    projectile.update(dt)
        
        # 更新弹药补给
        for supply in ammo_supplies[:]:
            if not supply.update(dt):
                ammo_supplies.remove(supply)
        
        # 检测玩家与弹药补给的碰撞
        for supply in ammo_supplies[:]:
            # 简单的距离检测
            dx = player.world_x - supply.world_x
            dy = player.world_y - supply.world_y
            distance = math.sqrt(dx**2 + dy**2)
            
            if distance < 30:  # 拾取范围
                if supply.on_pickup(player):
                    ammo_supplies.remove(supply)
                    print("拾取弹药补给！")
        
        # 清屏
        screen.fill((30, 30, 30))
        
        # 渲染玩家
        player.render(screen)
        
        # 渲染武器和投射物
        player.render_weapons(screen, 0, 0)
        
        # 渲染弹药补给
        for supply in ammo_supplies:
            supply.render(screen, 0, 0, screen.get_width() // 2, screen.get_height() // 2)
        
        # 显示信息
        info_text = [
            "子弹系统测试",
            "",
            "功能特性:",
            "- 手枪有子弹数量限制",
            "- 补给图标使用子弹图像",
            "- 枪械子弹共用一套补给系统",
            "",
            "测试方法:",
            "1. 左键射击消耗子弹",
            "2. 接触黄色子弹补给",
            "3. 观察子弹数量变化",
            "4. 子弹用完时无法射击",
            "",
            "控制:",
            "鼠标左键: 射击（消耗子弹）",
            "鼠标右键: 近战攻击（刀）",
            "ESC: 退出"
        ]
        
        for i, text in enumerate(info_text):
            text_surface = font.render(text, True, (255, 255, 255))
            screen.blit(text_surface, (10, 10 + i * 25))
        
        # 显示武器信息
        weapon_info = []
        for i, weapon in enumerate(player.weapons):
            if hasattr(weapon, 'ammo'):
                weapon_info.append(f"武器{i+1}: {weapon.type} (子弹: {weapon.ammo}/{weapon.max_ammo})")
            else:
                weapon_info.append(f"武器{i+1}: {weapon.type} (等级{weapon.level})")
        
        for i, text in enumerate(weapon_info):
            text_surface = font.render(text, True, (0, 255, 255))
            screen.blit(text_surface, (10, 400 + i * 25))
        
        # 显示投射物数量
        total_projectiles = 0
        for weapon in player.weapons:
            if hasattr(weapon, 'projectiles'):
                total_projectiles += len(weapon.projectiles)
        count_text = font.render(f"活跃投射物: {total_projectiles}", True, (0, 255, 0))
        screen.blit(count_text, (10, 450))
        
        # 显示补给数量
        supply_count = len(ammo_supplies)
        supply_text = font.render(f"弹药补给: {supply_count}", True, (255, 255, 0))
        screen.blit(supply_text, (10, 480))
        
        # 显示鼠标位置
        mouse_x, mouse_y = pygame.mouse.get_pos()
        mouse_text = font.render(f"鼠标位置: ({mouse_x}, {mouse_y})", True, (255, 255, 0))
        screen.blit(mouse_text, (10, 510))
        
        pygame.display.flip()
    
    pygame.quit()

if __name__ == "__main__":
    test_ammo_system() 
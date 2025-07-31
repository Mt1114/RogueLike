import pygame
import sys
import os
import math

# 添加项目路径
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))

from modules.weapons.types.knife import Knife
from modules.player import Player

def test_knife_weapon():
    """测试刀武器功能"""
    pygame.init()
    screen = pygame.display.set_mode((1200, 800))
    pygame.display.set_caption("刀武器测试")
    
    # 创建玩家
    player = Player(600, 400, "ninja_frog")
    
    # 添加刀武器
    player.add_weapon('knife')
    
    # 创建一些测试敌人
    class TestEnemy:
        def __init__(self, x, y):
            self.rect = pygame.Rect(x, y, 32, 32)
            self.health = 100
            self.max_health = 100
            self.invincible_timer = 0
            
        def take_damage(self, damage):
            self.health -= damage
            print(f"敌人受到 {damage} 点伤害，剩余血量: {self.health}")
            
        def alive(self):
            return self.health > 0
    
    enemies = [
        TestEnemy(200, 200),
        TestEnemy(400, 300),
        TestEnemy(800, 500),
        TestEnemy(1000, 200)
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
                    print("左键远程攻击！")
                elif event.button == 3:  # 右键近战攻击
                    # 处理玩家事件（包括近战攻击）
                    player.handle_event(event)
                    print("右键近战攻击！")
        
        # 更新玩家和武器
        player.update(dt)
        player.update_weapons(dt)
        
        # 更新投射物
        for weapon in player.weapons:
            if hasattr(weapon, 'projectiles'):
                for projectile in weapon.projectiles:
                    projectile.update(dt)
                    
                    # 检测与敌人的碰撞
                    for enemy in enemies[:]:  # 使用切片避免在迭代时修改列表
                        if enemy.alive():
                            # 简单的距离检测
                            dx = enemy.rect.centerx - projectile.world_x
                            dy = enemy.rect.centery - projectile.world_y
                            distance = math.sqrt(dx**2 + dy**2)
                            
                            if distance < 20:  # 碰撞半径
                                should_destroy = projectile.on_collision(enemy, enemies)
                                if should_destroy:
                                    projectile.kill()
                                if not enemy.alive():
                                    enemies.remove(enemy)
                                    print(f"敌人被消灭！")
        
        # 清屏
        screen.fill((30, 30, 30))
        
        # 渲染玩家
        player.render(screen)
        
        # 渲染武器和投射物
        player.render_weapons(screen, 0, 0)
        
        # 渲染敌人
        for enemy in enemies:
            if enemy.alive():
                pygame.draw.rect(screen, (255, 0, 0), enemy.rect)
                # 显示血量
                health_text = font.render(f"{enemy.health}", True, (255, 255, 255))
                screen.blit(health_text, (enemy.rect.x, enemy.rect.y - 20))
        
        # 显示信息
        info_text = [
            "刀武器测试",
            "",
            "功能特性:",
            "- 武器图像: knife_32x32.png",
            "- 攻击特效: swing02.png",
            "- 左键: 远程投掷",
            "- 右键: 近战攻击",
            "- 攻击特效动画",
            "",
            "控制:",
            "鼠标左键: 远程攻击",
            "鼠标右键: 近战攻击",
            "ESC: 退出"
        ]
        
        for i, text in enumerate(info_text):
            text_surface = font.render(text, True, (255, 255, 255))
            screen.blit(text_surface, (10, 10 + i * 25))
        
        # 显示投射物数量
        for weapon in player.weapons:
            if hasattr(weapon, 'projectiles'):
                projectile_count = len(weapon.projectiles)
                count_text = font.render(f"活跃飞刀: {projectile_count}", True, (0, 255, 0))
                screen.blit(count_text, (10, 300))
        
        # 显示鼠标位置
        mouse_x, mouse_y = pygame.mouse.get_pos()
        mouse_text = font.render(f"鼠标位置: ({mouse_x}, {mouse_y})", True, (255, 255, 0))
        screen.blit(mouse_text, (10, 330))
        
        # 显示武器信息
        weapon_info = [
            f"武器类型: {player.weapons[0].type if player.weapons else '无'}",
            f"武器等级: {player.weapons[0].level if player.weapons else 0}",
            f"攻击速度: {player.weapons[0].current_stats.get('attack_speed', 0):.1f}" if player.weapons else "攻击速度: 0"
        ]
        
        for i, text in enumerate(weapon_info):
            text_surface = font.render(text, True, (0, 255, 255))
            screen.blit(text_surface, (10, 360 + i * 25))
        
        pygame.display.flip()
    
    pygame.quit()

if __name__ == "__main__":
    test_knife_weapon() 
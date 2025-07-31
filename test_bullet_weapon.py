import pygame
import sys
import os
import math

# 添加项目路径
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))

from modules.weapons.types.bullet import BulletWeapon, BulletProjectile
from modules.player import Player

def test_bullet_weapon():
    """测试子弹武器功能"""
    pygame.init()
    screen = pygame.display.set_mode((1200, 800))
    pygame.display.set_caption("子弹武器测试")
    
    # 创建玩家
    player = Player(600, 400, "ninja_frog")
    
    # 添加子弹武器
    player.add_weapon('bullet')
    
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
                                print(f"发射子弹，方向: ({direction_x:.2f}, {direction_y:.2f})")
        
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
        screen.fill((50, 50, 50))
        
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
            f"玩家位置: ({player.world_x:.1f}, {player.world_y:.1f})",
            f"武器数量: {len(player.weapons)}",
            f"敌人数量: {len(enemies)}",
            "",
            "控制说明:",
            "空格键: 发射子弹",
            "鼠标: 瞄准方向",
            "ESC: 退出"
        ]
        
        for i, text in enumerate(info_text):
            text_surface = font.render(text, True, (255, 255, 255))
            screen.blit(text_surface, (10, 10 + i * 25))
        
        # 显示投射物数量
        for weapon in player.weapons:
            if hasattr(weapon, 'projectiles'):
                projectile_count = len(weapon.projectiles)
                count_text = font.render(f"投射物数量: {projectile_count}", True, (0, 255, 0))
                screen.blit(count_text, (10, 200))
        
        pygame.display.flip()
    
    pygame.quit()

if __name__ == "__main__":
    test_bullet_weapon() 
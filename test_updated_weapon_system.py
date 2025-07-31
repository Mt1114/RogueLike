import pygame
import sys
import os
import math

# 添加项目路径
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))

from modules.player import Player

def test_updated_weapon_system():
    """测试更新后的武器系统"""
    pygame.init()
    screen = pygame.display.set_mode((1200, 800))
    pygame.display.set_caption("更新后的武器系统测试")
    
    # 创建玩家（会自动获得手枪和刀）
    player = Player(600, 400, "ninja_frog")
    
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
            "更新后的武器系统测试",
            "",
            "功能特性:",
            "- 远程武器: 手枪 (左键)",
            "- 近战武器: 刀 (右键)",
            "- 手枪: 根据鼠标位置调整位置和朝向",
            "- 刀: 近战攻击，无特效",
            "",
            "手枪特性:",
            "- 鼠标在左，枪在玩家左侧",
            "- 鼠标在右，枪在玩家右侧",
            "- 鼠标在上，枪口朝上",
            "- 鼠标在下，枪口朝下",
            "",
            "控制:",
            "鼠标左键: 远程攻击（手枪）",
            "鼠标右键: 近战攻击（刀）",
            "ESC: 退出"
        ]
        
        for i, text in enumerate(info_text):
            text_surface = font.render(text, True, (255, 255, 255))
            screen.blit(text_surface, (10, 10 + i * 25))
        
        # 显示武器信息
        weapon_info = []
        for i, weapon in enumerate(player.weapons):
            weapon_info.append(f"武器{i+1}: {weapon.type} (等级{weapon.level})")
        
        for i, text in enumerate(weapon_info):
            text_surface = font.render(text, True, (0, 255, 255))
            screen.blit(text_surface, (10, 450 + i * 25))
        
        # 显示投射物数量
        total_projectiles = 0
        for weapon in player.weapons:
            if hasattr(weapon, 'projectiles'):
                total_projectiles += len(weapon.projectiles)
        count_text = font.render(f"活跃投射物: {total_projectiles}", True, (0, 255, 0))
        screen.blit(count_text, (10, 500))
        
        # 显示鼠标位置
        mouse_x, mouse_y = pygame.mouse.get_pos()
        mouse_text = font.render(f"鼠标位置: ({mouse_x}, {mouse_y})", True, (255, 255, 0))
        screen.blit(mouse_text, (10, 530))
        
        pygame.display.flip()
    
    pygame.quit()

if __name__ == "__main__":
    test_updated_weapon_system() 
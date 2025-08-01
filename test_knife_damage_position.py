import pygame
import sys
import os

# 添加项目路径
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))

from modules.player import Player
from modules.weapons.types.knife import Knife
from modules.enemies.enemy import Enemy

def test_knife_damage_position():
    """测试刀武器的伤害检测位置"""
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("刀伤害位置测试")
    
    # 创建玩家
    player = Player(400, 300, "ninja_frog")
    
    # 创建刀武器
    knife = Knife(player)
    knife.player = player
    
    # 创建测试敌人
    enemy = Enemy(450, 300, "slime")  # 在玩家右侧50像素
    enemy.health = 100
    
    # 字体
    font = pygame.font.Font(None, 24)
    
    clock = pygame.time.Clock()
    running = True
    
    # 测试状态
    test_attack = False
    mouse_x, mouse_y = 400, 300
    
    print("刀伤害位置测试")
    print("控制:")
    print("  鼠标移动: 改变攻击方向")
    print("  空格: 执行攻击")
    print("  ESC: 退出")
    
    while running:
        dt = clock.tick(60) / 1000.0
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_SPACE:
                    # 执行攻击
                    if not test_attack:
                        # 计算方向（从玩家到鼠标）
                        dx = mouse_x - player.world_x
                        dy = mouse_y - player.world_y
                        distance = (dx**2 + dy**2)**0.5
                        if distance > 0:
                            direction_x = dx / distance
                            direction_y = dy / distance
                        else:
                            direction_x = 1
                            direction_y = 0
                        
                        # 计算攻击位置
                        attack_x = player.world_x + direction_x * 32
                        attack_y = player.world_y + direction_y * 32
                        
                        print(f"玩家位置: ({player.world_x:.1f}, {player.world_y:.1f})")
                        print(f"攻击位置: ({attack_x:.1f}, {attack_y:.1f})")
                        print(f"敌人位置: ({enemy.rect.x:.1f}, {enemy.rect.y:.1f})")
                        print(f"攻击方向: ({direction_x:.2f}, {direction_y:.2f})")
                        
                        # 计算到攻击位置的距离
                        dx_to_attack = enemy.rect.x - attack_x
                        dy_to_attack = enemy.rect.y - attack_y
                        distance_to_attack = (dx_to_attack**2 + dy_to_attack**2)**0.5
                        
                        print(f"敌人到攻击位置距离: {distance_to_attack:.1f}")
                        print(f"敌人到玩家距离: {((enemy.rect.x - player.world_x)**2 + (enemy.rect.y - player.world_y)**2)**0.5:.1f}")
                        
                        # 执行攻击
                        knife._perform_melee_attack(direction_x, direction_y)
                        test_attack = True
                        print(f"敌人血量: {enemy.health}")
            elif event.type == pygame.MOUSEMOTION:
                mouse_x, mouse_y = event.pos
        
        # 更新武器
        knife.update(dt)
        
        # 清屏
        screen.fill((30, 30, 30))
        
        # 渲染玩家（简化）
        player_rect = pygame.Rect(380, 280, 40, 40)
        pygame.draw.rect(screen, (0, 255, 0), player_rect)
        
        # 渲染敌人（简化）
        enemy_rect = pygame.Rect(430, 280, 40, 40)
        pygame.draw.rect(screen, (255, 0, 0), enemy_rect)
        
        # 渲染攻击特效
        if knife.attack_effect and knife.effect_playing:
            knife.render(screen, 0, 0)
        
        # 显示信息
        info_text = [
            "刀伤害位置测试",
            "",
            "控制:",
            "鼠标移动: 改变攻击方向",
            "空格: 执行攻击",
            "ESC: 退出",
            "",
            f"玩家位置: ({player.world_x:.1f}, {player.world_y:.1f})",
            f"敌人位置: ({enemy.rect.x:.1f}, {enemy.rect.y:.1f})",
            f"鼠标位置: ({mouse_x}, {mouse_y})",
            f"敌人血量: {enemy.health}",
            "",
            "现在伤害检测基于攻击位置（特效位置）"
        ]
        
        for i, text in enumerate(info_text):
            text_surface = font.render(text, True, (255, 255, 255))
            screen.blit(text_surface, (10, 10 + i * 25))
        
        pygame.display.flip()
    
    pygame.quit()
    print("测试结束")

if __name__ == "__main__":
    test_knife_damage_position() 
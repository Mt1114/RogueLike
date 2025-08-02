import pygame
import sys
import os

# 添加src目录到路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from modules.dual_player_system import DualPlayerSystem
from modules.game import Game

def test_mystic_attack():
    """测试神秘剑士的攻击功能"""
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("神秘剑士攻击测试")
    clock = pygame.time.Clock()
    
    # 创建游戏实例
    game = Game(screen)
    
    # 创建双角色系统
    dual_system = DualPlayerSystem(screen, game)
    
    print("神秘剑士武器列表:")
    for weapon in dual_system.mystic_swordsman.weapons:
        print(f"  - {weapon.type}: {type(weapon).__name__}")
    
    print(f"\n神秘剑士武器数量: {len(dual_system.mystic_swordsman.weapons)}")
    
    running = True
    while running:
        dt = clock.tick(60) / 1000.0
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key in [pygame.K_KP2, pygame.K_KP4, pygame.K_KP6, pygame.K_KP8]:
                    print(f"按下数字键盘键: {event.key}")
                    # 测试神秘剑士攻击
                    dual_system._handle_mystic_attack(event)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # 左键
                    print("鼠标左键攻击")
                    dual_system.mystic_swordsman.weapon_manager.manual_attack(screen)
                elif event.button == 3:  # 右键
                    print("鼠标右键攻击")
                    dual_system.mystic_swordsman.weapon_manager.melee_attack(screen)
            
            # 处理其他事件
            dual_system.handle_event(event)
        
        # 更新
        dual_system.update(dt)
        
        # 渲染
        screen.fill((50, 50, 50))
        
        # 渲染双角色系统
        dual_system.render(screen, 0, 0)
        dual_system.render_weapons(screen, 0, 0)
        
        # 显示提示信息
        font = pygame.font.Font(None, 24)
        text1 = font.render("使用数字键盘 2,4,6,8 测试神秘剑士攻击", True, (255, 255, 255))
        text2 = font.render("使用鼠标左键/右键测试攻击", True, (255, 255, 255))
        text3 = font.render("按ESC退出", True, (255, 255, 255))
        
        screen.blit(text1, (10, 10))
        screen.blit(text2, (10, 40))
        screen.blit(text3, (10, 70))
        
        pygame.display.flip()
    
    pygame.quit()

if __name__ == "__main__":
    test_mystic_attack() 
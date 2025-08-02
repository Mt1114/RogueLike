import pygame
import sys
import os

# 添加src目录到路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from modules.dual_player_system import DualPlayerSystem
from modules.game import Game

def test_mystic_simple():
    """简单测试神秘剑士的攻击功能"""
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("神秘剑士攻击测试")
    clock = pygame.time.Clock()
    
    # 创建游戏实例
    game = Game(screen)
    
    # 创建双角色系统
    dual_system = DualPlayerSystem(screen, game)
    
    print("=== 神秘剑士武器检查 ===")
    print(f"武器数量: {len(dual_system.mystic_swordsman.weapons)}")
    for i, weapon in enumerate(dual_system.mystic_swordsman.weapons):
        print(f"武器 {i+1}: {weapon.type} ({type(weapon).__name__})")
    
    print("\n=== 测试说明 ===")
    print("使用数字键盘 2,4,6,8 测试神秘剑士攻击")
    print("2=下, 4=左, 6=右, 8=上")
    print("按ESC退出")
    
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
                    print(f"检测到数字键盘按键: {event.key}")
                    dual_system._handle_mystic_attack(event)
            
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
        texts = [
            "神秘剑士攻击测试",
            "数字键盘: 2=下, 4=左, 6=右, 8=上",
            "按ESC退出"
        ]
        
        for i, text in enumerate(texts):
            text_surface = font.render(text, True, (255, 255, 255))
            screen.blit(text_surface, (10, 10 + i * 30))
        
        pygame.display.flip()
    
    pygame.quit()

if __name__ == "__main__":
    test_mystic_simple() 
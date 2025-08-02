import pygame
import sys
import os
import math

# 添加src目录到路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from modules.dual_player_system import DualPlayerSystem
from modules.game import Game

def test_independent_lighting():
    """测试独立方向的光照系统"""
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("独立光照方向测试")
    clock = pygame.time.Clock()
    
    # 创建游戏实例
    game = Game(screen)
    
    # 创建双角色系统
    dual_system = DualPlayerSystem(screen, game)
    
    print("=== 独立光照方向测试 ===")
    print("✅ 游戏和双角色系统已初始化")
    
    print("\n=== 控制说明 ===")
    print("神秘剑士移动: 方向键 (↑↓←→)")
    print("神秘剑士攻击: 数字键盘 (2,4,6,8)")
    print("忍者蛙移动: WASD")
    print("鼠标移动: 控制光源方向（应该独立于角色移动）")
    print("退出: ESC")
    
    print("\n=== 测试要点 ===")
    print("1. 光源方向由忍者蛙指向鼠标")
    print("2. 当忍者蛙移动时，光源方向会跟随忍者蛙位置")
    print("3. 当鼠标移动时，光源方向会跟随鼠标位置")
    print("4. 神秘剑士移动不会影响光源方向")
    
    running = True
    attack_count = 0
    
    while running:
        dt = clock.tick(60) / 1000.0
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key in [pygame.K_KP2, pygame.K_KP4, pygame.K_KP6, pygame.K_KP8]:
                    attack_count += 1
                    print(f"\n🎯 攻击 #{attack_count}")
            
            # 处理所有事件
            dual_system.handle_event(event)
        
        # 更新
        dual_system.update(dt)
        
        # 渲染
        screen.fill((50, 50, 50))
        
        # 渲染双角色系统
        dual_system.render(screen, 0, 0)
        dual_system.render_weapons(screen, 0, 0)
        
        # 显示状态信息
        font = pygame.font.Font(None, 20)
        mouse_x, mouse_y = pygame.mouse.get_pos()
        screen_center_x = screen.get_width() // 2
        screen_center_y = screen.get_height() // 2
        
        # 计算忍者蛙指向鼠标的方向
        ninja_screen_x = dual_system.ninja_frog.world_x - 0 + screen.get_width() // 2
        ninja_screen_y = dual_system.ninja_frog.world_y - 0 + screen.get_height() // 2
        dx = mouse_x - ninja_screen_x
        dy = mouse_y - ninja_screen_y
        direction = math.atan2(dy, dx)
        direction_degrees = math.degrees(direction)
        
        texts = [
            "独立光照方向测试",
            "",
            "神秘剑士移动: 方向键 (↑↓←→)",
            "神秘剑士攻击: 数字键盘 (2,4,6,8)",
            "忍者蛙移动: WASD",
            "鼠标移动: 控制光源方向",
            "",
            f"攻击次数: {attack_count}",
            f"神秘剑士位置: ({int(dual_system.mystic_swordsman.world_x)}, {int(dual_system.mystic_swordsman.world_y)})",
            f"忍者蛙位置: ({int(dual_system.ninja_frog.world_x)}, {int(dual_system.ninja_frog.world_y)})",
            f"鼠标位置: ({mouse_x}, {mouse_y})",
            f"光源方向: {direction_degrees:.1f}°",
            f"光源中心: 忍者蛙位置",
            f"光源指向: 忍者蛙 → 鼠标",
            "",
            "测试: 移动忍者蛙或鼠标，光源方向会相应改变",
            "按ESC退出"
        ]
        
        for i, text in enumerate(texts):
            if text:  # 跳过空行
                text_surface = font.render(text, True, (255, 255, 255))
                screen.blit(text_surface, (10, 10 + i * 20))
        
        pygame.display.flip()
    
    pygame.quit()
    print(f"\n=== 测试完成 ===")
    print(f"总攻击次数: {attack_count}")

if __name__ == "__main__":
    test_independent_lighting() 
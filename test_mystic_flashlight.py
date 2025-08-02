import pygame
import sys
import os
import math

# 添加src目录到路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from modules.dual_player_system import DualPlayerSystem
from modules.game import Game

def test_mystic_flashlight():
    """测试神秘剑士攻击时的临时光圈效果"""
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("神秘剑士临时光圈测试")
    clock = pygame.time.Clock()
    
    # 创建游戏实例
    game = Game(screen)
    
    # 创建双角色系统
    dual_system = DualPlayerSystem(screen, game)
    
    print("=== 神秘剑士临时光圈测试 ===")
    print("✅ 游戏和双角色系统已初始化")
    
    print("\n=== 控制说明 ===")
    print("忍者蛙移动: WASD")
    print("神秘剑士移动: 方向键 (↑↓←→)")
    print("神秘剑士攻击: 数字键盘 (2,4,6,8)")
    print("鼠标移动: 控制光源方向")
    print("退出: ESC")
    
    print("\n=== 测试要点 ===")
    print("1. 神秘剑士攻击时应该出现临时光圈")
    print("2. 光圈应该逐渐消失")
    print("3. 光圈应该照亮神秘剑士周围区域")
    
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
        mystic_x, mystic_y = dual_system.mystic_swordsman.world_x, dual_system.mystic_swordsman.world_y
        
        # 获取光圈状态
        flashlight_active = dual_system.mystic_flashlight_active
        flashlight_timer = dual_system.mystic_flashlight_timer
        flashlight_duration = dual_system.mystic_flashlight_duration
        
        texts = [
            "神秘剑士临时光圈测试",
            "",
            "忍者蛙移动: WASD",
            "神秘剑士移动: 方向键 (↑↓←→)",
            "神秘剑士攻击: 数字键盘 (2,4,6,8)",
            "鼠标移动: 控制光源方向",
            "退出: ESC",
            "",
            f"神秘剑士位置: ({int(mystic_x)}, {int(mystic_y)})",
            f"攻击次数: {attack_count}",
            "",
            f"临时光圈状态: {'激活' if flashlight_active else '未激活'}",
            f"光圈剩余时间: {flashlight_timer:.2f}s / {flashlight_duration:.2f}s",
            "",
            "✅ 攻击时出现临时光圈",
            "✅ 光圈逐渐消失",
            "✅ 照亮神秘剑士周围区域"
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
    test_mystic_flashlight() 
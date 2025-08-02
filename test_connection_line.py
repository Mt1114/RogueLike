import pygame
import sys
import os
import math

# 添加src目录到路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from modules.dual_player_system import DualPlayerSystem
from modules.game import Game

def test_connection_line():
    """测试两个角色之间的连接线功能"""
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("角色连接线测试")
    clock = pygame.time.Clock()
    
    # 创建游戏实例
    game = Game(screen)
    
    # 创建双角色系统
    dual_system = DualPlayerSystem(screen, game)
    
    print("=== 角色连接线测试 ===")
    print("✅ 游戏和双角色系统已初始化")
    
    print("\n=== 控制说明 ===")
    print("忍者蛙移动: WASD")
    print("神秘剑士移动: 方向键 (↑↓←→)")
    print("神秘剑士攻击: 数字键盘 (2,4,6,8)")
    print("鼠标移动: 控制光源方向")
    print("退出: ESC")
    
    print("\n=== 测试要点 ===")
    print("1. 两个角色之间应该有一条黄色虚线连接")
    print("2. 连接线应该跟随角色移动")
    print("3. 在黑暗中也能看到神秘剑士的位置")
    
    running = True
    
    while running:
        dt = clock.tick(60) / 1000.0
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
            
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
        ninja_x, ninja_y = dual_system.ninja_frog.world_x, dual_system.ninja_frog.world_y
        mystic_x, mystic_y = dual_system.mystic_swordsman.world_x, dual_system.mystic_swordsman.world_y
        
        # 计算两个角色之间的距离
        dx = mystic_x - ninja_x
        dy = mystic_y - ninja_y
        distance = math.sqrt(dx * dx + dy * dy)
        
        texts = [
            "角色连接线测试",
            "",
            "忍者蛙移动: WASD",
            "神秘剑士移动: 方向键 (↑↓←→)",
            "神秘剑士攻击: 数字键盘 (2,4,6,8)",
            "鼠标移动: 控制光源方向",
            "退出: ESC",
            "",
            f"忍者蛙位置: ({int(ninja_x)}, {int(ninja_y)})",
            f"神秘剑士位置: ({int(mystic_x)}, {int(mystic_y)})",
            f"角色间距离: {distance:.1f} 像素",
            "",
            "✅ 黄色虚线连接两个角色",
            "✅ 在黑暗中也能看到神秘剑士位置"
        ]
        
        for i, text in enumerate(texts):
            if text:  # 跳过空行
                text_surface = font.render(text, True, (255, 255, 255))
                screen.blit(text_surface, (10, 10 + i * 20))
        
        pygame.display.flip()
    
    pygame.quit()
    print(f"\n=== 测试完成 ===")

if __name__ == "__main__":
    test_connection_line() 
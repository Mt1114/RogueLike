import pygame
import sys
import os
import math

# 添加src目录到路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from modules.dual_player_system import DualPlayerSystem
from modules.game import Game

def test_vision_angle_fix():
    """测试视野角度修复，确保靠近屏幕边缘时扇形角度不会变大"""
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("视野角度修复测试")
    clock = pygame.time.Clock()
    
    # 创建游戏实例
    game = Game(screen)
    
    # 创建双角色系统
    dual_system = DualPlayerSystem(screen, game)
    
    print("=== 视野角度修复测试 ===")
    print("✅ 游戏和双角色系统已初始化")
    
    print("\n=== 控制说明 ===")
    print("忍者蛙移动: WASD")
    print("鼠标移动: 控制光源方向")
    print("退出: ESC")
    
    print("\n=== 测试要点 ===")
    print("1. 视野角度应该始终保持90度")
    print("2. 靠近屏幕边缘时，扇形角度不应该变大")
    print("3. 视野应该被屏幕边界正确裁剪")
    
    running = True
    test_positions = [
        (400, 300),  # 屏幕中心
        (100, 100),  # 左上角附近
        (700, 100),  # 右上角附近
        (100, 500),  # 左下角附近
        (700, 500),  # 右下角附近
    ]
    current_position = 0
    
    while running:
        dt = clock.tick(60) / 1000.0
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_SPACE:
                    # 空格键切换测试位置
                    current_position = (current_position + 1) % len(test_positions)
                    x, y = test_positions[current_position]
                    dual_system.ninja_frog.world_x = x
                    dual_system.ninja_frog.world_y = y
                    print(f"切换到测试位置: ({x}, {y})")
            
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
        ninja_x, ninja_y = dual_system.ninja_frog.world_x, dual_system.ninja_frog.world_y
        
        # 计算视野角度
        dx = mouse_x - ninja_x
        dy = mouse_y - ninja_y
        direction = math.atan2(dy, dx)
        direction_degrees = math.degrees(direction)
        
        # 计算视野边界角度
        vision_system = dual_system.lighting_manager.vision_system
        start_angle = direction - vision_system.half_angle
        end_angle = direction + vision_system.half_angle
        start_degrees = math.degrees(start_angle)
        end_degrees = math.degrees(end_angle)
        angle_span = math.degrees(vision_system.angle)
        
        texts = [
            "视野角度修复测试",
            "",
            "忍者蛙移动: WASD",
            "鼠标移动: 控制光源方向",
            "空格键: 切换测试位置",
            "退出: ESC",
            "",
            f"忍者蛙位置: ({int(ninja_x)}, {int(ninja_y)})",
            f"鼠标位置: ({mouse_x}, {mouse_y})",
            f"视野方向: {direction_degrees:.1f}°",
            f"视野角度范围: {start_degrees:.1f}° - {end_degrees:.1f}°",
            f"视野角度跨度: {angle_span:.1f}° (应该始终为90°)",
            "",
            "测试: 移动忍者蛙到屏幕边缘，视野角度应该保持90°",
            "按空格键切换测试位置"
        ]
        
        for i, text in enumerate(texts):
            if text:  # 跳过空行
                text_surface = font.render(text, True, (255, 255, 255))
                screen.blit(text_surface, (10, 10 + i * 20))
        
        pygame.display.flip()
    
    pygame.quit()
    print(f"\n=== 测试完成 ===")

if __name__ == "__main__":
    test_vision_angle_fix() 
import pygame
import sys
import math
from src.modules.vision_system import VisionSystem, DarkOverlay

def test_vision_system():
    """测试视野系统"""
    pygame.init()
    
    # 设置屏幕
    screen_width = 800
    screen_height = 600
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("视野系统测试 - 圆形+扇形")
    
    # 创建视野系统（消除黑暗区域）
    vision_system = VisionSystem(
        radius=200,
        angle=90,
        color=(255, 255, 255, 128),  # 扇形区域半透明
        circle_radius=80,
        circle_color=(255, 255, 255, 255)  # 圆形区域完全不透明
    )
    
    # 创建黑暗遮罩
    dark_overlay = DarkOverlay(screen_width, screen_height, darkness_alpha=150)
    
    # 玩家位置（屏幕中心）
    player_x = screen_width // 2
    player_y = screen_height // 2
    
    clock = pygame.time.Clock()
    running = True
    
    print("视野系统测试 - 消除黑暗区域")
    print("F3: 切换视野系统")
    print("F4/F5: 调整扇形视野半径")
    print("F6/F7: 调整扇形视野角度")
    print("F8/F9: 调整圆形光圈半径")
    print("鼠标移动: 改变视野方向")
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F3:
                    # 这里可以添加切换逻辑
                    print("F3 按下")
                elif event.key == pygame.K_F4:
                    vision_system.set_radius(vision_system.radius + 50)
                    print(f"扇形视野半径: {vision_system.radius}")
                elif event.key == pygame.K_F5:
                    vision_system.set_radius(max(50, vision_system.radius - 50))
                    print(f"扇形视野半径: {vision_system.radius}")
                elif event.key == pygame.K_F6:
                    vision_system.set_angle(min(360, math.degrees(vision_system.angle) + 15))
                    print(f"扇形视野角度: {math.degrees(vision_system.angle):.1f}°")
                elif event.key == pygame.K_F7:
                    vision_system.set_angle(max(30, math.degrees(vision_system.angle) - 15))
                    print(f"扇形视野角度: {math.degrees(vision_system.angle):.1f}°")
                elif event.key == pygame.K_F8:
                    vision_system.set_circle_radius(vision_system.circle_radius + 20)
                    print(f"圆形光圈半径: {vision_system.circle_radius}")
                elif event.key == pygame.K_F9:
                    vision_system.set_circle_radius(max(20, vision_system.circle_radius - 20))
                    print(f"圆形光圈半径: {vision_system.circle_radius}")
        
        # 获取鼠标位置
        mouse_x, mouse_y = pygame.mouse.get_pos()
        
        # 更新视野系统
        vision_system.update(player_x, player_y, mouse_x, mouse_y)
        
        # 清屏
        screen.fill((50, 50, 50))
        
        # 绘制一些测试对象
        pygame.draw.circle(screen, (255, 0, 0), (player_x, player_y), 10)  # 玩家（红色）
        pygame.draw.circle(screen, (0, 255, 0), (mouse_x, mouse_y), 5)     # 鼠标（绿色）
        
        # 绘制一些测试点
        test_points = [
            (100, 100), (700, 100), (100, 500), (700, 500),
            (400, 100), (400, 500), (100, 300), (700, 300),
            (350, 300), (450, 300), (400, 250), (400, 350)  # 更靠近玩家的点
        ]
        
        for point in test_points:
            color = (0, 255, 255) if vision_system.is_in_vision(*point) else (100, 100, 100)
            pygame.draw.circle(screen, color, point, 8)
        
        # 渲染视野系统
        vision_system.render(screen, dark_overlay.get_overlay())
        
        # 显示信息
        font = pygame.font.Font(None, 24)
        info_text = [
            f"扇形视野半径: {vision_system.radius}",
            f"扇形视野角度: {math.degrees(vision_system.angle):.1f}°",
            f"圆形区域半径: {vision_system.circle_radius}",
            f"鼠标位置: ({mouse_x}, {mouse_y})",
            "青色点: 在视野内（圆形或扇形）",
            "灰色点: 在视野外",
            "圆形区域: 完全消除黑暗",
            "扇形区域: 部分消除黑暗"
        ]
        
        for i, text in enumerate(info_text):
            text_surface = font.render(text, True, (255, 255, 255))
            screen.blit(text_surface, (10, 10 + i * 25))
        
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    test_vision_system() 
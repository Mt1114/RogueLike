#!/usr/bin/env python3
"""
圆形光圈光线追踪测试
专门演示圆形光圈被墙壁遮挡的效果
"""

import pygame
import sys
import math
import numpy as np
from src.modules.vision_system import VisionSystem, DarkOverlay

def get_chinese_font(size=24):
    """获取支持中文的字体"""
    chinese_fonts = [
        'microsoftyaheimicrosoftyaheiui',
        'microsoft yahei',
        'simsun',
        'simhei',
        'kaiti',
        'fangsong'
    ]
    
    for font_name in chinese_fonts:
        try:
            font = pygame.font.SysFont(font_name, size)
            # 测试字体是否能渲染中文字符
            test_surface = font.render('测试', True, (255, 255, 255))
            return font
        except:
            continue
    
    # 如果所有中文字体都失败，返回默认字体
    return pygame.font.Font(None, size)

def test_circle_raycast():
    """测试圆形光圈光线追踪"""
    pygame.init()
    
    # 设置屏幕
    screen_width = 800
    screen_height = 600
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("圆形光圈光线追踪测试")
    
    # 创建视野系统（使用圆形光圈和扇形视野）
    vision_system = VisionSystem(radius=150, angle=90, circle_radius=100)
    dark_overlay = DarkOverlay(screen_width, screen_height, darkness_alpha=200)
    
    # 创建一些测试墙壁
    walls = [
        pygame.Rect(100, 100, 200, 20),   # 水平墙
        # pygame.Rect(400, 200, 20, 150),   # 垂直墙
        pygame.Rect(200, 300, 150, 20),   # 另一水平墙
        pygame.Rect(50, 400, 20, 100),    # 另一垂直墙
        pygame.Rect(500, 100, 20, 100),   # 右上角墙
        pygame.Rect(600, 300, 100, 20),   # 右下角墙
    ]
    
    # 设置墙壁数据
    vision_system.set_walls(walls, 32, screen_width, screen_height)
    
    # 玩家位置
    player_x = screen_width // 2
    player_y = screen_height // 2
    
    clock = pygame.time.Clock()
    running = True
    
    print("=== 圆形光圈光线追踪测试 ===")
    print("鼠标移动: 改变视野方向")
    print("F1: 切换光线追踪")
    print("F2: 显示/隐藏墙壁")
    print("F3: 调整圆形光圈半径")
    print("F4: 移动玩家位置")
    print("F5: 显示圆形光线追踪线")
    print("================================")
    
    show_walls = True
    use_raycast = True
    show_rays = False
    player_pos = (player_x, player_y)
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F1:
                    use_raycast = not use_raycast
                    print(f"光线追踪: {'启用' if use_raycast else '禁用'}")
                elif event.key == pygame.K_F2:
                    show_walls = not show_walls
                    print(f"显示墙壁: {'是' if show_walls else '否'}")
                elif event.key == pygame.K_F3:
                    current_radius = vision_system.circle_radius
                    new_radius = current_radius + 20 if current_radius < 200 else 50
                    vision_system.set_circle_radius(new_radius)
                    print(f"圆形光圈半径: {new_radius}")
                elif event.key == pygame.K_F4:
                    # 随机移动玩家位置
                    import random
                    player_pos = (random.randint(100, 700), random.randint(100, 500))
                    print(f"玩家位置: {player_pos}")
                elif event.key == pygame.K_F5:
                    show_rays = not show_rays
                    print(f"显示光线追踪线: {'是' if show_rays else '否'}")
        
        # 获取鼠标位置
        mouse_x, mouse_y = pygame.mouse.get_pos()
        
        # 更新视野系统
        vision_system.update(player_pos[0], player_pos[1], mouse_x, mouse_y)
        
        # 清屏
        screen.fill((50, 50, 50))
        
        # 绘制墙壁
        if show_walls:
            for wall in walls:
                pygame.draw.rect(screen, (100, 100, 100), wall)
                pygame.draw.rect(screen, (200, 200, 200), wall, 2)
        
        # 绘制玩家
        pygame.draw.circle(screen, (255, 0, 0), player_pos, 10)
        
        # 绘制鼠标位置
        pygame.draw.circle(screen, (0, 255, 0), (mouse_x, mouse_y), 5)
        
        # 绘制从玩家到鼠标的线
        pygame.draw.line(screen, (255, 255, 0), player_pos, (mouse_x, mouse_y), 2)
        
        # 绘制圆形光圈的边界（用于参考）
        pygame.draw.circle(screen, (255, 255, 255), player_pos, vision_system.circle_radius, 1)
        
        # 绘制圆形光圈的光线追踪线
        if show_rays:
            num_rays = max(64, int(vision_system.circle_radius / 2))
            angles = np.linspace(0, 2 * math.pi, num_rays)
            
            for angle in angles:
                end_x = player_pos[0] + vision_system.circle_radius * math.cos(angle)
                end_y = player_pos[1] + vision_system.circle_radius * math.sin(angle)
                
                # 进行光线追踪
                blocked, hit_point = vision_system.ray_cast(player_pos[0], player_pos[1], end_x, end_y)
                
                if blocked:
                    # 如果被阻挡，绘制到阻挡点的线
                    pygame.draw.line(screen, (255, 0, 0), player_pos, hit_point, 1)
                    # 绘制阻挡点
                    pygame.draw.circle(screen, (255, 0, 0), hit_point, 3)
                else:
                    # 如果没有被阻挡，绘制到终点的线
                    pygame.draw.line(screen, (0, 255, 0), player_pos, (end_x, end_y), 1)
        
        # 渲染视野系统
        vision_system.render(screen, dark_overlay.get_overlay())
        
        # 创建支持中文的字体
        font = get_chinese_font(24)
        
        # 调试信息：显示视野系统状态
        debug_info = [
            f"视野半径: {vision_system.radius}",
            f"视野角度: {math.degrees(vision_system.angle):.1f}°",
            f"圆形光圈半径: {vision_system.circle_radius}",
            f"视野方向: {math.degrees(vision_system.direction):.1f}°",
            f"墙壁数量: {len(walls)}",
            f"圆形光线数量: {max(64, int(vision_system.circle_radius / 2))}",
            f"阻挡点数量: {len([p for p in vision_system.walls if p])}"
        ]
        
        for i, text in enumerate(debug_info):
            text_surface = font.render(text, True, (255, 255, 0))
            screen.blit(text_surface, (10, 200 + i * 25))
        
        # 显示信息
        info_text = [
            f"光线追踪: {'启用' if use_raycast else '禁用'}",
            f"显示墙壁: {'是' if show_walls else '否'}",
            f"显示光线: {'是' if show_rays else '否'}",
            f"圆形光圈半径: {vision_system.circle_radius}",
            f"玩家位置: {player_pos}",
            f"鼠标位置: ({mouse_x}, {mouse_y})",
            "",
            "F1: 切换光线追踪  F2: 显示/隐藏墙壁",
            "F3: 调整圆形光圈半径  F4: 移动玩家位置",
            "F5: 显示圆形光线追踪线"
        ]
        
        for i, text in enumerate(info_text):
            text_surface = font.render(text, True, (255, 255, 255))
            screen.blit(text_surface, (10, 10 + i * 25))
        
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    test_circle_raycast() 
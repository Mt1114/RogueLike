#!/usr/bin/env python3
"""
测试图层检测功能
"""

import pygame
import sys
import os

# 添加src目录到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from modules.map_manager import MapManager
from modules.resource_manager import resource_manager

# 初始化Pygame
pygame.init()

# 设置屏幕
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("图层检测测试")

# 创建地图管理器
map_manager = MapManager(screen, scale=2.0)

# 加载Dungeon1地图
try:
    success = map_manager.load_map("Dungeon1")
    if success:
        print("地图加载成功")
        print(f"图层数量: {map_manager.get_layer_count()}")
        print(f"图层名称: {map_manager.get_layer_names()}")
    else:
        print("地图加载失败")
        sys.exit(1)
except Exception as e:
    print(f"地图加载失败: {e}")
    sys.exit(1)

# 相机位置
camera_x = 0
camera_y = 0

# 游戏循环
running = True
clock = pygame.time.Clock()

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            # 鼠标点击时检测图层
            mouse_x, mouse_y = pygame.mouse.get_pos()
            # 将屏幕坐标转换为世界坐标
            world_x = mouse_x - SCREEN_WIDTH // 2 + camera_x
            world_y = mouse_y - SCREEN_HEIGHT // 2 + camera_y
            
            print(f"\n=== 鼠标点击位置检测 ===")
            print(f"屏幕坐标: ({mouse_x}, {mouse_y})")
            print(f"世界坐标: ({world_x}, {world_y})")
            map_manager.print_layer_info_at_position(world_x, world_y)
    
    # 处理键盘输入移动相机
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        camera_x -= 5
    if keys[pygame.K_RIGHT]:
        camera_x += 5
    if keys[pygame.K_UP]:
        camera_y -= 5
    if keys[pygame.K_DOWN]:
        camera_y += 5
    
    # 清空屏幕
    screen.fill((0, 0, 0))
    
    # 渲染地图的"玩家之前"图层
    map_manager.render_layers_before_player(camera_x, camera_y)
    
    # 渲染玩家（用红色矩形表示）
    player_rect = pygame.Rect(SCREEN_WIDTH // 2 - 10, SCREEN_HEIGHT // 2 - 10, 20, 20)
    pygame.draw.rect(screen, (255, 0, 0), player_rect)
    
    # 渲染地图的"玩家之后"图层
    map_manager.render_layers_after_player(camera_x, camera_y)
    
    # 显示信息
    font = pygame.font.Font(None, 24)
    info_text = f"相机位置: ({camera_x}, {camera_y})"
    text_surface = font.render(info_text, True, (255, 255, 255))
    screen.blit(text_surface, (10, 10))
    
    help_text = "使用方向键移动相机，鼠标点击检测图层，ESC退出"
    help_surface = font.render(help_text, True, (255, 255, 255))
    screen.blit(help_surface, (10, 40))
    
    # 显示玩家位置的世界坐标
    player_world_x = SCREEN_WIDTH // 2 - SCREEN_WIDTH // 2 + camera_x
    player_world_y = SCREEN_HEIGHT // 2 - SCREEN_HEIGHT // 2 + camera_y
    player_pos_text = f"玩家世界坐标: ({player_world_x}, {player_world_y})"
    player_pos_surface = font.render(player_pos_text, True, (255, 255, 0))
    screen.blit(player_pos_surface, (10, 70))
    
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit() 
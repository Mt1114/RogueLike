import pygame
import sys
import os

# 添加src目录到路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from modules.items.teleport_item import TeleportItem
from modules.items.teleport_manager import TeleportManager
from modules.minimap import Minimap

# 初始化Pygame
pygame.init()

# 创建屏幕
screen_width = 1200
screen_height = 800
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("传送道具小地图测试")

# 创建地图管理器（模拟）
class MockMapManager:
    def __init__(self):
        self.map_width = 2000
        self.map_height = 1500
        
    def get_collision_tiles(self):
        return []  # 返回空列表，表示没有碰撞

# 创建小地图
map_manager = MockMapManager()
minimap = Minimap(map_manager.map_width, map_manager.map_height, screen_width, screen_height)

# 创建传送道具管理器
teleport_manager = TeleportManager(map_manager)

# 生成一些传送道具
for i in range(3):
    teleport_manager.spawn_teleport_item()

# 模拟玩家
class MockPlayer:
    def __init__(self):
        self.world_x = 1000
        self.world_y = 750

player = MockPlayer()

# 游戏主循环
clock = pygame.time.Clock()
running = True

while running:
    dt = clock.tick(60) / 1000.0
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
    
    # 更新传送道具
    teleport_manager.update(dt, player)
    
    # 清屏
    screen.fill((50, 50, 50))
    
    # 渲染传送道具（通过管理器）
    teleport_manager.render(screen, 0, 0)
    
    # 渲染小地图
    teleport_items = teleport_manager.get_items()
    minimap.render(screen, player, [], None, None, None, teleport_items)
    
    # 显示信息
    font = pygame.font.Font(None, 36)
    info_text = f"传送道具数量: {len(teleport_items)}"
    text_surface = font.render(info_text, True, (255, 255, 255))
    screen.blit(text_surface, (10, 10))
    
    # 显示传送道具位置
    y_offset = 50
    for i, item in enumerate(teleport_items):
        pos_text = f"道具 {i+1}: ({item.world_x:.0f}, {item.world_y:.0f})"
        text_surface = font.render(pos_text, True, (255, 255, 255))
        screen.blit(text_surface, (10, y_offset))
        y_offset += 30
    
    pygame.display.flip()

pygame.quit()
sys.exit() 
import pygame
import sys
import os

# 添加项目路径
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))

from modules.lighting_manager import LightingManager

def test_lighting_system():
    """测试新的光照系统"""
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("光照系统测试")
    
    # 创建光照管理器
    lighting_manager = LightingManager(800, 600)
    
    # 创建一些测试墙壁
    test_walls = [
        pygame.Rect(100, 100, 50, 50),
        pygame.Rect(200, 150, 50, 50),
        pygame.Rect(300, 200, 50, 50),
    ]
    
    # 设置墙壁
    lighting_manager.set_walls(test_walls, 32)
    
    clock = pygame.time.Clock()
    running = True
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
        
        # 获取鼠标位置
        mouse_x, mouse_y = pygame.mouse.get_pos()
        
        # 清屏
        screen.fill((0, 0, 0))
        
        # 绘制测试墙壁
        for wall in test_walls:
            pygame.draw.rect(screen, (100, 100, 100), wall)
        
        # 渲染光照系统
        lighting_manager.render(screen, 400, 300, mouse_x, mouse_y, 0, 0)
        
        # 绘制玩家位置（屏幕中心）
        pygame.draw.circle(screen, (0, 255, 0), (400, 300), 5)
        
        # 绘制鼠标位置
        pygame.draw.circle(screen, (255, 0, 0), (mouse_x, mouse_y), 3)
        
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()

if __name__ == "__main__":
    test_lighting_system() 
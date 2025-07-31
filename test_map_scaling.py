import pygame
import sys
import os

# 添加项目路径
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))

# 设置资源目录
os.environ['RESOURCE_DIR'] = os.path.abspath(os.path.join(os.path.dirname(__file__), 'assets'))

from modules.map_manager import MapManager

def test_map_scaling():
    """测试地图4倍缩放功能"""
    pygame.init()
    screen = pygame.display.set_mode((1200, 800))
    pygame.display.set_caption("地图4倍缩放测试")
    
    # 创建地图管理器（4倍缩放）
    map_manager = MapManager(screen, scale_factor=4.0)
    
    # 加载测试地图
    success = map_manager.load_map("simple_map")
    if not success:
        print("无法加载地图，尝试其他地图...")
        success = map_manager.load_map("test1_map")
    
    if not success:
        print("无法加载任何地图，退出测试")
        return
    
    # 获取地图信息
    map_width, map_height = map_manager.get_map_size()
    tile_width, tile_height = map_manager.get_tile_size()
    
    print(f"地图尺寸: {map_width} x {map_height}")
    print(f"瓦片尺寸: {tile_width} x {tile_height}")
    print(f"缩放因子: {map_manager.scale_factor}")
    
    # 相机位置（地图中心）
    camera_x = map_width // 2
    camera_y = map_height // 2
    
    # 字体
    font = pygame.font.Font(None, 24)
    
    clock = pygame.time.Clock()
    running = True
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_w:
                    camera_y -= tile_height  # 向上移动一个瓦片
                elif event.key == pygame.K_s:
                    camera_y += tile_height  # 向下移动一个瓦片
                elif event.key == pygame.K_a:
                    camera_x -= tile_width   # 向左移动一个瓦片
                elif event.key == pygame.K_d:
                    camera_x += tile_width   # 向右移动一个瓦片
        
        # 限制相机在地图边界内
        camera_x = max(0, min(camera_x, map_width))
        camera_y = max(0, min(camera_y, map_height))
        
        # 清屏
        screen.fill((50, 50, 50))
        
        # 渲染地图
        map_manager.render(camera_x, camera_y)
        
        # 绘制相机位置指示器
        screen_center_x = screen.get_width() // 2
        screen_center_y = screen.get_height() // 2
        pygame.draw.circle(screen, (255, 0, 0), (screen_center_x, screen_center_y), 10)
        
        # 显示信息
        info_text = [
            f"地图尺寸: {map_width} x {map_height}",
            f"瓦片尺寸: {tile_width} x {tile_height}",
            f"缩放因子: {map_manager.scale_factor}",
            f"相机位置: ({camera_x}, {camera_y})",
            "",
            "控制说明:",
            "WASD: 移动相机",
            "ESC: 退出"
        ]
        
        for i, text in enumerate(info_text):
            text_surface = font.render(text, True, (255, 255, 255))
            screen.blit(text_surface, (10, 10 + i * 25))
        
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()

if __name__ == "__main__":
    test_map_scaling() 
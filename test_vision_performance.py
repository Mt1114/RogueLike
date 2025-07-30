import pygame
import time
import sys
import os

# 添加src目录到路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from modules.vision_system import VisionSystem, DarkOverlay
from modules.vision_config import get_vision_config, validate_config

def test_vision_performance():
    """测试视野系统性能"""
    pygame.init()
    
    # 设置屏幕
    screen_width = 1280
    screen_height = 720
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("视野系统性能测试")
    
    # 获取配置
    config = get_vision_config()
    config = validate_config(config)
    
    # 创建视野系统
    vision_system = VisionSystem(
        radius=config["sector"]["radius"],
        angle=config["sector"]["angle"],
        color=config["sector"]["color"],
        circle_radius=config["circle"]["radius"],
        circle_color=config["circle"]["color"]
    )
    
    # 创建黑暗遮罩
    dark_overlay = DarkOverlay(screen_width, screen_height, config["darkness"]["alpha"])
    
    # 模拟墙壁数据
    walls = [
        pygame.Rect(100, 100, 200, 50),
        pygame.Rect(400, 300, 150, 100),
        pygame.Rect(600, 200, 100, 300),
        pygame.Rect(800, 400, 200, 80),
    ]
    
    vision_system.set_walls(walls, 32, 2000, 2000)
    vision_system.set_camera_and_screen(0, 0, screen_width//2, screen_height//2)
    
    # 性能测试参数
    test_duration = 5.0  # 测试5秒
    frame_count = 0
    total_render_time = 0
    total_raycast_time = 0
    
    clock = pygame.time.Clock()
    start_time = time.time()
    
    print("开始性能测试...")
    print("按ESC键退出")
    
    running = True
    while running:
        current_time = time.time()
        dt = clock.tick(60) / 1000.0
        
        # 处理事件
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
        
        # 更新视野系统
        mouse_x, mouse_y = pygame.mouse.get_pos()
        vision_system.update(screen_width//2, screen_height//2, mouse_x, mouse_y)
        
        # 渲染
        screen.fill((50, 50, 50))
        
        # 绘制墙壁
        for wall in walls:
            pygame.draw.rect(screen, (100, 100, 100), wall)
        
        # 渲染视野系统
        render_start = time.time()
        vision_system.render(screen, dark_overlay.get_overlay())
        render_time = time.time() - render_start
        
        # 统计性能
        frame_count += 1
        total_render_time += render_time
        
        # 显示性能信息
        stats = vision_system.get_performance_stats()
        fps = 1.0 / dt if dt > 0 else 0
        
        info_text = [
            f"FPS: {fps:.1f}",
            f"渲染时间: {render_time*1000:.1f}ms",
            f"光线追踪调用: {stats['raycast_calls']}",
            f"缓存命中率: {stats['cache_hits']/(stats['cache_hits']+stats['cache_misses'])*100:.1f}%" if (stats['cache_hits']+stats['cache_misses']) > 0 else "缓存命中率: 0%",
            f"平均光线追踪时间: {stats['raycast_time']/max(1, stats['raycast_calls'])*1000:.2f}ms" if stats['raycast_calls'] > 0 else "平均光线追踪时间: 0ms"
        ]
        
        font = pygame.font.Font(None, 24)
        for i, text in enumerate(info_text):
            text_surface = font.render(text, True, (255, 255, 255))
            screen.blit(text_surface, (10, 10 + i * 25))
        
        pygame.display.flip()
        
        # 检查测试时间
        if current_time - start_time >= test_duration:
            print(f"\n性能测试结果:")
            print(f"总帧数: {frame_count}")
            print(f"平均FPS: {frame_count / test_duration:.1f}")
            print(f"平均渲染时间: {total_render_time / frame_count * 1000:.2f}ms")
            print(f"总光线追踪调用: {stats['raycast_calls']}")
            print(f"缓存命中率: {stats['cache_hits']/(stats['cache_hits']+stats['cache_misses'])*100:.1f}%" if (stats['cache_hits']+stats['cache_misses']) > 0 else "缓存命中率: 0%")
            break
    
    pygame.quit()

if __name__ == "__main__":
    test_vision_performance() 
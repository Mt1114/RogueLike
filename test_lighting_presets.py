import pygame
import sys
import os

# 添加项目路径
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))

from modules.lighting_manager import LightingManager

def test_lighting_presets():
    """测试光照预设功能"""
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("光照预设测试")
    
    # 创建光照管理器
    lighting_manager = LightingManager(800, 600, "default")
    
    # 创建一些测试墙壁
    test_walls = [
        pygame.Rect(100, 100, 50, 50),
        pygame.Rect(200, 150, 50, 50),
        pygame.Rect(300, 200, 50, 50),
        pygame.Rect(400, 250, 50, 50),
        pygame.Rect(500, 300, 50, 50),
    ]
    
    # 设置墙壁
    lighting_manager.set_walls(test_walls, 32)
    
    # 获取可用预设
    available_presets = lighting_manager.get_available_presets()
    print(f"可用预设: {available_presets}")
    
    clock = pygame.time.Clock()
    running = True
    
    # 字体
    font = pygame.font.Font(None, 24)
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_F4:
                    # 循环切换预设
                    lighting_manager.cycle_preset()
                    current_preset = lighting_manager.get_current_preset()
                    preset_info = lighting_manager.get_preset_info(current_preset)
                    print(f"切换到预设: {preset_info['name']}")
                elif event.key == pygame.K_1:
                    # 切换到默认预设
                    lighting_manager.set_preset("default")
                elif event.key == pygame.K_2:
                    # 切换到宽视野预设
                    lighting_manager.set_preset("wide")
                elif event.key == pygame.K_3:
                    # 切换到窄视野预设
                    lighting_manager.set_preset("narrow")
                elif event.key == pygame.K_4:
                    # 切换到夜视模式预设
                    lighting_manager.set_preset("night_vision")
                elif event.key == pygame.K_5:
                    # 切换到隧道视野预设
                    lighting_manager.set_preset("tunnel")
        
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
        
        # 显示当前预设信息
        current_preset = lighting_manager.get_current_preset()
        preset_info = lighting_manager.get_preset_info(current_preset)
        
        if preset_info:
            # 显示预设名称
            preset_text = font.render(f"当前预设: {preset_info['name']}", True, (255, 255, 255))
            screen.blit(preset_text, (10, 10))
            
            # 显示预设参数
            params_text = font.render(
                f"视野半径: {preset_info['sector_radius']}, "
                f"视野角度: {preset_info['sector_angle']}°, "
                f"光圈半径: {preset_info['circle_radius']}, "
                f"黑暗程度: {preset_info['darkness_alpha']}", 
                True, (200, 200, 200)
            )
            screen.blit(params_text, (10, 35))
        
        # 显示控制说明
        controls_text = font.render(
            "F4: 循环切换预设 | 1-5: 直接切换预设 | ESC: 退出", 
            True, (150, 150, 150)
        )
        screen.blit(controls_text, (10, 570))
        
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()

if __name__ == "__main__":
    test_lighting_presets() 
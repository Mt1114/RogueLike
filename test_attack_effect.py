import pygame
import sys
import os

# 添加项目路径
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))

from modules.player import Player
from modules.weapons.attack_effect import AttackEffect

def test_attack_effect():
    """测试攻击特效系统"""
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("攻击特效测试")
    
    # 创建玩家
    player = Player(400, 300, "ninja_frog")
    
    # 创建攻击特效
    try:
        effect = AttackEffect(
            'images/attcak/hit_animations/swing02.png',
            frame_width=64,
            frame_height=64,
            frame_count=10
        )
        print(f"特效创建成功，帧数: {len(effect.frames)}")
        for i, frame in enumerate(effect.frames):
            print(f"  帧 {i}: {frame.get_size()}")
    except Exception as e:
        print(f"特效创建失败: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # 字体
    font = pygame.font.Font(None, 24)
    
    clock = pygame.time.Clock()
    running = True
    
    # 特效状态
    effect_playing = False
    mouse_x, mouse_y = 400, 300
    
    print("攻击特效测试")
    print("控制:")
    print("  鼠标移动: 改变特效方向")
    print("  空格: 播放特效")
    print("  ESC: 退出")
    
    while running:
        dt = clock.tick(60) / 1000.0
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_SPACE:
                    # 播放特效
                    if not effect_playing:
                        # 计算方向（从玩家到鼠标）
                        dx = mouse_x - 400
                        dy = mouse_y - 300
                        distance = (dx**2 + dy**2)**0.5
                        if distance > 0:
                            direction_x = dx / distance
                            direction_y = dy / distance
                        else:
                            direction_x = 1
                            direction_y = 0
                        
                        effect.play(400, 300, direction_x, direction_y)
                        effect_playing = True
                        print(f"播放特效，方向: ({direction_x:.2f}, {direction_y:.2f})")
            elif event.type == pygame.MOUSEMOTION:
                mouse_x, mouse_y = event.pos
        
        # 更新特效
        if effect_playing:
            effect.update(dt)
            if effect.is_finished():
                effect_playing = False
                print("特效播放完毕")
        
        # 清屏
        screen.fill((30, 30, 30))
        
        # 渲染玩家（简化）
        player_rect = pygame.Rect(380, 280, 40, 40)
        pygame.draw.rect(screen, (0, 255, 0), player_rect)
        
        # 渲染特效
        if effect_playing:
            effect.render(screen, 0, 0)
        
        # 显示信息
        info_text = [
            "攻击特效测试",
            "",
            "控制:",
            "鼠标移动: 改变特效方向",
            "空格: 播放特效",
            "ESC: 退出",
            "",
            f"特效状态: {'播放中' if effect_playing else '停止'}",
            f"鼠标位置: ({mouse_x}, {mouse_y})",
            f"特效帧数: {len(effect.frames) if effect.frames else 0}",
            f"当前帧: {effect.current_frame if effect_playing else 'N/A'}"
        ]
        
        for i, text in enumerate(info_text):
            text_surface = font.render(text, True, (255, 255, 255))
            screen.blit(text_surface, (10, 10 + i * 25))
        
        pygame.display.flip()
    
    pygame.quit()
    print("测试结束")

if __name__ == "__main__":
    test_attack_effect() 
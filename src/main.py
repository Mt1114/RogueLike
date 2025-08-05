import pygame
import sys
from modules.game import Game
from modules.intro_animation import IntroAnimation

def main():
    pygame.init()
    
    # 尝试初始化音频系统，如果失败则继续运行游戏（只是没有声音）
    try:
        pygame.mixer.init()
        print("音频系统初始化成功")
    except pygame.error as e:
        print(f"音频系统初始化失败: {e}")
        print("游戏将继续运行，但没有声音")
    
    screen_width = 1920
    screen_height = 1280
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("像素生存")
    
    clock = pygame.time.Clock()
    
    # 创建开场动画
    intro_animation = IntroAnimation(screen)
    
    # 开场动画循环
    print("播放开场动画...")
    while intro_animation.is_playing:
        dt = clock.tick(60) / 1000.0  # 60 FPS for smooth animation
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            # 允许跳过动画
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE or event.key == pygame.K_ESCAPE:
                    intro_animation.is_playing = False
        
        intro_animation.update(dt)
        intro_animation.render()
        pygame.display.flip()
    
    print("开场动画完成，进入游戏...")
    
    # 创建游戏实例
    game = Game(screen)
    
    # 主游戏循环
    while game.running:
        dt = clock.tick(30) / 1000.0  # 转换为秒
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            game.handle_event(event)
        
        game.update(dt)
        game.render()
        pygame.display.flip()
    
    # 如果游戏结束，退出
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main() 
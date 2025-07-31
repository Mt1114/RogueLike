import pygame
import sys
import os
import math

# 添加项目路径
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))

from modules.player import Player

def test_gun_flip():
    """测试枪械翻转功能"""
    pygame.init()
    screen = pygame.display.set_mode((1200, 800))
    pygame.display.set_caption("枪械翻转测试")
    
    # 创建玩家（会自动获得手枪和刀）
    player = Player(600, 400, "ninja_frog")
    
    # 字体
    font = pygame.font.Font(None, 24)
    
    clock = pygame.time.Clock()
    running = True
    
    # 记录鼠标位置变化
    last_mouse_x = 600
    flip_detected = False
    flip_timer = 0
    
    while running:
        dt = clock.tick(60) / 1000.0
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # 左键远程攻击
                    # 处理玩家事件（包括射击）
                    player.handle_event(event)
                    print("左键远程攻击（手枪）！")
        
        # 更新玩家和武器
        player.update(dt)
        player.update_weapons(dt)
        
        # 检测翻转
        mouse_x, mouse_y = pygame.mouse.get_pos()
        player_center_x = screen.get_width() // 2
        
        # 检测是否从左到右或从右到左切换
        if (last_mouse_x < player_center_x and mouse_x >= player_center_x) or \
           (last_mouse_x >= player_center_x and mouse_x < player_center_x):
            flip_detected = True
            flip_timer = 0.5  # 显示翻转提示0.5秒
        
        last_mouse_x = mouse_x
        
        # 更新翻转计时器
        if flip_timer > 0:
            flip_timer -= dt
        
        # 清屏
        screen.fill((30, 30, 30))
        
        # 渲染玩家
        player.render(screen)
        
        # 渲染武器和投射物
        player.render_weapons(screen, 0, 0)
        
        # 显示信息
        info_text = [
            "枪械翻转测试",
            "",
            "功能特性:",
            "- 鼠标在左侧时，枪械上下翻转",
            "- 鼠标在右侧时，枪械正常显示",
            "- 左右切换时会有翻转动画",
            "",
            "测试方法:",
            "1. 将鼠标移动到玩家左侧",
            "2. 观察枪械是否上下翻转",
            "3. 将鼠标移动到玩家右侧",
            "4. 观察枪械是否恢复正常",
            "5. 快速左右移动鼠标观察翻转",
            "",
            "控制:",
            "鼠标左键: 射击",
            "ESC: 退出"
        ]
        
        for i, text in enumerate(info_text):
            text_surface = font.render(text, True, (255, 255, 255))
            screen.blit(text_surface, (10, 10 + i * 25))
        
        # 显示当前状态
        current_side = "左侧" if mouse_x < player_center_x else "右侧"
        status_text = f"鼠标位置: {current_side} (X: {mouse_x})"
        status_surface = font.render(status_text, True, (0, 255, 0))
        screen.blit(status_surface, (10, 400))
        
        # 显示翻转提示
        if flip_detected and flip_timer > 0:
            flip_text = "检测到左右切换！"
            flip_surface = font.render(flip_text, True, (255, 255, 0))
            screen.blit(flip_surface, (10, 430))
        
        # 显示武器信息
        weapon_info = []
        for i, weapon in enumerate(player.weapons):
            weapon_info.append(f"武器{i+1}: {weapon.type} (等级{weapon.level})")
        
        for i, text in enumerate(weapon_info):
            text_surface = font.render(text, True, (0, 255, 255))
            screen.blit(text_surface, (10, 460 + i * 25))
        
        # 显示投射物数量
        total_projectiles = 0
        for weapon in player.weapons:
            if hasattr(weapon, 'projectiles'):
                total_projectiles += len(weapon.projectiles)
        count_text = font.render(f"活跃投射物: {total_projectiles}", True, (0, 255, 0))
        screen.blit(count_text, (10, 520))
        
        pygame.display.flip()
    
    pygame.quit()

if __name__ == "__main__":
    test_gun_flip() 
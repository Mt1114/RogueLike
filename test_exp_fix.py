import pygame
import sys
import os
import time

# 添加项目路径
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))

from modules.player import Player
from modules.enemies.enemy_manager import EnemyManager

def test_exp_fix():
    """测试经验值自动增加问题是否已修复"""
    pygame.init()
    screen = pygame.display.set_mode((1200, 800))
    pygame.display.set_caption("经验值修复测试")
    
    # 创建玩家
    player = Player(600, 400, "ninja_frog")
    
    # 创建敌人管理器
    enemy_manager = EnemyManager()
    enemy_manager.set_map_boundaries(0, 0, 2000, 2000)
    
    # 字体
    font = pygame.font.Font(None, 24)
    
    clock = pygame.time.Clock()
    running = True
    
    # 记录初始经验值
    initial_exp = player.experience
    initial_level = player.level
    
    # 测试时间
    test_duration = 10.0  # 测试10秒
    start_time = time.time()
    
    while running:
        current_time = time.time()
        elapsed_time = current_time - start_time
        
        dt = clock.tick(60) / 1000.0
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
        
        # 更新玩家和敌人管理器
        player.update(dt)
        player.update_weapons(dt)
        enemy_manager.update(dt, player)
        
        # 检查经验值是否自动增加
        current_exp = player.experience
        current_level = player.level
        
        # 清屏
        screen.fill((30, 30, 30))
        
        # 渲染玩家
        player.render(screen)
        
        # 渲染武器和投射物
        player.render_weapons(screen, 0, 0)
        
        # 渲染敌人管理器
        enemy_manager.render(screen, 0, 0, screen.get_width() // 2, screen.get_height() // 2)
        
        # 显示信息
        info_text = [
            "经验值修复测试",
            "",
            "测试内容:",
            "- 检查经验值是否自动增加",
            "- 检查等级是否自动提升",
            "- 测试时间: 10秒",
            "",
            "预期结果:",
            "- 经验值应该保持不变",
            "- 等级应该保持不变",
            "",
            "控制:",
            "ESC: 退出"
        ]
        
        for i, text in enumerate(info_text):
            text_surface = font.render(text, True, (255, 255, 255))
            screen.blit(text_surface, (10, 10 + i * 25))
        
        # 显示当前状态
        status_text = [
            f"测试时间: {elapsed_time:.1f}/10.0秒",
            f"初始经验值: {initial_exp}",
            f"当前经验值: {current_exp}",
            f"经验值变化: {current_exp - initial_exp}",
            f"初始等级: {initial_level}",
            f"当前等级: {current_level}",
            f"等级变化: {current_level - initial_level}",
            f"经验倍率: {player.progression.exp_multiplier:.2f}",
            f"下一级所需经验: {player.exp_to_next_level}"
        ]
        
        # 根据经验值变化设置颜色
        exp_change = current_exp - initial_exp
        level_change = current_level - initial_level
        
        if exp_change == 0 and level_change == 0:
            status_color = (0, 255, 0)  # 绿色 - 正常
        else:
            status_color = (255, 0, 0)  # 红色 - 异常
        
        for i, text in enumerate(status_text):
            text_surface = font.render(text, True, status_color)
            screen.blit(text_surface, (10, 400 + i * 25))
        
        # 显示测试结果
        if elapsed_time >= test_duration:
            if exp_change == 0 and level_change == 0:
                result_text = "✅ 测试通过：经验值没有自动增加"
                result_color = (0, 255, 0)
            else:
                result_text = f"❌ 测试失败：经验值增加了{exp_change}，等级增加了{level_change}"
                result_color = (255, 0, 0)
            
            result_surface = font.render(result_text, True, result_color)
            screen.blit(result_surface, (10, 650))
        
        # 显示武器信息
        weapon_info = []
        for i, weapon in enumerate(player.weapons):
            if hasattr(weapon, 'ammo'):
                weapon_info.append(f"武器{i+1}: {weapon.type} (子弹: {weapon.ammo}/{weapon.max_ammo})")
            else:
                weapon_info.append(f"武器{i+1}: {weapon.type} (等级{weapon.level})")
        
        for i, text in enumerate(weapon_info):
            text_surface = font.render(text, True, (0, 255, 255))
            screen.blit(text_surface, (10, 680 + i * 25))
        
        pygame.display.flip()
        
        # 如果测试时间到了，等待几秒后退出
        if elapsed_time >= test_duration + 3.0:
            running = False
    
    pygame.quit()
    
    # 打印最终结果
    final_exp = player.experience
    final_level = player.level
    print(f"\n=== 经验值修复测试结果 ===")
    print(f"初始经验值: {initial_exp}")
    print(f"最终经验值: {final_exp}")
    print(f"经验值变化: {final_exp - initial_exp}")
    print(f"初始等级: {initial_level}")
    print(f"最终等级: {final_level}")
    print(f"等级变化: {final_level - initial_level}")
    
    if final_exp == initial_exp and final_level == initial_level:
        print("✅ 测试通过：经验值没有自动增加")
    else:
        print("❌ 测试失败：经验值或等级发生了意外变化")

if __name__ == "__main__":
    test_exp_fix() 
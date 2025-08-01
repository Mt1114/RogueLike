import pygame
import sys
import os

# 添加项目路径
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))

from modules.player import Player
from modules.enemies.enemy_manager import EnemyManager
from modules.enemies.enemy import Enemy

def test_death_handling():
    """测试敌人死亡处理逻辑"""
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("敌人死亡处理测试")
    
    # 创建玩家
    player = Player(400, 300, "ninja_frog")
    
    # 创建敌人管理器
    enemy_manager = EnemyManager()
    enemy_manager.set_map_boundaries(0, 0, 2000, 2000)
    
    # 创建一个测试敌人
    try:
        test_enemy = enemy_manager.spawn_enemy('ghost', 500, 300)
        print(f"成功创建敌人: {test_enemy}")
        if test_enemy:
            print(f"敌人类型: {test_enemy.type}")
            print(f"敌人生命值: {test_enemy.health}")
            print(f"敌人配置: {test_enemy.config}")
    except Exception as e:
        print(f"创建敌人失败: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # 字体
    font = pygame.font.Font(None, 24)
    
    clock = pygame.time.Clock()
    running = True
    
    # 记录状态
    initial_exp = player.experience
    initial_level = player.level
    kill_count = 0
    
    print(f"初始状态:")
    print(f"  玩家经验值: {initial_exp}")
    print(f"  玩家等级: {initial_level}")
    print(f"  敌人数量: {len(enemy_manager.enemies)}")
    print(f"  敌人生命值: {test_enemy.health}")
    
    while running:
        dt = clock.tick(60) / 1000.0
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_SPACE:
                    # 手动杀死敌人
                    if test_enemy and test_enemy.alive():
                        print(f"\n手动杀死敌人:")
                        print(f"  杀死前经验值: {player.experience}")
                        print(f"  杀死前等级: {player.level}")
                        
                        # 直接杀死敌人
                        test_enemy.health = 0
                        test_enemy._alive = False
                        
                        # 模拟游戏主循环的死亡处理
                        kill_count += 1
                        if hasattr(test_enemy, 'config') and 'exp_value' in test_enemy.config:
                            exp_reward = test_enemy.config['exp_value']
                            player.add_experience(exp_reward)
                            print(f"  击杀 {test_enemy.type} 获得 {exp_reward} 经验值")
                        
                        print(f"  杀死后经验值: {player.experience}")
                        print(f"  杀死后等级: {player.level}")
                        
                        # 移除敌人
                        enemy_manager.remove_enemy(test_enemy)
                        test_enemy = None
        
        # 更新游戏对象
        player.update(dt)
        enemy_manager.update(dt, player)
        
        # 清屏
        screen.fill((30, 30, 30))
        
        # 渲染玩家
        player.render(screen)
        
        # 渲染敌人
        if test_enemy and test_enemy.alive():
            test_enemy.render(screen, test_enemy.rect.x - 400, test_enemy.rect.y - 300)
        
        # 显示信息
        info_text = [
            "敌人死亡处理测试",
            "",
            "控制:",
            "空格: 手动杀死敌人",
            "ESC: 退出",
            "",
            f"敌人数量: {len(enemy_manager.enemies)}",
            f"敌人存活: {test_enemy.alive() if test_enemy else False}",
            f"敌人生命值: {test_enemy.health if test_enemy else 0}",
            f"击杀数: {kill_count}",
            "",
            f"玩家经验值: {player.experience}",
            f"玩家等级: {player.level}",
            f"经验值变化: {player.experience - initial_exp}",
            f"等级变化: {player.level - initial_level}"
        ]
        
        for i, text in enumerate(info_text):
            text_surface = font.render(text, True, (255, 255, 255))
            screen.blit(text_surface, (10, 10 + i * 25))
        
        pygame.display.flip()
    
    pygame.quit()
    
    # 打印最终结果
    print(f"\n=== 测试结果 ===")
    print(f"初始经验值: {initial_exp}")
    print(f"最终经验值: {player.experience}")
    print(f"经验值变化: {player.experience - initial_exp}")
    print(f"初始等级: {initial_level}")
    print(f"最终等级: {player.level}")
    print(f"等级变化: {player.level - initial_level}")
    print(f"击杀数: {kill_count}")

if __name__ == "__main__":
    test_death_handling() 
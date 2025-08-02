import pygame
import sys
import os

# 添加src目录到路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from modules.dual_player_system import DualPlayerSystem
from modules.game import Game

def test_final_weapon_fix():
    """测试最终武器修复：子弹飞行和武器显示"""
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("最终武器修复测试")
    clock = pygame.time.Clock()
    
    # 创建游戏实例
    game = Game(screen)
    
    # 创建双角色系统
    dual_system = DualPlayerSystem(screen, game)
    
    print("=== 最终武器修复测试 ===")
    print("✅ 游戏和双角色系统已初始化")
    
    # 检查神秘剑士的武器
    mystic = dual_system.mystic_swordsman
    bullet_weapon = None
    for weapon in mystic.weapon_manager.weapons:
        if weapon.type == 'bullet':
            bullet_weapon = weapon
            break
    
    if bullet_weapon:
        print(f"✅ 神秘剑士子弹武器已找到")
        print(f"   初始弹药: {bullet_weapon.ammo}")
        print(f"   初始投射物数量: {len(bullet_weapon.projectiles)}")
    else:
        print("❌ 神秘剑士没有子弹武器")
        return
    
    print("\n=== 控制说明 ===")
    print("神秘剑士移动: 方向键 (↑↓←→)")
    print("神秘剑士攻击: 数字键盘 (2,4,6,8)")
    print("  2 = 向下攻击")
    print("  4 = 向左攻击") 
    print("  6 = 向右攻击")
    print("  8 = 向上攻击")
    print("忍者蛙移动: WASD")
    print("退出: ESC")
    
    print("\n=== 测试要点 ===")
    print("1. 武器只在攻击时显示，平时不显示")
    print("2. 子弹应该飞行，有飞行轨迹")
    print("3. 攻击方向应该正确指向2486方向")
    print("4. 光源方向应该只跟随鼠标，不跟随神秘剑士")
    
    running = True
    attack_count = 0
    
    while running:
        dt = clock.tick(60) / 1000.0
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key in [pygame.K_KP2, pygame.K_KP4, pygame.K_KP6, pygame.K_KP8]:
                    attack_count += 1
                    print(f"\n🎯 攻击 #{attack_count}")
                    
                    # 显示攻击前的状态
                    print(f"   攻击前: 弹药 {bullet_weapon.ammo}, 投射物 {len(bullet_weapon.projectiles)}")
                    
                    # 处理攻击
                    dual_system.handle_event(event)
                    
                    # 显示攻击后的状态
                    print(f"   攻击后: 弹药 {bullet_weapon.ammo}, 投射物 {len(bullet_weapon.projectiles)}")
                    
                    # 检查武器是否正在攻击
                    if bullet_weapon.is_attacking:
                        print(f"   ✅ 武器正在显示 (攻击动画)")
                    else:
                        print(f"   ❌ 武器未显示")
            
            # 处理所有事件
            dual_system.handle_event(event)
        
        # 更新
        dual_system.update(dt)
        
        # 渲染
        screen.fill((50, 50, 50))
        
        # 渲染双角色系统
        dual_system.render(screen, 0, 0)
        dual_system.render_weapons(screen, 0, 0)
        
        # 显示状态信息
        font = pygame.font.Font(None, 20)
        texts = [
            "最终武器修复测试",
            "",
            "神秘剑士移动: 方向键 (↑↓←→)",
            "神秘剑士攻击: 数字键盘 (2,4,6,8)",
            "  2=下, 4=左, 6=右, 8=上",
            "",
            f"攻击次数: {attack_count}",
            f"神秘剑士位置: ({int(dual_system.mystic_swordsman.world_x)}, {int(dual_system.mystic_swordsman.world_y)})",
            f"忍者蛙位置: ({int(dual_system.ninja_frog.world_x)}, {int(dual_system.ninja_frog.world_y)})",
            f"攻击方向: {dual_system.mystic_attack_direction}",
            f"子弹数量: {len(bullet_weapon.projectiles)}",
            f"武器显示: {'是' if bullet_weapon.is_attacking else '否'}",
            f"弹药: {bullet_weapon.ammo}",
            "",
            "按ESC退出"
        ]
        
        for i, text in enumerate(texts):
            if text:  # 跳过空行
                text_surface = font.render(text, True, (255, 255, 255))
                screen.blit(text_surface, (10, 10 + i * 20))
        
        pygame.display.flip()
    
    pygame.quit()
    print(f"\n=== 测试完成 ===")
    print(f"总攻击次数: {attack_count}")

if __name__ == "__main__":
    test_final_weapon_fix() 
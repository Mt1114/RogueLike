import pygame
import sys
import os

# 添加src目录到路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from modules.game import Game
from modules.dual_player_system import DualPlayerSystem

def main():
    """测试子弹飞行和武器显示修复"""
    pygame.init()
    screen = pygame.display.set_mode((1200, 800))
    pygame.display.set_caption("子弹飞行测试")
    clock = pygame.time.Clock()
    
    # 创建游戏实例
    game = Game(screen)
    
    # 初始化双角色系统
    dual_system = DualPlayerSystem(screen, game)
    
    print("=== 子弹飞行和武器显示测试 ===")
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
    print("神秘剑士攻击: 数字键 2,4,6,8")
    print("退出: ESC")
    print("\n=== 测试目标 ===")
    print("1. 武器只在攻击时显示，平时不显示")
    print("2. 子弹应该飞行，有飞行轨迹")
    print("3. 攻击方向应该正确指向2486方向")
    
    attack_count = 0
    running = True
    
    while running:
        dt = clock.tick(60) / 1000.0  # 转换为秒
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                else:
                    # 处理神秘剑士的攻击
                    dual_system.handle_event(event)
                    
                    # 检查是否触发了攻击
                    if event.key in [pygame.K_KP2, pygame.K_KP4, pygame.K_KP6, pygame.K_KP8]:
                        attack_count += 1
                        print(f"\n🎯 攻击 #{attack_count}")
                        print(f"   子弹武器: 弹药 {bullet_weapon.ammo}, 投射物 {len(bullet_weapon.projectiles)}")
                        
                        # 检查武器是否正在攻击
                        if bullet_weapon.is_attacking:
                            print(f"   ✅ 武器正在显示 (攻击动画)")
                        else:
                            print(f"   ❌ 武器未显示")
        
        # 更新游戏状态
        dual_system.update(dt)
        
        # 清屏
        screen.fill((50, 50, 50))
        
        # 渲染游戏
        game.render()
        
        # 渲染武器
        dual_system.render_weapons(screen, game.camera_x, game.camera_y)
        
        # 显示调试信息
        font = pygame.font.Font(None, 24)
        debug_text = [
            f"攻击次数: {attack_count}",
            f"子弹数量: {len(bullet_weapon.projectiles)}",
            f"武器显示: {'是' if bullet_weapon.is_attacking else '否'}",
            f"弹药: {bullet_weapon.ammo}",
            "",
            "按 2,4,6,8 攻击",
            "按 ESC 退出"
        ]
        
        y_offset = 10
        for text in debug_text:
            if text:  # 跳过空行
                text_surface = font.render(text, True, (255, 255, 255))
                screen.blit(text_surface, (10, y_offset))
            y_offset += 25
        
        pygame.display.flip()
    
    pygame.quit()
    print(f"\n=== 测试完成 ===")
    print(f"总攻击次数: {attack_count}")

if __name__ == "__main__":
    main() 
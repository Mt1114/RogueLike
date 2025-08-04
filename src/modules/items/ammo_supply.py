"""
远程攻击补给物品
提供远程武器的弹药补给
"""

import pygame
import random
import math
from .item import Item

class AmmoSupply(Item):
    """远程攻击补给物品"""
    
    def __init__(self, x, y):
        # 先设置图像，再调用父类构造函数
        # 加载补给图标
        try:
            self.image = pygame.image.load("assets/images/weapons/bullet_8x8.png").convert_alpha()
            self.image = pygame.transform.scale(self.image, (32, 32))
        except:
            # 如果加载失败，创建一个默认的黄色圆形图标
            self.image = pygame.Surface((32, 32), pygame.SRCALPHA)
            pygame.draw.circle(self.image, (255, 255, 0), (16, 16), 16)
        
        # 现在调用父类构造函数
        super().__init__(x, y, "ammo_supply")
        
        # 设置碰撞区域
        self.rect = pygame.Rect(x - 16, y - 16, 32, 32)  # 32x32的碰撞区域
        
        # 补给属性
        self.ammo_amount =150  # 每次补给150发
        self.lifetime = 20.0  # 存活20秒
        self.spawn_timer = 0.0  # 生成计时器
        
        # 动画效果（只影响渲染，不影响世界坐标）
        self.bob_timer = 0.0
        self.bob_speed = 2.0
        self.bob_amount = 3.0
        
        # 闪烁效果
        self.blink_timer = 0.0
        self.blink_speed = 0.5
        self.visible = True
        
    def update(self, dt):
        """更新补给物品状态"""
        # 更新存活时间
        self.spawn_timer += dt
        
        # 检查是否超时
        if self.spawn_timer >= self.lifetime:
            return False  # 返回False表示应该销毁
        
        # 更新浮动动画计时器（只用于渲染效果，不影响世界坐标）
        self.bob_timer += dt * self.bob_speed
        
        # 更新碰撞区域位置（使用世界坐标）
        self.rect.centerx = self.world_x
        self.rect.centery = self.world_y
        
        # 闪烁效果（最后10秒开始闪烁）
        if self.spawn_timer >= self.lifetime - 10.0:
            self.blink_timer += dt
            if self.blink_timer >= self.blink_speed:
                self.visible = not self.visible
                self.blink_timer = 0.0
        
        return True  # 返回True表示继续存在
    
    def on_pickup(self, player):
        """被拾取时的处理"""
        # 给玩家的远程武器补充弹药
        if hasattr(player, 'weapon_manager'):
            for weapon in player.weapon_manager.weapons:
                if hasattr(weapon, 'ammo') and not weapon.is_melee:
                    # 确保不超过最大弹药量
                    weapon.ammo = min(weapon.ammo + self.ammo_amount, weapon.max_ammo)
                    print(f"获得弹药补给！武器类型: {weapon.type}, 当前弹药: {weapon.ammo}/{weapon.max_ammo}")
        
        return True  # 返回True表示拾取成功，物品应该被销毁
    
    def render(self, screen, camera_x, camera_y, screen_center_x=None, screen_center_y=None):
        """渲染补给物品"""
        if not self.visible:
            return
            
        # 计算屏幕坐标（使用与门相同的坐标系统）
        if screen_center_x is not None and screen_center_y is not None:
            # 使用与门相同的坐标系统
            screen_x = screen_center_x + (self.world_x - camera_x)
            screen_y = screen_center_y + (self.world_y - camera_y)
        else:
            # 兼容旧的坐标系统
            screen_x = int(self.world_x - camera_x)
            screen_y = int(self.world_y - camera_y)
        
        # 应用浮动效果（只影响渲染位置，不影响世界坐标）
        bob_offset = math.sin(self.bob_timer) * self.bob_amount
        screen_y += int(bob_offset)
        
        # 检查是否在屏幕范围内
        if (screen_x < -50 or screen_x > screen.get_width() + 50 or
            screen_y < -50 or screen_y > screen.get_height() + 50):
            return
        
        # 绘制补给物品
        screen.blit(self.image, (screen_x - self.rect.width // 2, 
                                screen_y - self.rect.height // 2))
        
        # 调试：绘制碰撞区域（红色边框）
        debug_rect = pygame.Rect(screen_x - self.rect.width // 2, 
                                screen_y - self.rect.height // 2,
                                self.rect.width, self.rect.height)
        pygame.draw.rect(screen, (255, 0, 0), debug_rect, 2)
        
        # 绘制剩余时间指示器
        remaining_time = max(0, self.lifetime - self.spawn_timer)
        if remaining_time <= 10.0:  # 最后10秒显示倒计时
            font = pygame.font.Font(None, 20)
            time_text = font.render(f"{remaining_time:.1f}s", True, (255, 255, 255))
            text_rect = time_text.get_rect()
            text_rect.centerx = screen_x
            text_rect.bottom = screen_y - 20
            screen.blit(time_text, text_rect) 
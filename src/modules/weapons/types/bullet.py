import pygame
import math
from ...resource_manager import resource_manager
from ..weapon import Weapon
from ..weapon_stats import WeaponStatType, WeaponStatsDict

class BulletProjectile(pygame.sprite.Sprite):
    """子弹投射物类"""
    def __init__(self, x, y, direction_x, direction_y, stats):
        super().__init__()
        # 加载子弹图像
        self.base_image = resource_manager.load_image('weapon_bullet', 'images/weapons/bullet_8x8.png')
        self.image = self.base_image
        self.rect = self.image.get_rect()
        
        # 位置信息（世界坐标）
        self.world_x = float(x)
        self.world_y = float(y)
        self.rect.centerx = self.world_x
        self.rect.centery = self.world_y
        
        # 方向信息（直线飞行）
        self.direction_x = float(direction_x)
        self.direction_y = float(direction_y)
        
        # 投射物属性
        self.damage = stats.get(WeaponStatType.DAMAGE, 20)
        self.speed = float(stats.get(WeaponStatType.PROJECTILE_SPEED, 400))
        
        # 存活时间
        self.lifetime = stats.get(WeaponStatType.LIFETIME, 3.0)
        self.age = 0.0
        
        # 碰撞相关
        self.hit_count = 0
        self.max_penetration = stats.get(WeaponStatType.PENETRATION, 1)
        self.can_penetrate = self.max_penetration > 1
        self.penetration_damage_reduction = 0.3  # 穿透后伤害减少30%
        
        # 旋转图像以匹配飞行方向
        self._update_image_rotation()
    
    def _update_image_rotation(self):
        """根据飞行方向旋转子弹图像"""
        if self.direction_x == 0 and self.direction_y == 0:
            return
            
        # 计算角度
        angle = math.degrees(math.atan2(-self.direction_y, self.direction_x))
        
        # 旋转图像
        self.image = pygame.transform.rotate(self.base_image, angle)
        self.rect = self.image.get_rect(center=self.rect.center)
    
    def update(self, dt):
        """更新子弹状态"""
        # 更新年龄
        self.age += dt
        
        # 检查生命周期
        if self.age >= self.lifetime:
            self.kill()
            return
        
        # 更新位置
        distance = self.speed * dt
        self.world_x += self.direction_x * distance
        self.world_y += self.direction_y * distance
        
        # 更新矩形位置
        self.rect.centerx = int(self.world_x)
        self.rect.centery = int(self.world_y)
    
    def on_collision(self, enemy, enemies=None):
        """处理与敌人的碰撞"""
        # 检查敌人是否处于无敌状态
        if hasattr(enemy, 'invincible_timer') and enemy.invincible_timer > 0:
            return False
        
        # 造成伤害
        enemy.take_damage(self.damage)
        
        # 增加命中计数
        self.hit_count += 1
        
        # 检查穿透
        if not self.can_penetrate:
            return True  # 销毁子弹
        
        # 如果子弹可以穿透且未达到最大穿透次数
        if self.hit_count < self.max_penetration:
            # 降低伤害
            self.damage *= (1 - self.penetration_damage_reduction)
            return False  # 保持子弹
        
        return True  # 销毁子弹
    
    def render(self, screen, camera_x, camera_y):
        """渲染子弹"""
        # 计算屏幕位置
        screen_x = self.world_x - camera_x + screen.get_width() // 2
        screen_y = self.world_y - camera_y + screen.get_height() // 2
        
        # 渲染子弹
        screen.blit(self.image, (screen_x - self.image.get_width() // 2, 
                                 screen_y - self.image.get_height() // 2))

class BulletWeapon(Weapon):
    """子弹武器类"""
    def __init__(self, player):
        super().__init__(player, 'bullet')
        
        # 攻击动画
        self.attack_animation_timer = 0
        self.attack_animation_duration = 0.2  # 攻击动画持续时间
        self.is_attacking = False
        
        # 子弹系统
        self.ammo = 30  # 初始子弹数量
        self.max_ammo = 30  # 最大子弹数量
        self.is_melee = False  # 标记为远程武器
        
    def get_weapon_image(self):
        """获取武器图像"""
        return resource_manager.load_image('weapon_gun', 'images/weapons/gun.png')
    
    def _perform_attack(self, direction_x, direction_y):
        """执行远程攻击"""
        if not self.can_attack():
            return
        
        # 检查子弹数量
        if self.ammo <= 0:
            print("没有子弹了！")
            return
        
        # 开始攻击动画
        self.is_attacking = True
        self.attack_animation_timer = 0
        
        # 创建子弹
        self._create_bullet(direction_x, direction_y)
        
        # 消耗子弹
        self.ammo -= 1
        
        # 重置攻击计时器
        self.attack_timer = 0
    
    def _create_bullet(self, direction_x, direction_y):
        """创建子弹"""
        # 获取玩家位置
        player_x = self.player.world_x
        player_y = self.player.world_y
        
        # 计算子弹起始位置（稍微偏移以避免与玩家碰撞）
        offset_distance = 30
        start_x = player_x + direction_x * offset_distance
        start_y = player_y + direction_y * offset_distance
        
        # 创建子弹
        bullet = BulletProjectile(start_x, start_y, direction_x, direction_y, self.current_stats)
        self.projectiles.add(bullet)
    
    def update(self, dt):
        """更新武器状态"""
        super().update(dt)
        
        # 更新投射物
        for projectile in self.projectiles:
            projectile.update(dt)
        
        # 移除已销毁的投射物
        self.projectiles = pygame.sprite.Group([p for p in self.projectiles if p.alive()])
        
        # 更新攻击动画
        if self.is_attacking:
            self.attack_animation_timer += dt
            if self.attack_animation_timer >= self.attack_animation_duration:
                self.is_attacking = False
    
    def render(self, screen, camera_x, camera_y):
        """渲染武器和投射物"""
        # 渲染所有子弹
        for projectile in self.projectiles:
            projectile.render(screen, camera_x, camera_y)
        
        # 渲染武器（如果正在攻击）
        if self.is_attacking:
            self._render_weapon_attack(screen, camera_x, camera_y)
    
    def manual_attack(self, screen):
        """手动攻击（鼠标左键触发）"""
        if not self.can_attack():
            return
        
        # 检查子弹数量
        if self.ammo <= 0:
            print("没有子弹了！")
            return
        
        # 获取鼠标位置
        mouse_x, mouse_y = pygame.mouse.get_pos()
        screen_center_x = screen.get_width() // 2
        screen_center_y = screen.get_height() // 2
        
        # 计算射击方向（鼠标方向）
        direction_x = mouse_x - screen_center_x
        direction_y = mouse_y - screen_center_y
        
        # 标准化方向向量
        length = math.sqrt(direction_x**2 + direction_y**2)
        if length > 0:
            direction_x /= length
            direction_y /= length
            
            # 执行攻击
            self._perform_attack(direction_x, direction_y)
    
    def _render_weapon_attack(self, screen, camera_x, camera_y):
        """渲染武器攻击动画"""
        # 获取武器图像
        weapon_image = self.get_weapon_image()
        if not weapon_image:
            return
        
        # 计算玩家屏幕位置
        player_screen_x = screen.get_width() // 2
        player_screen_y = screen.get_height() // 2
        
        # 获取鼠标位置
        mouse_x, mouse_y = pygame.mouse.get_pos()
        
        # 计算鼠标相对于玩家的方向
        direction_x = mouse_x - player_screen_x
        direction_y = mouse_y - player_screen_y
        
        # 标准化方向向量
        length = math.sqrt(direction_x**2 + direction_y**2)
        if length > 0:
            direction_x /= length
            direction_y /= length
        
        # 根据鼠标位置调整枪的位置
        weapon_distance = 25  # 枪与玩家的距离
        
        # 计算枪的位置
        weapon_screen_x = player_screen_x + direction_x * weapon_distance
        weapon_screen_y = player_screen_y + direction_y * weapon_distance
        
        # 根据方向决定是否需要上下翻转
        # 当鼠标在玩家左侧时（direction_x < 0），需要上下翻转
        if direction_x < 0:
            # 当在左侧时，需要调整角度计算
            # 对于左侧，我们需要镜像角度
            angle = math.degrees(math.atan2(direction_y, direction_x))
            # 应用旋转
            rotated_image = pygame.transform.rotate(weapon_image, angle)
            # 上下翻转图像
            flipped_image = pygame.transform.flip(rotated_image, False, True)
            final_image = flipped_image
        else:
            # 右侧正常计算角度
            angle = math.degrees(math.atan2(-direction_y, direction_x))
            # 应用旋转
            rotated_image = pygame.transform.rotate(weapon_image, angle)
            final_image = rotated_image
        
        # 渲染武器
        screen.blit(final_image, (weapon_screen_x - final_image.get_width() // 2,
                                 weapon_screen_y - final_image.get_height() // 2)) 
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
        
        # 记录起始位置（用于距离计算）
        self.start_x = float(x)
        self.start_y = float(y)
        
        # 方向信息（直线飞行）
        self.direction_x = float(direction_x)
        self.direction_y = float(direction_y)
        
        # 投射物属性
        self.damage = stats.get(WeaponStatType.DAMAGE, 20)
        self.speed = float(stats.get(WeaponStatType.PROJECTILE_SPEED, 400))
        
        # 存活时间
        self.lifetime = stats.get(WeaponStatType.LIFETIME, 3.0)
        self.age = 0.0
        
        # 距离限制（640像素）
        self.max_distance = 480.0
        self.distance_traveled = 0.0
        
        # 碰撞相关
        self.hit_count = 0
        self.max_penetration = stats.get(WeaponStatType.PENETRATION, 1)
        self.can_penetrate = self.max_penetration > 1
        self.penetration_damage_reduction = 0.3  # 穿透后伤害减少30%
        
        # 增加碰撞体积
        self.collision_radius = 12  # 碰撞半径（像素）
        
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
        
        # 更新已飞行距离
        self.distance_traveled += distance
        
        # 检查距离限制
        if self.distance_traveled >= self.max_distance:
            self.kill()
            return
        
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
        self.ammo = 300  # 初始子弹数量
        self.max_ammo = 3000  # 最大子弹数量
        self.is_melee = False  # 标记为远程武器
        
        # 装弹系统
        self.shots_fired = 0  # 已发射的子弹数
        self.shots_before_reload = 30  # 装弹前可发射的子弹数
        self.is_reloading = False  # 是否正在装弹
        self.reload_timer = 0  # 装弹计时器
        self.reload_duration = 2.0  # 装弹持续时间（秒）
    
    def get_weapon_image(self):
        """获取武器图像"""
        return resource_manager.load_image('weapon_gun', 'images/weapons/gun.png')
    
    def can_attack(self):
        """检查是否可以攻击"""
        # 检查是否正在装弹
        if self.is_reloading:
            return False
        # 调用父类的can_attack方法
        return super().can_attack()
    
    def _perform_attack(self, direction_x, direction_y):
        """执行远程攻击"""
        if not self.can_attack():
            return
        
        # 检查是否正在装弹
        if self.is_reloading:
            return
        
        # 检查子弹数量（每次射击需要5颗子弹）
        if self.ammo < 5:
            print("no bullet")
            return
        
        # 开始攻击动画
        self.is_attacking = True
        self.attack_animation_timer = 0
        
        # 播放枪声
        resource_manager.play_sound("gun_shot")
        
        # 创建子弹
        self._create_bullet(direction_x, direction_y)
        
        # 消耗子弹（每次射击发射5束子弹）
        self.ammo -= 5
        
        # 增加已发射子弹计数
        self.shots_fired += 5
        
        # 检查是否需要装弹
        if self.shots_fired >= self.shots_before_reload:
            self.is_reloading = True
            self.reload_timer = 0
            self.shots_fired = 0  # 重置已发射子弹计数
            print("开始装弹")
        
        # 重置攻击计时器
        self.attack_timer = 0
    
    def _create_bullet(self, direction_x, direction_y):
        """创建扇形子弹"""
        # 获取玩家位置
        player_x = self.player.world_x
        player_y = self.player.world_y
        
        # 计算主方向的角度
        main_angle = math.atan2(direction_y, direction_x)
        
        # 扇形参数
        spread_angle = math.radians(30)  # 30度扇形
        bullet_count = 5  # 5束子弹
        angle_step = spread_angle / (bullet_count - 1)  # 每束子弹之间的角度间隔
        
        # 计算起始角度（扇形中心向左偏移）
        start_angle = main_angle - spread_angle / 2
        
        # 创建5束子弹
        for i in range(bullet_count):
            # 计算当前子弹的角度
            current_angle = start_angle + i * angle_step
            
            # 计算子弹方向
            bullet_direction_x = math.cos(current_angle)
            bullet_direction_y = math.sin(current_angle)
            
            # 计算子弹起始位置（稍微偏移以避免与玩家碰撞）
            offset_distance = 0
            start_x = player_x + bullet_direction_x * offset_distance
            start_y = player_y + bullet_direction_y * offset_distance
            
            # 创建子弹
            bullet = BulletProjectile(start_x, start_y, bullet_direction_x, bullet_direction_y, self.current_stats)
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
        
        # 更新装弹计时器
        if self.is_reloading:
            self.reload_timer += dt
            if self.reload_timer >= self.reload_duration:
                self.is_reloading = False
                self.reload_timer = 0
                print("装弹完成")
    
    def render(self, screen, camera_x, camera_y, attack_direction_x=None, attack_direction_y=None):
        """渲染武器和投射物"""
        # 渲染所有子弹
        for projectile in self.projectiles:
            projectile.render(screen, camera_x, camera_y)
        
        # 渲染武器（如果正在攻击）
        if self.is_attacking:
            self._render_weapon_attack(screen, camera_x, camera_y, attack_direction_x, attack_direction_y)
    
    def manual_attack(self, screen):
        """手动攻击（鼠标左键触发）"""
        if not self.can_attack():
            return
        
        # 检查子弹数量（每次射击需要5颗子弹）
        if self.ammo < 5:
            print("子弹不足！需要5颗子弹进行扇形射击。")
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
    
    def _render_weapon_attack(self, screen, camera_x, camera_y, attack_direction_x=None, attack_direction_y=None):
        """渲染武器攻击动画"""
        # 获取武器图像
        weapon_image = self.get_weapon_image()
        if not weapon_image:
            return
        
        # 计算神秘剑士的屏幕位置
        player_screen_x = self.player.world_x - camera_x + screen.get_width() // 2
        player_screen_y = self.player.world_y - camera_y + screen.get_height() // 2
        
        # 使用传入的攻击方向，如果没有则使用鼠标方向
        if attack_direction_x is not None and attack_direction_y is not None:
            direction_x = attack_direction_x
            direction_y = attack_direction_y
        else:
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
        
        # 根据攻击方向调整枪的位置
        weapon_distance = 25  # 枪与玩家的距离
        
        # 计算枪的位置
        weapon_screen_x = player_screen_x + direction_x * weapon_distance
        weapon_screen_y = player_screen_y + direction_y * weapon_distance
        
        # 根据方向决定是否需要上下翻转
        # 当攻击方向在玩家左侧时（direction_x < 0），需要上下翻转
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
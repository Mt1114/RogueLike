import pygame
import math
from ...resource_manager import resource_manager
from ..weapon import Weapon
from ..weapon_stats import WeaponStatType, WeaponStatsDict
from ..weapons_data import get_weapon_base_stats

class ThrownKnife(pygame.sprite.Sprite):
    """飞刀投射物类"""
    
    def __init__(self, x, y, direction_x, direction_y, stats):
        super().__init__()
        # 从资源管理器获取飞刀图像并旋转
        original_image = resource_manager.load_image('weapon_knife', 'images/weapons/knife_32x32.png')
        # 计算需要旋转的角度
        angle = math.degrees(math.atan2(direction_y, direction_x))
        # 原始图片刀尖朝上（-90度），需要调整基础角度
        base_angle = -45
        final_angle = -(angle - base_angle)
        self.image = pygame.transform.rotate(original_image, final_angle)
        self.rect = self.image.get_rect()
        self.rect.center = (int(x), int(y))
        
        # 设置飞刀属性
        self.start_x = float(x)  # 起始x坐标，用于动画
        self.start_y = float(y)  # 起始y坐标，用于动画
        self.world_x = float(x)
        self.world_y = float(y)
        self.direction_x = float(direction_x)
        self.direction_y = float(direction_y)
        self.damage = stats.get(WeaponStatType.DAMAGE, 20)  # 默认伤害20
        self.speed = stats.get(WeaponStatType.PROJECTILE_SPEED, 400)  # 默认速度400
        self.lifetime = stats.get(WeaponStatType.LIFETIME, 3.0)  # 默认生命周期3秒
        
        # 穿透相关属性
        self.can_penetrate = stats.get(WeaponStatType.CAN_PENETRATE, False)
        self.max_penetration = stats.get(WeaponStatType.MAX_PENETRATION, 0)
        self.penetration_damage_reduction = stats.get(WeaponStatType.PENETRATION_DAMAGE_REDUCTION, 0.2)
        self.hit_count = 0  # 命中敌人计数
        
        # 投掷动画相关
        self.throw_duration = 0.1  # 投掷动画持续时间
        self.throw_timer = 0  # 投掷动画计时器
        self.throw_progress = 0  # 投掷动画进度
        
        # 存活时间跟踪
        self.time_alive = 0
        
    def update(self, dt):
        # 更新投掷动画进度
        if self.throw_timer < self.throw_duration:
            self.throw_timer += dt
            progress = min(self.throw_timer / self.throw_duration, 1.0)
            self.throw_progress = progress
            
            # 从玩家位置插值到目标位置
            target_x = self.start_x + self.direction_x * self.speed * self.throw_duration
            target_y = self.start_y + self.direction_y * self.speed * self.throw_duration
            
            self.world_x = self.start_x + (target_x - self.start_x) * progress
            self.world_y = self.start_y + (target_y - self.start_y) * progress
        else:
            # 投掷动画结束后，正常移动
            self.world_x += self.direction_x * self.speed * dt
            self.world_y += self.direction_y * self.speed * dt
        
        # 更新碰撞盒位置
        self.rect.centerx = int(self.world_x)
        self.rect.centery = int(self.world_y)
        
        # 更新存活时间
        self.time_alive += dt
        if self.time_alive >= self.lifetime:
            self.kill()
            
    def render(self, screen, camera_x, camera_y):
        # 计算屏幕位置（相对于相机的偏移）
        screen_x = self.world_x - camera_x + screen.get_width() // 2
        screen_y = self.world_y - camera_y + screen.get_height() // 2
        
        # 根据投掷进度缩放图像
        # FIXME: 这里会让小刀变大，感觉很奇怪。 和update中的平滑同时关闭，感觉会好一些。
        if self.throw_timer < self.throw_duration:
            # 在投掷开始时略微放大，然后恢复正常大小
            scale = 1.0 + 0.5 * (1.0 - self.throw_progress)
            scaled_image = pygame.transform.scale(
                self.image,
                (int(self.image.get_width() * scale),
                 int(self.image.get_height() * scale))
            )
            # 调整绘制位置以保持中心点不变
            draw_x = screen_x - scaled_image.get_width() / 2
            draw_y = screen_y - scaled_image.get_height() / 2
            screen.blit(scaled_image, (draw_x, draw_y))
        else:
            # 正常渲染
            screen.blit(self.image, (screen_x - self.rect.width/2, screen_y - self.rect.height/2))

class Knife(Weapon):
    def __init__(self, player):
        super().__init__(player, 'knife')
        
        # 加载武器图像
        self.image = resource_manager.load_image('weapon_knife', 'images/weapons/knife_32x32.png')
        self.rect = self.image.get_rect()

        # 加载攻击音效
        resource_manager.load_sound('knife_throw', 'sounds/weapons/knife_throw.wav')
        
    def update(self, dt):
        super().update(dt)
        
        # 移除自动发射逻辑，改为手动发射
        # 更新已投掷的小刀
        self.projectiles.update(dt)
        
    def get_weapon_image(self):
        """获取武器图像"""
        return self.image
        
    def _render_melee_weapon(self, screen, weapon_image, screen_x, screen_y, 
                            direction_x, direction_y, progress):
        """渲染飞刀近战攻击动画"""
        # 计算武器旋转角度
        angle = math.degrees(math.atan2(-direction_y, direction_x))
        
        # 飞刀的特殊动画：从玩家身后快速挥向前方
        start_distance = -8   # 开始时在玩家身后（更近）
        end_distance = 20     # 结束时在玩家前方（更近）
        
        # 使用更快的缓动函数，模拟快速挥击
        ease_progress = self._ease_out_cubic(progress)
        current_distance = start_distance + (end_distance - start_distance) * ease_progress
        
        # 计算武器位置
        weapon_x = screen_x + direction_x * current_distance
        weapon_y = screen_y + direction_y * current_distance
        
        # 根据攻击进度缩放武器大小
        scale = 1.0 + 0.3 * (1.0 - ease_progress)  # 开始时稍大，结束时正常大小
        scaled_image = pygame.transform.scale(weapon_image, 
                                           (int(weapon_image.get_width() * scale),
                                            int(weapon_image.get_height() * scale)))
        
        # 旋转武器图像
        rotated_image = pygame.transform.rotate(scaled_image, angle)
        
        # 绘制武器
        weapon_rect = rotated_image.get_rect()
        weapon_rect.center = (weapon_x, weapon_y)
        screen.blit(rotated_image, weapon_rect)
        
    def _ease_out_cubic(self, t):
        """三次缓动函数，让飞刀攻击更快更锐利"""
        return 1 - (1 - t) ** 3
        
    def _perform_attack(self, direction_x, direction_y):
        """执行飞刀攻击
        
        Args:
            direction_x: 攻击方向X分量
            direction_y: 攻击方向Y分量
        """
        knives_count = int(self.current_stats[WeaponStatType.PROJECTILES_PER_CAST])
        
        if knives_count > 1:
            # 计算扇形分布
            spread_angle = self.current_stats[WeaponStatType.SPREAD_ANGLE]
            angle_step = spread_angle / (knives_count - 1)
            base_angle = math.degrees(math.atan2(direction_y, direction_x))
            start_angle = base_angle - spread_angle / 2
            
            for i in range(knives_count):
                current_angle = math.radians(start_angle + angle_step * i)
                knife_dir_x = math.cos(current_angle)
                knife_dir_y = math.sin(current_angle)
                self._throw_single_knife(knife_dir_x, knife_dir_y)
        else:
            # 单个小刀直接投掷
            self._throw_single_knife(direction_x, direction_y)
            
        # 播放投掷音效
        resource_manager.play_sound('knife_throw')
        
    def _perform_melee_attack(self, direction_x, direction_y):
        """执行飞刀近战攻击
        
        Args:
            direction_x: 攻击方向X分量
            direction_y: 攻击方向Y分量
        """
        if not self.player.game or not self.player.game.enemy_manager:
            return
            
        enemies = self.player.game.enemy_manager.enemies
        attack_range = 80  # 扩大攻击范围
        attack_damage = self.current_stats.get(WeaponStatType.DAMAGE, 10) * 1.5  # 1.5倍伤害
        
        for enemy in enemies:
            # 计算到敌人的距离
            dx = enemy.rect.x - self.player.world_x
            dy = enemy.rect.y - self.player.world_y
            distance = (dx**2 + dy**2)**0.5
            
            if distance <= attack_range:
                # 计算敌人相对于玩家的方向
                enemy_dir_x = dx / distance if distance > 0 else 0
                enemy_dir_y = dy / distance if distance > 0 else 0
                
                # 计算点积，判断敌人是否在攻击方向的前方
                dot_product = direction_x * enemy_dir_x + direction_y * enemy_dir_y
                
                # 扩大攻击角度范围（从60度扩大到120度）
                if dot_product > -0.5:  # 从0.5改为-0.5，扩大攻击角度
                    # 对敌人造成伤害
                    enemy.take_damage(attack_damage)
                    
                    # 播放攻击音效
                    from ...resource_manager import resource_manager
                    resource_manager.play_sound("melee_attack")
        
    def _throw_single_knife(self, direction_x, direction_y):
        """投掷单个小刀"""
        knife = ThrownKnife(
            self.player.world_x,
            self.player.world_y,
            direction_x,
            direction_y,
            self.current_stats
        )
        self.projectiles.add(knife)
        
    def render(self, screen, camera_x, camera_y):
        # 渲染所有投掷出去的小刀
        for knife in self.projectiles:
            knife.render(screen, camera_x, camera_y)

import pygame
import math
import random
from ...resource_manager import resource_manager
from ..weapon import Weapon
from ..weapon_stats import WeaponStatType, WeaponStatsDict

class FrostExplosionEffect(pygame.sprite.Sprite):
    """冰霜新星爆炸特效"""
    def __init__(self, x, y, radius):
        super().__init__()
        self.world_x = x
        self.world_y = y
        self.radius = radius
        
        # 使用资源管理器的spritesheet和animation功能
        spritesheet = resource_manager.load_spritesheet('frost_explosion', 'images/effects/explosion_64x64.png')
        
        # 创建爆炸动画帧，使用第三行 (row=2)
        animation = resource_manager.create_animation(
            'frost_explosion_anim', spritesheet, 
            frame_width=64, frame_height=64,
            frame_count=8, row=2,
            frame_duration=0.033
        )
        
        self.frames = animation.frames
        self.total_frames = len(self.frames)
        self.animation_speed = animation.frame_duration
        
        self.current_frame = 0
        self.image = pygame.transform.scale(self.frames[0], (128, 128))
        self.rect = self.image.get_rect(center=(int(x), int(y)))
        
        # 动画控制
        self.animation_timer = 0
    
    def update(self, dt):
        # 更新动画
        self.animation_timer += dt
        if self.animation_timer >= self.animation_speed:
            self.animation_timer = 0
            self.current_frame += 1
            if self.current_frame >= len(self.frames):
                # 动画结束，移除特效
                self.kill()
                return
            
            # 更新当前帧
            self.image = self.frames[self.current_frame]
            self.image = pygame.transform.scale(self.image, (128, 128))
            self.rect = self.image.get_rect(center=(int(self.world_x), int(self.world_y)))
    
    def render(self, screen, camera_x, camera_y):
        # 计算屏幕位置
        screen_x = self.world_x - camera_x + screen.get_width() // 2
        screen_y = self.world_y - camera_y + screen.get_height() // 2
        
        # 渲染爆炸效果
        screen.blit(self.image, (screen_x - self.image.get_width() // 2, 
                                 screen_y - self.image.get_height() // 2))

class FrostNovaProjectile(pygame.sprite.Sprite):
    def __init__(self, x, y, direction_x, direction_y, stats):
        super().__init__()
        # 加载基础图像
        self.base_image = resource_manager.load_image('weapon_frost_nova', 'images/weapons/nova_32x32.png')
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
        self.damage = stats.get(WeaponStatType.DAMAGE, 25)
        self.speed = float(stats.get(WeaponStatType.PROJECTILE_SPEED, 250))  # 确保速度是浮点数
        
        # 冰霜特有属性
        self.explosion_radius = stats.get(WeaponStatType.EXPLOSION_RADIUS, 50)
        self.slow_amount = stats.get(WeaponStatType.SLOW_PERCENT, 50) / 100  # 转换为百分比
        self.slow_duration = stats.get(WeaponStatType.FREEZE_DURATION, 2.0)
        
        # 存活时间
        self.lifetime = stats.get(WeaponStatType.LIFETIME, 2.0)
        
        # 动画效果
        self.scale = 1.0
        self.pulse_time = 0
        self.pulse_duration = 0.5

        self.hit_count = 0  # 命中敌人计数
        
        # 特效组引用
        self.effects_group = None
        
        # 设置图像旋转
        self._update_image_rotation()
        
    def _update_image_rotation(self):
        """根据飞行方向旋转图像"""
        angle = math.degrees(math.atan2(-self.direction_y, self.direction_x))  # 注意：pygame的y轴是向下的，所以需要取负
        self.image = pygame.transform.rotate(self.base_image, angle)
        # 保持旋转后的图像中心点不变
        new_rect = self.image.get_rect()
        new_rect.center = self.rect.center
        self.rect = new_rect
        
    def update(self, dt):
        # 直线飞行，不再追踪目标
        self.world_x += self.direction_x * self.speed * dt
        self.world_y += self.direction_y * self.speed * dt
        
        # 更新碰撞盒位置
        self.rect.centerx = round(self.world_x)
        self.rect.centery = round(self.world_y)
        
        # 更新动画
        self.pulse_time = (self.pulse_time + dt) % self.pulse_duration
        self.scale = 1.0 + 0.2 * math.sin(self.pulse_time * 2 * math.pi / self.pulse_duration)
        
        # 更新存活时间
        self.lifetime -= dt
        if self.lifetime <= 0:
            self.kill()

    def render(self, screen, camera_x, camera_y):
        # 计算屏幕位置
        screen_x = self.world_x - camera_x + screen.get_width() // 2
        screen_y = self.world_y - camera_y + screen.get_height() // 2
        
        # 缩放图像
        scaled_size = (int(self.image.get_width() * self.scale),
                      int(self.image.get_height() * self.scale))
        scaled_image = pygame.transform.scale(self.image, scaled_size)
        
        # 调整绘制位置以保持中心点不变
        draw_x = screen_x - scaled_image.get_width() / 2
        draw_y = screen_y - scaled_image.get_height() / 2
        screen.blit(scaled_image, (draw_x, draw_y))

    def apply_slow_effect(self, enemy, slow_amount=None):
        """
        对敌人应用减速效果
        
        Args:
            enemy: 要减速的敌人
            slow_amount: 减速百分比（0-1之间），如果为None则使用默认值
        """
        if slow_amount is None:
            slow_amount = self.slow_amount
            
        # 保存敌人的原始速度（如果还没有保存）
        if not hasattr(enemy, 'original_speed'):
            enemy.original_speed = enemy.speed
            
        # 应用减速效果
        enemy.speed = enemy.original_speed * (1 - slow_amount)
        
        # 设置敌人的减速状态和持续时间
        enemy.is_slowed = True
        enemy.slow_timer = self.slow_duration
        
    def on_collision(self, enemy, enemies=None):
        """
        当冰霜新星与敌人碰撞时调用此方法，触发爆炸效果
        
        Args:
            enemy: 被击中的敌人
            enemies: 游戏中的所有敌人列表
        
        Returns:
            bool: 始终返回True，因为冰霜新星碰撞后总是需要销毁
        """
        # 触发爆炸
        self.explode(enemy, enemies)
        return True
        
    def explode(self, target_enemy, enemies=None):
        """
        冰霜新星爆炸，对范围内的敌人造成伤害和减速效果
        
        Args:
            target_enemy: 冰霜新星碰撞的目标敌人或爆炸位置
            enemies: 游戏中的敌人列表
        """
        # 确定爆炸中心点
        if hasattr(target_enemy, 'rect'):
            # 如果是敌人对象，使用敌人的中心点
            explosion_x = target_enemy.rect.centerx
            explosion_y = target_enemy.rect.centery
        else:
            # 如果是坐标元组或其他，直接使用当前位置
            explosion_x = self.world_x
            explosion_y = self.world_y
        
        # 创建爆炸特效
        if hasattr(self, 'effects_group') and self.effects_group is not None:
            explosion = FrostExplosionEffect(explosion_x, explosion_y, self.explosion_radius)
            self.effects_group.add(explosion)
        
        # 如果有敌人列表，对范围内敌人造成伤害和减速效果
        if enemies:
            # 创建可能受影响的敌人列表（预筛选）
            potential_targets = []
            for enemy in enemies:
                # 先做一个简单的矩形检测，快速排除明显不在范围内的敌人
                if (abs(enemy.rect.centerx - explosion_x) <= self.explosion_radius + enemy.rect.width // 2 and
                    abs(enemy.rect.centery - explosion_y) <= self.explosion_radius + enemy.rect.height // 2):
                    potential_targets.append(enemy)
            
            # 只对可能受影响的敌人进行精确的圆形范围检测
            for enemy in potential_targets:
                # 计算与敌人的距离
                dx = enemy.rect.centerx - explosion_x
                dy = enemy.rect.centery - explosion_y
                distance = math.sqrt(dx * dx + dy * dy)
                
                # 如果在爆炸范围内，造成伤害和减速
                if distance <= self.explosion_radius:
                    # 目标敌人受100%伤害，爆炸范围内敌人受50%伤害
                    damage_multiplier = 1.0 if enemy is target_enemy else 0.5
                    actual_damage = int(self.damage * damage_multiplier)
                    
                    # 造成伤害
                    enemy.take_damage(actual_damage)
                    
                    # 应用减速效果 - 所有被爆炸影响的敌人都会被减速
                    if hasattr(enemy, 'apply_slow_effect'):
                        enemy.apply_slow_effect(self.slow_amount, self.slow_duration)
        
        # 播放爆炸音效
        try:
            resource_manager.play_sound('frost_nova_explode')
        except Exception as e:
            # 在测试环境中可能没有音效资源，忽略错误
            print(f"Warning: Could not play frost explosion sound: {e}")
        
        # 销毁冰霜新星
        self.kill()

class FrostNova(Weapon):
    def __init__(self, player):
        super().__init__(player, 'frost_nova')
        
        # 加载武器图像
        self.image = resource_manager.load_image('weapon_frost_nova', 'images/weapons/nova_32x32.png')
        self.rect = self.image.get_rect()

        # 加载攻击音效
        resource_manager.load_sound('frost_nova_cast', 'sounds/weapons/frost_nova_cast.wav')
        
        # 爆炸特效列表
        self.explosion_effects = pygame.sprite.Group()
        
    def find_nearest_enemy(self, enemies):
        """找到最近的敌人
        
        Args:
            enemies: 敌人列表
            
        Returns:
            Enemy: 最近的敌人，如果没有敌人则返回None
        """
        if not enemies:
            return None
            
        nearest_enemy = None
        min_distance = float('inf')
        
        for enemy in enemies:
            if enemy.alive():
                distance = math.sqrt(
                    (enemy.rect.x - self.player.world_x) ** 2 + 
                    (enemy.rect.y - self.player.world_y) ** 2
                )
                if distance < min_distance:
                    min_distance = distance
                    nearest_enemy = enemy
                    
        return nearest_enemy
        
    def update(self, dt):
        super().update(dt)
        
        # 移除自动发射逻辑，改为手动发射
        # 更新所有冰霜新星
        self.projectiles.update(dt)
        
        # 更新爆炸特效
        self.explosion_effects.update(dt)
        
    def get_weapon_image(self):
        """获取武器图像"""
        return self.image
        
    def _render_melee_weapon(self, screen, weapon_image, screen_x, screen_y, 
                            direction_x, direction_y, progress):
        """渲染冰锥近战攻击动画"""
        # 计算武器旋转角度
        angle = math.degrees(math.atan2(-direction_y, direction_x))
        
        # 冰锥的特殊动画：从玩家手中释放冰霜
        start_distance = -3   # 开始时在玩家手中（更近）
        end_distance = 25     # 结束时在玩家前方（更近）
        
        # 使用冰霜般的缓动函数
        ease_progress = self._ease_out_quart(progress)
        current_distance = start_distance + (end_distance - start_distance) * ease_progress
        
        # 计算武器位置
        weapon_x = screen_x + direction_x * current_distance
        weapon_y = screen_y + direction_y * current_distance
        
        # 根据攻击进度缩放和添加冰霜效果
        base_scale = 1.0 + 0.4 * (1.0 - ease_progress)  # 开始时更大
        # 添加冰霜闪烁效果
        frost_scale = base_scale + 0.15 * math.sin(progress * 15)  # 较慢的闪烁
        
        scaled_image = pygame.transform.scale(weapon_image, 
                                           (int(weapon_image.get_width() * frost_scale),
                                            int(weapon_image.get_height() * frost_scale)))
        
        # 旋转武器图像
        rotated_image = pygame.transform.rotate(scaled_image, angle)
        
        # 绘制武器
        weapon_rect = rotated_image.get_rect()
        weapon_rect.center = (weapon_x, weapon_y)
        screen.blit(rotated_image, weapon_rect)
        
    def _ease_out_quart(self, t):
        """四次缓动函数，让冰锥攻击更流畅"""
        return 1 - (1 - t) ** 4
        
    def _perform_attack(self, direction_x, direction_y):
        """执行冰霜新星攻击
        
        Args:
            direction_x: 攻击方向X分量
            direction_y: 攻击方向Y分量
        """
        # 直接朝鼠标方向发射冰霜新星，不再自动追踪敌人
        self._cast_directional_nova(direction_x, direction_y)
            
        # 播放施法音效
        resource_manager.play_sound('frost_nova_cast')
        
    def _perform_melee_attack(self, direction_x, direction_y):
        """执行冰锥近战攻击
        
        Args:
            direction_x: 攻击方向X分量
            direction_y: 攻击方向Y分量
        """
        if not self.player.game or not self.player.game.enemy_manager:
            return
            
        enemies = self.player.game.enemy_manager.enemies
        attack_range = 90  # 扩大攻击范围
        attack_damage = self.current_stats.get(WeaponStatType.DAMAGE, 10) * 1.8  # 1.8倍伤害
        
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
                    
                    # 应用减速效果
                    if hasattr(enemy, 'apply_slow_effect'):
                        enemy.apply_slow_effect(2, 0.5)  # 2秒减速，速度减半
                    
                    # 播放攻击音效
                    from ...resource_manager import resource_manager
                    resource_manager.play_sound("melee_attack")
        
    def _cast_directional_nova(self, direction_x, direction_y):
        """朝指定方向发射冰霜新星
        
        Args:
            direction_x: 方向X分量
            direction_y: 方向Y分量
        """
        nova = FrostNovaProjectile(
            self.player.world_x,
            self.player.world_y,
            direction_x,
            direction_y,
            self.current_stats
        )
        self.projectiles.add(nova)
        
    def _cast_single_nova(self, target):
        """发射单个冰霜新星（保留用于兼容性）
        
        Args:
            target: 目标敌人
        """
        # 计算朝向目标的方向
        dx = target.rect.centerx - self.player.world_x
        dy = target.rect.centery - self.player.world_y
        distance = math.sqrt(dx * dx + dy * dy)
        
        if distance > 0:
            direction_x = dx / distance
            direction_y = dy / distance
        else:
            direction_x = 1
            direction_y = 0
            
        nova = FrostNovaProjectile(
            self.player.world_x,
            self.player.world_y,
            direction_x,
            direction_y,
            self.current_stats
        )
        self.projectiles.add(nova)
        
    def render(self, screen, camera_x, camera_y):
        # 渲染所有冰霜新星
        for nova in self.projectiles:
            nova.render(screen, camera_x, camera_y)
            
        # 渲染爆炸特效
        for effect in self.explosion_effects:
            effect.render(screen, camera_x, camera_y) 
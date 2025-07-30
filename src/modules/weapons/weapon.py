import pygame
from ..resource_manager import resource_manager
from enum import Enum, auto
from .weapon_stats import WeaponStatType, DEFAULT_WEAPON_STATS
import math
from .weapons_data import get_weapon_base_stats, get_weapon_config

class WeaponType(Enum):
    MELEE = auto()      # 近战武器
    PROJECTILE = auto() # 投射物武器
    
class Weapon(pygame.sprite.Sprite):
    def __init__(self, player, weapon_type):
        super().__init__()
        self.player = player
        self.type = weapon_type

        # 加载武器配置数据
        weapon_stats = get_weapon_base_stats(weapon_type)
        if weapon_stats:
            self.base_stats = weapon_stats.copy()
        else:
            self.base_stats = DEFAULT_WEAPON_STATS.copy()
            
        self.current_stats = self.base_stats.copy()
        
        # 等级
        self.level = 1
        
        # 攻击状态
        self.attack_timer = 0
        self.attack_interval = 1.0 / self.current_stats.get(WeaponStatType.ATTACK_SPEED, 1.0)
        
        # 近战攻击状态
        self.melee_attacking = False
        self.melee_attack_timer = 0
        self.melee_attack_duration = 0.3  # 近战攻击动画持续时间
        self.melee_attack_progress = 0  # 近战攻击进度 (0-1)
        
        # 投射物列表（如果是投射物类型的武器）
        self.projectiles = pygame.sprite.Group()
        
        # 加载配置中的图标路径
        weapon_config = get_weapon_config(weapon_type)
        if weapon_config and 'icon_path' in weapon_config:
            self.icon_path = weapon_config['icon_path']
        else:
            self.icon_path = None
        
    def get_projectiles(self):
        """获取武器的投射物列表，如果没有则返回空列表"""
        return self.projectiles if hasattr(self, 'projectiles') else pygame.sprite.Group()
        
    def handle_collision(self, projectile, enemy, enemies=None):
        """处理武器投射物与敌人的碰撞
        
        Args:
            projectile: 武器的投射物
            enemy: 被击中的敌人
            enemies: 游戏中的所有敌人列表

        Returns:
            bool: 是否应该销毁投射物
        """
        # 检查敌人是否处于无敌状态
        if hasattr(enemy, 'invincible_timer') and enemy.invincible_timer > 0:
            # 敌人处于无敌状态，不计算新的碰撞
            return False
            
        # 检查投射物是否有特殊的碰撞处理方法（如火球的爆炸）
        if hasattr(projectile, 'on_collision'):
            # 调用投射物自己的碰撞处理方法
            return projectile.on_collision(enemy, enemies)
            
        # 默认碰撞处理逻辑
        # 造成伤害
        enemy.take_damage(projectile.damage)
        
        # 增加命中计数（只有在实际造成伤害时才增加）
        projectile.hit_count += 1
        
        # 检查穿透属性
        if not hasattr(projectile, 'can_penetrate') or not projectile.can_penetrate:
            return True
            
        # 如果投射物可以穿透且未达到最大穿透次数，继续保持投射物
        if projectile.hit_count < projectile.max_penetration:
            # 每次穿透后降低伤害
            projectile.damage *= (1 - projectile.penetration_damage_reduction)
            return False
            
        return True
        
    def _apply_player_attack_power(self, attack_power=None):
        """应用玩家的攻击力加成到武器伤害"""
        if WeaponStatType.DAMAGE in self.current_stats:
            # 使用当前伤害值乘以玩家攻击力加成
            current_damage = self.current_stats[WeaponStatType.DAMAGE]
            # 如果提供了attack_power参数，则使用它，否则使用player的值
            multiplier = attack_power if attack_power is not None else self.player.attack_power
            self.current_stats[WeaponStatType.DAMAGE] = int(current_damage * multiplier)
        
    def apply_effects(self, effects):
        """应用升级效果"""
        # 保存旧的攻击间隔用于比较
        old_attack_speed = self.current_stats.get(WeaponStatType.ATTACK_SPEED, 1.0)
        
        # 应用所有效果
        for stat, value in effects.items():
            if stat in self.current_stats and isinstance(value, dict):
                # 处理复杂效果，如 {'multiply': 1.2} 或 {'add': 10}
                if 'multiply' in value:
                    self.current_stats[stat] *= value['multiply']
                elif 'add' in value:
                    self.current_stats[stat] += value['add']
            else:
                # 直接设置值，可能存在base state里面没有，但是后续升级会增加的属性，如：穿透、爆炸等。
                self.current_stats[stat] = value
                    
        # 如果攻击速度改变，更新攻击间隔
        new_attack_speed = self.current_stats.get(WeaponStatType.ATTACK_SPEED, 1.0)
        if new_attack_speed != old_attack_speed:
            self.attack_interval = 1.0 / new_attack_speed
            
        # 在应用效果后重新应用玩家的攻击力加成
        self._apply_player_attack_power()
    
    def get_mouse_direction(self, screen):
        """获取鼠标相对于玩家的方向向量
        
        Args:
            screen: pygame屏幕对象
            
        Returns:
            tuple: (direction_x, direction_y) 标准化后的方向向量
        """
        # 获取鼠标位置
        mouse_x, mouse_y = pygame.mouse.get_pos()
        
        # 获取屏幕中心（玩家在屏幕上的位置）
        screen_center_x = screen.get_width() // 2
        screen_center_y = screen.get_height() // 2
        
        # 计算鼠标相对于屏幕中心的方向
        direction_x = mouse_x - screen_center_x
        direction_y = mouse_y - screen_center_y
        
        # 标准化方向向量
        magnitude = math.sqrt(direction_x ** 2 + direction_y ** 2)
        if magnitude > 0:
            direction_x /= magnitude
            direction_y /= magnitude
        
        return direction_x, direction_y
            
    def can_attack(self):
        """检查是否可以攻击"""
        return self.attack_timer >= self.attack_interval
        
    def manual_attack(self, screen):
        """手动攻击（按J键触发）
        
        Args:
            screen: pygame屏幕对象，用于获取鼠标位置
        """
        if self.can_attack():
            self.attack_timer = 0
            # 获取鼠标方向
            direction_x, direction_y = self.get_mouse_direction(screen)
            # 执行攻击
            self._perform_attack(direction_x, direction_y)
            
    def melee_attack(self, screen):
        """近战攻击（鼠标右键触发）
        
        Args:
            screen: pygame屏幕对象，用于获取鼠标位置
        """
        if self.can_attack() and not self.melee_attacking:
            self.attack_timer = 0
            # 开始近战攻击动画
            self.melee_attacking = True
            self.melee_attack_timer = 0
            self.melee_attack_progress = 0
            # 获取鼠标方向
            direction_x, direction_y = self.get_mouse_direction(screen)
            # 执行近战攻击
            self._perform_melee_attack(direction_x, direction_y)
            
    def _perform_melee_attack(self, direction_x, direction_y):
        """执行近战攻击的具体实现，由子类重写
        
        Args:
            direction_x: 攻击方向X分量
            direction_y: 攻击方向Y分量
        """
        pass
        
    def _perform_attack(self, direction_x, direction_y):
        """执行攻击的具体实现，由子类重写
        
        Args:
            direction_x: 攻击方向X分量
            direction_y: 攻击方向Y分量
        """
        pass
        
    def update(self, dt):
        """更新武器状态"""
        self.attack_timer += dt
        
        # 更新近战攻击动画
        if self.melee_attacking:
            self.melee_attack_timer += dt
            self.melee_attack_progress = min(self.melee_attack_timer / self.melee_attack_duration, 1.0)
            
            # 如果近战攻击动画结束
            if self.melee_attack_progress >= 1.0:
                self.melee_attacking = False
                self.melee_attack_timer = 0
                self.melee_attack_progress = 0
        
    def get_player_direction(self):
        """获取玩家朝向的方向向量"""
        direction_x = self.player.movement.direction.x
        direction_y = self.player.movement.direction.y
        
        # 如果玩家不在移动（方向为0,0），则使用上一个非零方向或默认朝向右侧
        if direction_x == 0 and direction_y == 0:
            if hasattr(self.player.movement, 'last_movement_direction'):
                direction_x = self.player.movement.last_movement_direction.x
                direction_y = self.player.movement.last_movement_direction.y
            else:
                direction_x = 1  # 默认朝向右侧
                direction_y = 0
        
        # 标准化方向向量
        magnitude = math.sqrt(direction_x ** 2 + direction_y ** 2)
        if magnitude > 0:
            direction_x /= magnitude
            direction_y /= magnitude
        
        return direction_x, direction_y
    
    def render(self, screen, camera_x, camera_y):
        """渲染武器"""
        pass
        
    def render_melee_attack(self, screen, camera_x, camera_y, direction_x, direction_y):
        """渲染近战攻击动画
        
        Args:
            screen: pygame屏幕对象
            camera_x: 相机X坐标
            camera_y: 相机Y坐标
            direction_x: 攻击方向X分量
            direction_y: 攻击方向Y分量
        """
        if not self.melee_attacking:
            return
            
        # 计算屏幕位置
        screen_x = self.player.world_x - camera_x + screen.get_width() // 2
        screen_y = self.player.world_y - camera_y + screen.get_height() // 2
        
        # 获取武器图像
        weapon_image = self.get_weapon_image()
        if not weapon_image:
            return
            
        # 根据攻击进度计算武器位置和旋转
        self._render_melee_weapon(screen, weapon_image, screen_x, screen_y, 
                                 direction_x, direction_y, self.melee_attack_progress)
        
    def get_weapon_image(self):
        """获取武器图像，子类可以重写"""
        return self.image if hasattr(self, 'image') else None
        
    def _render_melee_weapon(self, screen, weapon_image, screen_x, screen_y, 
                            direction_x, direction_y, progress):
        """渲染近战武器动画
        
        Args:
            screen: pygame屏幕对象
            weapon_image: 武器图像
            screen_x: 屏幕X坐标
            screen_y: 屏幕Y坐标
            direction_x: 攻击方向X分量
            direction_y: 攻击方向Y分量
            progress: 攻击进度 (0-1)
        """
        # 计算武器旋转角度
        angle = math.degrees(math.atan2(-direction_y, direction_x))
        
        # 根据攻击进度计算武器位置
        # 开始时武器在玩家身后，结束时在玩家前方
        start_distance = -10  # 开始时在玩家身后（更近）
        end_distance = 25     # 结束时在玩家前方（更近）
        
        # 使用缓动函数让动画更自然
        ease_progress = self._ease_out_quad(progress)
        current_distance = start_distance + (end_distance - start_distance) * ease_progress
        
        # 计算武器位置
        weapon_x = screen_x + direction_x * current_distance
        weapon_y = screen_y + direction_y * current_distance
        
        # 旋转武器图像
        rotated_image = pygame.transform.rotate(weapon_image, angle)
        
        # 绘制武器
        weapon_rect = rotated_image.get_rect()
        weapon_rect.center = (weapon_x, weapon_y)
        screen.blit(rotated_image, weapon_rect)
        
    def _ease_out_quad(self, t):
        """缓动函数，让动画更自然"""
        return t * (2 - t)
    
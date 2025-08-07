from ..enemy import Enemy
from ...resource_manager import resource_manager
import pygame
import math

class Soul(Enemy):
    """远程攻击敌人示例类"""
    
    def __init__(self, x, y, enemy_type='soul', difficulty="normal", level=1, scale=None):
        # 调用基类构造函数，传递敌人类型、难度和等级
        super().__init__(x, y, enemy_type, difficulty, level, scale)
        
        # 从配置获取远程攻击相关属性
        self.attack_range = self.config.get("attack_range", 800)        # 攻击距离
        self.min_attack_range = self.config.get("min_attack_range", 300) # 最小攻击距离，太近不会发射
        self.attack_cooldown = 0
        self.attack_cooldown_time = self.config.get("attack_cooldown", 2.0)  # 攻击冷却时间（秒）
        self.projectile_speed = self.config.get("projectile_speed", 180)
        self.projectiles = pygame.sprite.Group()  # 存储投射物
        
        # 加载动画
        self.load_animations()
        
        # 设置初始图像
        self.current_animation = 'idle'
        self.image = self.animations[self.current_animation].get_current_frame()
        # 应用缩放
        original_size = self.image.get_size()
        new_size = (int(original_size[0] * self.scale), int(original_size[1] * self.scale))
        self.image = pygame.transform.scale(self.image, new_size)
        
    def load_animations(self):
        """加载远程敌人的动画"""
        # 获取配置中的动画速度
        animation_speed = self.config.get("animation_speed", 0.0333)
        
        # 加载精灵表 - 使用Soul专用的图片
        idle_spritesheet = resource_manager.load_spritesheet(
            'soul_idle_spritesheet', 'images/enemy/Soul/idle/Soul_idle.png')
        move_spritesheet = resource_manager.load_spritesheet(
            'soul_move_spritesheet', 'images/enemy/Soul/move/Soul_move.png')
        
        # 创建动画 - 竖着的精灵图格式
        # idle: 192*960 = 5帧，每帧192x192
        # move: 192*1536 = 8帧，每帧192x192
        self.animations = {
            'idle': resource_manager.create_animation(
                'soul_idle', idle_spritesheet,
                frame_width=192, frame_height=192,  # 单帧尺寸
                frame_count=5, row=0,  # 5帧
                frame_duration=animation_speed,
                vertical=True  # 标记为竖着的精灵图
            ),
            'walk': resource_manager.create_animation(
                'soul_walk', move_spritesheet,
                frame_width=192, frame_height=192,  # 单帧尺寸
                frame_count=8, row=0,  # 8帧
                frame_duration=animation_speed,
                vertical=True  # 标记为竖着的精灵图
            ),
            'hurt': resource_manager.create_animation(
                'soul_hurt', idle_spritesheet,  # hurt使用idle的图片
                frame_width=192, frame_height=192,  # 单帧尺寸
                frame_count=5, row=0,  # 5帧
                frame_duration=animation_speed,
                vertical=True  # 标记为竖着的精灵图
            )
        }
        
    def update(self, dt, player, second_player=None):
        # 首先调用父类更新方法
        super().update(dt, player, second_player)
        
        # 更新冷却时间
        if self.attack_cooldown > 0:
            self.attack_cooldown -= dt
            
        # 更新投射物
        self.projectiles.update(dt)
        
        # 检查与玩家的碰撞伤害
        self._check_collision_damage(player, second_player)
        
    def render(self, screen, screen_x, screen_y, show_health_bar=True):
        # 创建一个临时的rect用于绘制
        draw_rect = self.rect.copy()
        draw_rect.x = screen_x
        draw_rect.y = screen_y
        
        # 绘制碰撞光圈
        self._render_collision_aura(screen, screen_x, screen_y)
        
        # 绘制敌人
        if hasattr(self, 'image'):
            if self.show_outline:
                # 创建带轮廓的图像
                from ..enemy import create_outlined_sprite
                outlined_image = create_outlined_sprite(
                    self,
                    outline_color=self.outline_color,
                    outline_thickness=self.outline_thickness
                )
                screen.blit(outlined_image, draw_rect)
            else:
                screen.blit(self.image, draw_rect)
        
        # 绘制血条（仅在show_health_bar为True时）
        if show_health_bar:
            # Soul敌人的血条：增长6倍，增宽3倍
            health_bar_width = 32 * self.scale * 3  # 增宽3倍
            health_bar_height = 5 * self.scale * 6   # 增长6倍
            health_ratio = max(0, self.health / self.max_health)  # 确保比例不为负数
            
            # 调整血条位置，使其位于敌人正上方，并向右移动50像素
            bar_x = screen_x - health_bar_width // 2 + 20 + 80  # 居中显示并向右移动50像素
            bar_y = screen_y - 20 * self.scale  # 稍微高一点，确保在敌人正上方
            
            # 根据血量百分比选择颜色
            if health_ratio > 0.8:
                health_color = (0, 255, 0)  # 绿色 (>80%)
            elif health_ratio > 0.2:
                health_color = (255, 255, 0)  # 黄色 (>20%)
            else:
                health_color = (255, 0, 0)  # 红色 (<20%)
            
            # 绘制血条背景（深红色）
            pygame.draw.rect(screen, (100, 0, 0),  # 深红色背景
                            (bar_x, bar_y,
                             health_bar_width, health_bar_height))
            
            # 绘制血条（根据血量百分比选择颜色）
            if health_ratio > 0:
                pygame.draw.rect(screen, health_color,
                                (bar_x, bar_y,
                                 health_bar_width * health_ratio, health_bar_height))
            
            # 绘制血条边框（白色）
            pygame.draw.rect(screen, (255, 255, 255),  # 白色边框
                            (bar_x, bar_y,
                             health_bar_width, health_bar_height), 1)
            
            # 显示血量数值（在血条中央）
            health_text = f"{int(self.health)}/{int(self.max_health)}"
            # 创建字体（根据缩放调整大小）
            font_size = max(8, int(10 * self.scale))
            health_font = pygame.font.SysFont('simHei', font_size)
            health_text_surface = health_font.render(health_text, True, (255, 255, 255))  # 白色文字
            health_text_rect = health_text_surface.get_rect()
            health_text_rect.centerx = bar_x + health_bar_width // 2
            health_text_rect.centery = bar_y + health_bar_height // 2
            
            # 渲染文字阴影（略微偏移）
            shadow_surface = health_font.render(health_text, True, (0, 0, 0))
            shadow_rect = shadow_surface.get_rect()
            shadow_rect.centerx = health_text_rect.centerx + 1
            shadow_rect.centery = health_text_rect.centery + 1
            screen.blit(shadow_surface, shadow_rect)
            
            # 渲染主文字
            screen.blit(health_text_surface, health_text_rect)
        
        # 渲染投射物
        for projectile in self.projectiles:
            # 计算投射物相对于敌人的偏移
            projectile_offset_x = projectile.x - self.rect.centerx
            projectile_offset_y = projectile.y - self.rect.centery
            
            # 计算投射物在屏幕上的位置 = 敌人屏幕位置 + 相对偏移
            projectile_screen_x = screen_x + projectile_offset_x
            projectile_screen_y = screen_y + projectile_offset_y
            
            # 渲染投射物
            screen.blit(projectile.image, 
                      (projectile_screen_x - projectile.image.get_width()//2, 
                       projectile_screen_y - projectile.image.get_height()//2))
        
    def _check_collision_damage(self, player, second_player=None):
        """检查与玩家的碰撞伤害"""
        collision_radius = 200  # 碰撞半径
        
        # 计算碰撞圆心的偏移位置（向右50像素，向下50像素）
        collision_center_x = self.rect.centerx + 50
        collision_center_y = self.rect.centery + 50
        
        # 检查与第一个玩家的碰撞
        if player and player.health > 0:
            distance = math.sqrt((collision_center_x - player.rect.centerx)**2 + 
                               (collision_center_y - player.rect.centery)**2)
            if distance <= collision_radius:
                # 造成碰撞伤害
                collision_damage = self.damage * 0.5  # 碰撞伤害为攻击伤害的一半
                
                # 在双人模式下，如果神秘剑客被击中，伤害转移给忍者蛙
                if hasattr(player, 'hero_type') and player.hero_type == "role2":
                    # 检查是否有双人系统
                    if hasattr(player, 'game') and hasattr(player.game, 'dual_player_system'):
                        # 获取忍者蛙并转移伤害
                        ninja_frog = player.game.dual_player_system.ninja_frog
                        ninja_frog.take_damage(collision_damage)
                        # 让神秘剑客也闪烁
                        if hasattr(player, 'animation') and hasattr(player.animation, 'start_blinking'):
                            invincible_duration = player.health_component.invincible_duration
                            player.animation.start_blinking(invincible_duration)
                        print(f"神秘剑客受到Soul碰撞伤害，忍者蛙受到 {collision_damage} 点伤害")
                    else:
                        # 如果没有双人系统，直接对神秘剑客造成伤害
                        player.take_damage(collision_damage)
                        print(f"神秘剑客受到Soul碰撞伤害: {collision_damage}")
                else:
                    # 忍者蛙被击中，直接造成伤害
                    player.take_damage(collision_damage)
                    print(f"忍者蛙受到Soul碰撞伤害: {collision_damage}")
        
        # 检查与第二个玩家的碰撞
        if second_player and second_player.health > 0:
            distance = math.sqrt((collision_center_x - second_player.rect.centerx)**2 + 
                               (collision_center_y - second_player.rect.centery)**2)
            if distance <= collision_radius:
                # 造成碰撞伤害
                collision_damage = self.damage * 0.5  # 碰撞伤害为攻击伤害的一半
                
                # 在双人模式下，如果神秘剑客被击中，伤害转移给忍者蛙
                if hasattr(second_player, 'hero_type') and second_player.hero_type == "role2":
                    # 检查是否有双人系统
                    if hasattr(second_player, 'game') and hasattr(second_player.game, 'dual_player_system'):
                        # 获取忍者蛙并转移伤害
                        ninja_frog = second_player.game.dual_player_system.ninja_frog
                        ninja_frog.take_damage(collision_damage)
                        # 让神秘剑客也闪烁
                        if hasattr(second_player, 'animation') and hasattr(second_player.animation, 'start_blinking'):
                            invincible_duration = second_player.health_component.invincible_duration
                            second_player.animation.start_blinking(invincible_duration)
                        print(f"神秘剑客受到Soul碰撞伤害，忍者蛙受到 {collision_damage} 点伤害")
                    else:
                        # 如果没有双人系统，直接对神秘剑客造成伤害
                        second_player.take_damage(collision_damage)
                        print(f"神秘剑客受到Soul碰撞伤害: {collision_damage}")
                else:
                    # 忍者蛙被击中，直接造成伤害
                    second_player.take_damage(collision_damage)
                    print(f"忍者蛙受到Soul碰撞伤害: {collision_damage}")
        
    def _render_collision_aura(self, screen, screen_x, screen_y):
        """绘制碰撞光圈"""
        import time
        
        # 获取当前时间用于动画
        current_time = time.time()
        
        # 光圈参数
        collision_radius = 200
        # 移动光圈中心位置（向右50像素，向下50像素）
        center_x = screen_x + self.rect.width // 2 + 50
        center_y = screen_y + self.rect.height // 2 + 50
        
        # 创建渐变光圈效果
        num_circles = 5  # 光圈层数
        base_alpha = 30  # 基础透明度
        
        for i in range(num_circles):
            # 计算当前圈的半径和透明度
            radius = collision_radius - i * 20  # 每圈递减20像素
            alpha = base_alpha - i * 5  # 每圈递减5透明度
            
            # 添加呼吸效果
            breath_factor = 0.5 + 0.3 * math.sin(current_time * 2)  # 呼吸动画
            alpha = int(alpha * breath_factor)
            
            if alpha > 0 and radius > 0:
                # 创建带透明度的表面
                aura_surface = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
                
                # 绘制渐变圆
                for r in range(radius, 0, -2):
                    # 计算当前半径的透明度
                    current_alpha = int(alpha * (r / radius))
                    if current_alpha > 0:
                        color = (255, 255, 255, current_alpha)  # 青色光圈
                        pygame.draw.circle(aura_surface, color, (radius, radius), r, 2)
                
                # 将光圈绘制到屏幕上
                screen.blit(aura_surface, (center_x - radius, center_y - radius))
        
    def attack(self, player, dt, second_player=None):
        """
        实现基类的抽象方法，远程攻击逻辑
        
        Args:
            player: 攻击目标（玩家）
            dt: 时间增量
            second_player: 第二个玩家（可选）
            
        Returns:
            bool: 攻击是否命中
        """
        # 选择最近的目标
        target_player = self._get_nearest_player(player, second_player)
        
        # 更新所有投射物
        hit = False
        for projectile in list(self.projectiles):
            # 检查投射物是否击中玩家
            if self._check_projectile_hit(projectile, target_player):
                projectile.kill()
                hit = True
                
        # 如果冷却完成，检查是否可以进行新的攻击
        if self.attack_cooldown <= 0:
            # 计算到目标玩家的距离
            dx = target_player.world_x - self.rect.centerx
            dy = target_player.world_y - self.rect.centery
            distance = math.sqrt(dx * dx + dy * dy)
            
            # 如果在攻击范围内但不是太近
            if self.min_attack_range < distance < self.attack_range:
                # 计算攻击方向
                if distance > 0:
                    direction_x = dx / distance
                    direction_y = dy / distance
                    
                    # 发射投射物
                    print(f"Soul 发射投射物，目标: {target_player.hero_type}")
                    self._fire_projectile(direction_x, direction_y)
                    
                    # 重置攻击冷却
                    self.attack_cooldown = self.attack_cooldown_time
                    
        return hit
                
    def _fire_projectile(self, direction_x, direction_y):
        """
        发射投射物
        
        Args:
            direction_x: X方向单位向量
            direction_y: Y方向单位向量
        """
        # 创建投射物，使用rect中心坐标
        projectile = RangerProjectile(
            self.rect.centerx, 
            self.rect.centery,
            direction_x,
            direction_y,
            self.damage,
            self.projectile_speed
        )
        self.projectiles.add(projectile)
        
        # 同时添加到敌人管理器的投射物列表中
        if hasattr(self, 'game') and hasattr(self.game, 'enemy_manager'):
            self.game.enemy_manager.enemy_projectiles.append(projectile)
            print(f"投射物已添加到enemy_projectiles，当前数量: {len(self.game.enemy_manager.enemy_projectiles)}")
        else:
            print(f"无法添加投射物到enemy_projectiles，game或enemy_manager不存在")
        
    def _check_projectile_hit(self, projectile, player):
        """
        检查投射物是否击中玩家
        
        Args:
            projectile: 投射物对象
            player: 玩家对象
            
        Returns:
            bool: 是否击中
        """
        # 计算投射物和玩家之间的距离
        dx = projectile.x - player.world_x
        dy = projectile.y - player.world_y
        distance = math.sqrt(dx * dx + dy * dy)
        
        # 如果距离小于碰撞半径，则判定为击中
        if distance < player.rect.width / 2 + projectile.radius:
            # 在双人模式下，如果神秘剑客被击中，伤害转移给忍者蛙
            if hasattr(player, 'hero_type') and player.hero_type == "role2":
                # 检查是否有双人系统
                if hasattr(player, 'game') and hasattr(player.game, 'dual_player_system'):
                    # 获取忍者蛙并转移伤害
                    ninja_frog = player.game.dual_player_system.ninja_frog
                    ninja_frog.take_damage(projectile.damage)
                    # 让神秘剑客也闪烁
                    if hasattr(player, 'animation') and hasattr(player.animation, 'start_blinking'):
                        invincible_duration = player.health_component.invincible_duration
                        player.animation.start_blinking(invincible_duration)
                    print(f"神秘剑客被Soul投射物击中，忍者蛙受到 {projectile.damage} 点伤害")
                else:
                    # 如果没有双人系统，直接对神秘剑客造成伤害
                    player.take_damage(projectile.damage)
                    print(f"神秘剑客被Soul投射物击中，受到 {projectile.damage} 点伤害")
            else:
                # 忍者蛙被击中，直接造成伤害
                player.take_damage(projectile.damage)
                print(f"忍者蛙被Soul投射物击中，受到 {projectile.damage} 点伤害")
            
            return True
            
        return False


class RangerProjectile(pygame.sprite.Sprite):
    """远程敌人的投射物类"""
    
    def __init__(self, x, y, direction_x, direction_y, damage, speed):
        super().__init__()
        # 基本属性
        self.x = x  # 投射物的世界 x 坐标
        self.y = y  # 投射物的世界 y 坐标
        self.direction_x = direction_x  # 横向方向向量（已归一化）
        self.direction_y = direction_y  # 纵向方向向量（已归一化）
        self.damage = damage  # 投射物伤害
        self.speed = speed  # 投射物速度
        self.radius = 4  # 碰撞半径，减小碰撞大小
        self.lifetime = 5.0  # 生命周期（秒）
        
        # 创建更大更明显的投射物图像
        self.image = pygame.Surface((16, 16), pygame.SRCALPHA)
        pygame.draw.circle(self.image, (0, 200, 0), (10, 10), 10)  # 红色圆形投射物
        
        # 根据方向添加"尾巴"，使弹道更明显
        end_x = 8 - int(direction_x * 8)
        end_y = 8 - int(direction_y * 8)
        pygame.draw.line(self.image, (255, 200, 200), (8, 8), (end_x, end_y), 3)
        
        # 设置rect用于渲染和碰撞检测
        self.rect = self.image.get_rect(center=(x, y))
        
    def update(self, dt):
        """更新投射物状态"""
        # 按照固定方向和速度更新位置
        self.x += self.direction_x * self.speed * dt
        self.y += self.direction_y * self.speed * dt
        
        # 更新rect位置
        self.rect.center = (self.x, self.y)
        
        # 更新生命周期
        self.lifetime -= dt
        if self.lifetime <= 0:
            self.kill()
            
    def render(self, screen, camera_x, camera_y):
        """渲染投射物(已在Soul的render方法中实现，此方法不再使用)"""
        pass
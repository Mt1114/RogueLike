import pygame
import math
from ..enemy import Enemy
from ...resource_manager import resource_manager

class EnemyProjectile(pygame.sprite.Sprite):
    """敌人子弹类"""
    def __init__(self, x, y, direction_x, direction_y, speed, damage):
        super().__init__()
        
        # 位置信息
        self.world_x = float(x)
        self.world_y = float(y)
        
        # 方向信息
        self.direction_x = float(direction_x)
        self.direction_y = float(direction_y)
        
        # 属性
        self.speed = float(speed)
        self.damage = int(damage)
        
        # 生命周期
        self.lifetime = 5.0  # 5秒后自动销毁
        
        # 加载子弹图片 - 使用指定的图片资源
        try:
            bullet_image = resource_manager.load_image('enemy_bullet', 'images/enemy/Soul/attack/bullet.png')
            # 裁剪第一个192*192的区域
            self.image = pygame.Surface((192, 192), pygame.SRCALPHA)
            self.image.blit(bullet_image, (0, 0), (0, 0, 192, 192))
            # 缩放为合适的大小
            self.image = pygame.transform.scale(self.image, (16, 16))
        except:
            # 如果加载失败，使用默认的红色圆形
            self.image = pygame.Surface((8, 8), pygame.SRCALPHA)
            pygame.draw.circle(self.image, (255, 0, 0), (4, 4), 4)
        
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

class SoulBoss(Enemy):
    """Soul Boss - 强大的boss敌人"""
    
    def __init__(self, x, y, enemy_type, difficulty="normal", level=1):
        super().__init__(x, y, enemy_type, difficulty, level)
        self.type = "soul_boss"
        
        # 加载动画
        self.load_animations()
        
        # 攻击相关
        self.attack_timer = 0
        self.attack_cooldown = self.config.get('attack_cooldown', 1.0)
        self.projectile_speed = self.config.get('projectile_speed', 200)
        self.attack_range = self.config.get('attack_range', 1000)
        self.min_attack_range = self.config.get('min_attack_range', 200)
        
        # 设置初始动画
        self.current_animation = self.idle_animation
        self.image = self.current_animation.get_current_frame()
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        
        # 碰撞箱
        self.collision_rect = pygame.Rect(0, 0, 64, 64)
        self.collision_rect.center = self.rect.center
        
    def load_animations(self):
        """加载所有动画"""
        # Idle动画 - 192*960，裁剪成5个
        idle_spritesheet = resource_manager.load_spritesheet('soul_boss_idle', 'images/enemy/Soul/idle/Soul_idle.png')
        self.idle_animation = resource_manager.create_animation(
            'soul_boss_idle', idle_spritesheet,
            frame_width=192, frame_height=192,
            frame_count=5, row=0,
            frame_duration=self.config.get('animation_speed', 0.0333)
        )
        
        # Move动画 - 192*1536，裁剪成8个
        move_spritesheet = resource_manager.load_spritesheet('soul_boss_move', 'images/enemy/Soul/move/Soul_move.png')
        self.move_animation = resource_manager.create_animation(
            'soul_boss_move', move_spritesheet,
            frame_width=192, frame_height=192,
            frame_count=8, row=0,
            frame_duration=self.config.get('animation_speed', 0.0333)
        )
        
        # Attack动画 - 192*1920，裁剪成10个
        attack_spritesheet = resource_manager.load_spritesheet('soul_boss_attack', 'images/enemy/Soul/attack/Soul_attack.png')
        self.attack_animation = resource_manager.create_animation(
            'soul_boss_attack', attack_spritesheet,
            frame_width=192, frame_height=192,
            frame_count=10, row=0,
            frame_duration=self.config.get('animation_speed', 0.0333)
        )
        
        # 子弹动画 - 192*768，裁剪成4个
        bullet_spritesheet = resource_manager.load_spritesheet('soul_boss_bullet', 'images/enemy/Soul/attack/bullet.png')
        self.bullet_animation = resource_manager.create_animation(
            'soul_boss_bullet', bullet_spritesheet,
            frame_width=192, frame_height=192,
            frame_count=4, row=0,
            frame_duration=0.1
        )
        
    def update(self, dt, player):
        """更新boss状态"""
        super().update(dt, player)
        
        # 更新攻击计时器
        self.attack_timer += dt
        
        # 计算与玩家的距离 - 使用和普通怪物一样的坐标系统
        dx = player.world_x - self.rect.x
        dy = player.world_y - self.rect.y
        distance = math.sqrt(dx*dx + dy*dy)
        
        # 决定行为 - 使用和普通怪物一致的逻辑
        if distance <= self.attack_range and distance >= self.min_attack_range:
            # 在攻击范围内，进行攻击
            self.attack(player, dt)
        else:
            # 不在攻击范围内，移动
            self._move_towards_player(dt, player, dx, dy, distance)
            
        # 更新动画
        self._update_animation(dt)
        
    def attack(self, player, dt):
        """攻击玩家方法，实现抽象方法"""
        # 计算与玩家的距离
        dx = player.world_x - self.rect.x
        dy = player.world_y - self.rect.y
        distance = math.sqrt(dx*dx + dy*dy)
        
        # 如果在攻击范围内
        if distance < self.attack_range and distance >= self.min_attack_range:
            # 切换到攻击动画
            if self.current_animation != self.attack_animation:
                self.current_animation = self.attack_animation
                self.current_animation.reset()
            
            # 检查攻击冷却
            if self.attack_timer >= self.attack_cooldown:
                # 发射子弹
                self._fire_projectile(player, dx, dy)
                self.attack_timer = 0
                return True
        
        return False
        
    def _attack_player(self, dt, player, dx, dy, distance):
        """攻击玩家"""
        # 切换到攻击动画
        if self.current_animation != self.attack_animation:
            self.current_animation = self.attack_animation
            self.current_animation.reset()
        
        # 检查攻击冷却
        if self.attack_timer >= self.attack_cooldown:
            # 使用和普通怪物一致的攻击方式
            self.attack_player(player)
            self.attack_timer = 0
            
    def _fire_projectile(self, player, dx, dy):
        """发射子弹"""
        # 计算子弹方向
        distance = math.sqrt(dx*dx + dy*dy)
        if distance > 0:
            direction_x = dx / distance
            direction_y = dy / distance
        else:
            direction_x = 1
            direction_y = 0
            
        # 创建敌人子弹
        bullet = EnemyProjectile(
            self.rect.x, self.rect.y,
            direction_x, direction_y,
            self.projectile_speed,
            self.damage
        )
        
        # 将子弹添加到游戏中的敌人子弹列表
        # 通过player.game来访问游戏系统
        if hasattr(player, 'game') and player.game and hasattr(player.game, 'enemy_manager'):
            if not hasattr(player.game.enemy_manager, 'enemy_projectiles'):
                player.game.enemy_manager.enemy_projectiles = []
            player.game.enemy_manager.enemy_projectiles.append(bullet)
            print(f"Boss发射子弹，当前子弹数量: {len(player.game.enemy_manager.enemy_projectiles)}")
            
    def _move_towards_player(self, dt, player, dx, dy, distance):
        """向玩家移动"""
        # 切换到移动动画
        if self.current_animation != self.move_animation:
            self.current_animation = self.move_animation
            self.current_animation.reset()
            
        # 计算移动方向
        if distance > 0:
            direction_x = dx / distance
            direction_y = dy / distance
        else:
            direction_x = 0
            direction_y = 0
            
        # 移动 - 使用和普通怪物一样的坐标系统
        self.rect.x += direction_x * self.speed * dt
        self.rect.y += direction_y * self.speed * dt
        
    def _update_animation(self, dt):
        """更新动画"""
        # 更新当前动画
        self.current_animation.update(dt)
        self.image = self.current_animation.get_current_frame()
        
        # 更新碰撞箱和位置 - 使用和普通怪物一样的坐标系统
        old_center = self.rect.center
        self.rect = self.image.get_rect()
        self.rect.center = old_center
        self.collision_rect.center = self.rect.center
        
    def render(self, screen, screen_x, screen_y, show_health_bar=True):
        """渲染boss"""
        # 创建一个临时的rect用于绘制
        draw_rect = self.rect.copy()
        draw_rect.x = screen_x
        draw_rect.y = screen_y
        
        # 渲染boss图像
        screen.blit(self.image, draw_rect)
        
        # 渲染血条（boss血条更明显）
        if show_health_bar:
            self._render_health_bar(screen, screen_x, screen_y)
        
    def _render_health_bar(self, screen, x, y):
        """渲染血条"""
        bar_width = 100
        bar_height = 8
        health_ratio = self.health / self.max_health
        
        # 血条背景
        bg_rect = pygame.Rect(x - bar_width//2, y - 50, bar_width, bar_height)
        pygame.draw.rect(screen, (100, 0, 0), bg_rect)
        
        # 血条
        health_rect = pygame.Rect(x - bar_width//2, y - 50, int(bar_width * health_ratio), bar_height)
        pygame.draw.rect(screen, (255, 0, 0), health_rect)
        
        # 血条边框
        pygame.draw.rect(screen, (255, 255, 255), bg_rect, 1) 
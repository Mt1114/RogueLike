import pygame
import math
from .resource_manager import resource_manager
from .weapons.types.knife import Knife
from .weapons.types.fireball import Fireball
from .weapons.types.frost_nova import FrostNova
from .weapons.types.bullet import BulletWeapon
from .upgrade_system import UpgradeType, WeaponUpgradeLevel, PassiveUpgradeLevel
from .hero_config import get_hero_config
from .utils import create_outlined_sprite
from .components.components import (
    MovementComponent,
    AnimationComponent,
    HealthComponent,
    WeaponManager,
    PassiveManager,
    ProgressionSystem
)
class Player(pygame.sprite.Sprite):
    def __init__(self, x, y, hero_type="ninja_frog"):
        super().__init__()
        
        # 加载英雄配置
        self.hero_config = get_hero_config(hero_type)
        self.hero_type = hero_type
        
        # 世界坐标（实际位置）
        self.world_x = x
        self.world_y = y
        
        # 游戏实例引用（用于获取敌人列表等）
        self.game = None
        
        # 钥匙状态 - 改为支持多把钥匙
        self.keys_collected = 0  # 收集的钥匙数量
        self.total_keys_needed = 3  # 需要收集的总钥匙数量
        
        # 初始化各组件
        self._init_components()
        
        # 设置初始图像和碰撞矩形
        self.image = self.animation.get_current_frame()
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        
        # 调整碰撞箱大小以适配64x64像素的角色图片
        # 保持碰撞箱为64x64像素，与图像大小一致
        self.collision_rect = pygame.Rect(0, 0, 64, 64)
        self.collision_rect.center = self.rect.center
        
        # 创建遮罩
        self.mask = None
        self.update_mask()
        
        # 轮廓相关
        self.show_outline = False
        self.outline_color = (255, 0, 0)  # 默认红色轮廓
        self.outline_thickness = 1
        
        # 大招相关
        self.ultimate_active = False
        self.ultimate_timer = 0
        self.ultimate_duration = 1.0  # 大招持续时间1秒
        self.ultimate_damage = 60  # 大招伤害
        self.ultimate_distance = 256  # 大招移动距离
        self.ultimate_start_x = 0  # 大招开始位置
        self.ultimate_start_y = 0
        self.ultimate_direction_x = 0  # 大招方向
        self.ultimate_direction_y = 0
        self.ultimate_hit_enemies = set()  # 已经造成伤害的敌人
        self.ultimate_cooldown = 15.0  # 大招CD时间
        self.ultimate_cooldown_timer = 0  # 大招CD计时器
        self.ultimate_icon = None  # 大招图标
        
        # 穿墙技能相关（仅对忍者蛙）
        self.phase_through_walls = False  # 是否处于穿墙状态
        self.phase_timer = 0  # 穿墙持续时间计时器
        self.phase_duration = 2.0  # 穿墙持续时间2秒
        self.phase_cooldown = 15.0  # 穿墙CD时间
        self.phase_cooldown_timer = 0  # 穿墙CD计时器
        self.phase_icon = None  # 穿墙技能图标
        
        # 武器切换相关（仅对神秘剑士）
        self.is_ranged_mode = True  # True为远程模式，False为近战模式
        
        # 添加初始武器
        starting_weapon = self.hero_config.get("starting_weapon", "bullet")
        self.add_weapon(starting_weapon)  # 添加远程武器（手枪）
        self.add_weapon("knife")  # 添加近战武器（刀）
        
        # 加载大招图标（仅对role2角色）
        if self.hero_type == "role2":
            self._load_ultimate_icon()
        
        # 加载穿墙技能图标（仅对忍者蛙）
        if self.hero_type == "ninja_frog":
            self._load_phase_icon()
        
    def _init_components(self):
        """初始化所有组件"""
        
        # 基础属性
        base_stats = self.hero_config["base_stats"]
        
        # 1. 动画组件
        self.animation = AnimationComponent(self)
        self.animation.load_animations(self.hero_config["animations"])
        
        # 2. 移动组件
        self.movement = MovementComponent(self, speed=base_stats["speed"])
        
        # 3. 生命值组件
        self.health_component = HealthComponent(
            self,
            max_health=base_stats["max_health"],
            defense=base_stats["defense"],
            health_regen=base_stats["health_regen"]
        )
        # 设置受伤回调
        self.health_component.on_damaged = self._on_damaged
        
        # 4. 武器管理器
        self.weapon_manager = WeaponManager(self)
        self.weapon_manager.available_weapons = {
            'knife': Knife,
            'fireball': Fireball,
            'frost_nova': FrostNova,
            'bullet': BulletWeapon
        }
        
        # 5. 被动技能管理器
        self.passive_manager = PassiveManager(self)
        self.passive_manager.on_stats_changed = self._update_stats
        
        # 6. 进阶系统
        self.progression = ProgressionSystem(self, base_exp_multiplier=base_stats["exp_multiplier"])
        self.progression.set_luck(base_stats["luck"])
        
        # 其他属性（兼容旧接口）
        self.pickup_range = base_stats["pickup_range"]
        self.attack_power = base_stats["attack_power"]
        
    def _on_damaged(self, amount):
        """受伤回调"""
        # 设置动画为受伤状态
        self.animation.set_animation('hurt')
        
    def _update_stats(self):
        """更新玩家属性"""
        # 获取基础属性
        base_stats = self.hero_config["base_stats"].copy()
        
        # 计算被动加成后的属性
        final_stats = self.passive_manager.calculate_stats(base_stats)
        
        # 应用属性到各组件
        self.movement.set_speed(final_stats["speed"])
        
        self.health_component.max_health = final_stats["max_health"]
        self.health_component.defense = final_stats["defense"]
        self.health_component.health_regen = final_stats["health_regen"]
        
        self.progression.set_exp_multiplier(final_stats["exp_multiplier"])
        self.progression.set_luck(final_stats["luck"])
        
        # 更新其他属性
        self.pickup_range = final_stats["pickup_range"]
        self.attack_power = final_stats["attack_power"]
        
        # 更新武器攻击力
        self.weapon_manager.apply_attack_power(self.attack_power)
        
    # 兼容旧接口的属性访问器
    @property
    def health(self):
        return self.health_component.health
        
    @health.setter
    def health(self, value):
        self.health_component.health = value
        
    @property
    def max_health(self):
        return self.health_component.max_health
        
    @property
    def defense(self):
        return self.health_component.defense
        
    @property
    def invincible(self):
        return self.health_component.invincible
        
    @property
    def weapons(self):
        return self.weapon_manager.weapons
        
    @property
    def weapon_levels(self):
        return self.weapon_manager.weapon_levels
        
    @property
    def passives(self):
        return self.passive_manager.passives
        
    @property
    def passive_levels(self):
        return self.passive_manager.passive_levels
        
    @property
    def level(self):
        return self.progression.level
        
    @property
    def experience(self):
        return self.progression.experience
        
    @property
    def exp_to_next_level(self):
        return self.progression.exp_to_next_level
        
    @property
    def coins(self):
        return self.progression.coins
        
    @coins.setter
    def coins(self, value):
        self.progression.coins = value
        
    @property
    def luck(self):
        return self.progression.luck
    
    # 公共方法 - 保持与旧接口兼容
    def handle_event(self, event):
        """处理输入事件"""
        self.movement.handle_event(event)
        
        # 处理U键远程攻击
        if event.type == pygame.KEYDOWN and event.key == pygame.K_u:
            # 获取屏幕对象（从游戏实例获取）
            if self.game and hasattr(self.game, 'screen'):
                self.weapon_manager.manual_attack(self.game.screen)
                
        # 处理K键近战攻击
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_k:
            # 获取屏幕对象（从游戏实例获取）
            if self.game and hasattr(self.game, 'screen'):
                self.weapon_manager.melee_attack(self.game.screen)
        
        # 处理小键盘5键大招（仅对role2角色）
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_KP5:
            if self.hero_type == "role2" and not self.ultimate_active:
                self.activate_ultimate()
        
        # 处理穿墙技能（仅对忍者蛙）
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            if self.hero_type == "ninja_frog" and not self.phase_through_walls and self.phase_cooldown_timer <= 0:
                self.activate_phase_through_walls()
        
        # 处理武器切换（仅对神秘剑士）
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_1:
            if self.hero_type == "role2":  # 神秘剑士
                self.toggle_weapon_mode()
        
    def update(self, dt):
        """更新玩家状态"""
        # 更新大招CD计时器
        if self.ultimate_cooldown_timer > 0:
            self.ultimate_cooldown_timer -= dt
            if self.ultimate_cooldown_timer < 0:
                self.ultimate_cooldown_timer = 0
        
        # 更新穿墙技能CD计时器
        if self.phase_cooldown_timer > 0:
            self.phase_cooldown_timer -= dt
            if self.phase_cooldown_timer < 0:
                self.phase_cooldown_timer = 0
        
        # 更新各组件（始终更新）
        self.movement.update(dt)
        self.animation.update(dt)
        self.health_component.update(dt)
        
        # 更新大招状态
        if self.ultimate_active:
            self.update_ultimate(dt)
        # 更新穿墙技能状态
        elif self.phase_through_walls:
            self.update_phase_through_walls(dt)
        else:
            # 更新动画状态（仅在非大招和非穿墙状态下）
            self._update_animation_state()
        
        # 更新武器（包括投射物移动）
        self.update_weapons(dt)
        
        # 更新当前图像
        self.image = self.animation.get_current_frame(not self.movement.facing_right)
        
        # 更新碰撞箱位置（使用世界坐标）
        self.collision_rect.center = (self.world_x, self.world_y)
        
        # 更新遮罩
        self.update_mask()
        
    def update_mask(self):
        """更新精灵遮罩"""
        self.mask = pygame.mask.from_surface(self.image)
        
    def toggle_outline(self, show=None, color=None, thickness=None):
        """
        切换是否显示轮廓
        
        Args:
            show: 是否显示轮廓，None表示切换当前状态
            color: 轮廓颜色，None表示使用当前颜色
            thickness: 轮廓粗细，None表示使用当前粗细
        """
        if show is not None:
            self.show_outline = show
        else:
            self.show_outline = not self.show_outline
            
        if color is not None:
            self.outline_color = color
            
        if thickness is not None:
            self.outline_thickness = thickness
        
    def render(self, screen):
        """渲染玩家"""
        if not self.health_component.invincible or self.animation.visible:
            # 如果在穿墙状态，使用特殊动画
            if hasattr(self, 'phase_through_walls') and self.phase_through_walls and hasattr(self, 'phase_animation_image') and self.phase_animation_image:
                # 使用穿墙动画图片
                current_frame = self.phase_animation_image
            else:
                # 获取当前动画帧
                current_frame = self.animation.get_current_frame(not self.movement.facing_right)
            
            if current_frame:
                # 图像已经是64x64像素，不需要缩放
                if self.show_outline:
                    # 创建带轮廓的图像
                    outlined_image = create_outlined_sprite(
                        current_frame,
                        outline_color=self.outline_color,
                        outline_thickness=self.outline_thickness
                    )
                    screen.blit(outlined_image, self.rect)
                else:
                    screen.blit(current_frame, self.rect)
            
    def _update_animation_state(self):
        """更新动画状态"""
        # 如果在大招状态，不切换动画
        if self.ultimate_active:
            return
            
        # 如果不在受伤状态
        if not self.health_component.is_hurt():
            # 根据移动状态切换动画
            if self.movement.is_moving():
                # 行走时在4个run动画之间轮播
                current_time = pygame.time.get_ticks() / 1000.0
                run_cycle = int(current_time * 10) % 4  # 每0.1秒切换一次
                
                if run_cycle == 0:
                    self.animation.set_animation('run')
                elif run_cycle == 1:
                    self.animation.set_animation('run2')
                elif run_cycle == 2:
                    self.animation.set_animation('run3')
                else:
                    self.animation.set_animation('run4')
            else:
                self.animation.set_animation('idle')
                
    def take_damage(self, amount):
        """受到伤害"""
        return self.health_component.take_damage(amount)
        
    def heal(self, amount):
        """治疗生命值"""
        return self.health_component.heal(amount)
        
    def apply_weapon_upgrade(self, weapon_type, level, effects):
        """应用武器升级"""
        return self.weapon_manager.apply_weapon_upgrade(weapon_type, level, effects)
            
    def apply_passive_upgrade(self, passive_type, level, effects):
        """应用被动升级"""
        return self.passive_manager.apply_passive_upgrade(passive_type, level, effects)
        
    def get_weapon_level(self, weapon_type):
        """获取指定武器的等级"""
        return self.weapon_manager.get_weapon_level(weapon_type)
        
    def get_passive_level(self, passive_type):
        """获取指定被动的等级"""
        return self.passive_manager.get_passive_level(passive_type)
        
    def add_weapon(self, weapon_type):
        """添加武器"""
        return self.weapon_manager.add_weapon(weapon_type)
        
    def update_weapons(self, dt):
        """更新所有武器状态"""
        self.weapon_manager.update(dt)
        
    def render_weapons(self, screen, camera_x, camera_y, attack_direction_x=None, attack_direction_y=None):
        """渲染所有武器"""
        self.weapon_manager.render(screen, camera_x, camera_y, attack_direction_x, attack_direction_y)
        
    def render_melee_attacks(self, screen, camera_x, camera_y):
        """渲染所有武器的近战攻击动画"""
        self.weapon_manager.render_melee_attacks(screen, camera_x, camera_y)
        
    def remove_weapon(self, weapon_type):
        """移除指定类型的武器"""
        self.weapon_manager.remove_weapon(weapon_type)
        
    def add_experience(self, amount):
        """添加经验值"""
        return self.progression.add_experience(amount)
            
    def level_up(self):
        """升级处理"""
        return self.progression.level_up()
        
    def add_coins(self, amount):
        """添加金币"""
        return self.progression.add_coins(amount)
    
    def activate_ultimate(self):
        """激活大招"""
        if self.ultimate_active or self.ultimate_cooldown_timer > 0:
            return
            
        self.ultimate_active = True
        self.ultimate_timer = 0
        self.ultimate_hit_enemies.clear()
        
        # 记录开始位置
        self.ultimate_start_x = self.world_x
        self.ultimate_start_y = self.world_y
        
        # 获取鼠标方向
        if self.game and hasattr(self.game, 'screen'):
            mouse_x, mouse_y = pygame.mouse.get_pos()
            screen_center_x = self.game.screen.get_width() // 2
            screen_center_y = self.game.screen.get_height() // 2
            
            # 计算方向向量
            dx = mouse_x - screen_center_x
            dy = mouse_y - screen_center_y
            
            # 标准化方向向量
            length = (dx ** 2 + dy ** 2) ** 0.5
            if length > 0:
                self.ultimate_direction_x = dx / length
                self.ultimate_direction_y = dy / length
            else:
                # 如果没有鼠标输入，使用玩家朝向
                self.ultimate_direction_x = 1 if self.movement.facing_right else -1
                self.ultimate_direction_y = 0
        
        # 设置大招动画
        self.animation.set_animation('ultimate')
    
    def update_ultimate(self, dt):
        """更新大招状态"""
        if not self.ultimate_active:
            return
            
        self.ultimate_timer += dt
        
        # 计算移动距离
        progress = self.ultimate_timer / self.ultimate_duration
        current_distance = progress * self.ultimate_distance
        
        # 更新位置
        self.world_x = self.ultimate_start_x + self.ultimate_direction_x * current_distance
        self.world_y = self.ultimate_start_y + self.ultimate_direction_y * current_distance
        
        # 检查敌人碰撞
        if self.game and hasattr(self.game, 'enemy_manager'):
            for enemy in self.game.enemy_manager.enemies:
                if enemy.alive():
                    # 检查是否已经对这个敌人造成过伤害
                    if enemy not in self.ultimate_hit_enemies:
                        # 计算距离
                        dx = enemy.rect.centerx - self.world_x
                        dy = enemy.rect.centery - self.world_y
                        distance = (dx ** 2 + dy ** 2) ** 0.5
                        
                        # 如果敌人在大招范围内，造成伤害
                        if distance < 100:  # 大招范围
                            enemy.take_damage(self.ultimate_damage)
                            self.ultimate_hit_enemies.add(enemy)
        
        # 检查大招是否结束
        if self.ultimate_timer >= self.ultimate_duration:
            self.ultimate_active = False
            self.ultimate_cooldown_timer = self.ultimate_cooldown  # 开始CD
            # 恢复正常动画
            self._update_animation_state()
    
    def render_ultimate(self, screen):
        """渲染大招效果"""
        if self.ultimate_active:
            # 可以在这里添加大招特效
            pass
    
    def _load_ultimate_icon(self):
        """加载大招图标"""
        try:
            from .resource_manager import resource_manager
            # 加载大招的最后一帧作为图标
            self.ultimate_icon = resource_manager.load_image(
                "ultimate_icon", 
                "images/roles/role2/attack_frames/frame_04.png"
            )
            # 缩放图标到合适大小
            if self.ultimate_icon and self.ultimate_icon.get_size() != (1, 1):
                self.ultimate_icon = pygame.transform.scale(self.ultimate_icon, (48, 48))
            else:
                print("大招图标加载失败，使用默认图标")
                self.ultimate_icon = None
        except Exception as e:
            print(f"无法加载大招图标: {e}")
            self.ultimate_icon = None
    
    def render_ultimate_cooldown(self, screen):
        """渲染大招CD显示"""
        if self.hero_type != "role2":
            return
            
        # 计算CD显示位置（左侧中央）
        icon_size = 48
        margin = 20
        x = margin
        y = screen.get_height() // 2 - icon_size // 2
        
        # 如果没有图标，创建一个默认的红色圆形图标
        if not self.ultimate_icon:
            self.ultimate_icon = pygame.Surface((icon_size, icon_size), pygame.SRCALPHA)
            pygame.draw.circle(self.ultimate_icon, (255, 0, 0), (icon_size // 2, icon_size // 2), icon_size // 2)
        
        # 渲染图标
        screen.blit(self.ultimate_icon, (x, y))
        
        # 如果CD中，渲染半透明遮罩和CD时间
        if self.ultimate_cooldown_timer > 0:
            # 创建半透明遮罩
            overlay = pygame.Surface((icon_size, icon_size), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 128))  # 半透明黑色
            screen.blit(overlay, (x, y))
            
            # 渲染CD时间
            font = pygame.font.Font(None, 24)
            cd_text = f"{self.ultimate_cooldown_timer:.1f}"
            text_surface = font.render(cd_text, True, (255, 255, 255))
            text_rect = text_surface.get_rect(center=(x + icon_size // 2, y + icon_size // 2))
            screen.blit(text_surface, text_rect)
    
    def activate_phase_through_walls(self):
        """激活穿墙技能"""
        if self.phase_through_walls or self.phase_cooldown_timer > 0:
            return
            
        self.phase_through_walls = True
        self.phase_timer = 0
        print("激活穿墙技能！")
        
        # 加载穿墙时的特殊动画
        self._load_phase_animation()
    
    def update_phase_through_walls(self, dt):
        """更新穿墙技能状态"""
        if not self.phase_through_walls:
            return
            
        self.phase_timer += dt
        
        # 检查穿墙技能是否结束
        if self.phase_timer >= self.phase_duration:
            self.phase_through_walls = False
            self.phase_cooldown_timer = self.phase_cooldown  # 开始CD
            print("穿墙技能结束")
    
    def _load_phase_icon(self):
        """加载穿墙技能图标"""
        # 用户要求不改变图标，因此不加载特定图片，让render方法使用默认圆形图标
        self.phase_icon = None
    
    def render_phase_cooldown(self, screen):
        """渲染穿墙技能CD显示"""
        if self.hero_type != "ninja_frog":
            return
            
        # 计算CD显示位置（右侧中央）
        icon_size = 48
        margin = 20
        x = screen.get_width() - margin - icon_size
        y = screen.get_height() // 2 - icon_size // 2
        
        # 如果没有图标，创建一个默认的蓝色圆形图标
        if not self.phase_icon:
            self.phase_icon = pygame.Surface((icon_size, icon_size), pygame.SRCALPHA)
            pygame.draw.circle(self.phase_icon, (0, 255, 255), (icon_size // 2, icon_size // 2), icon_size // 2)
        
        # 创建带黄色边框的图标
        bordered_icon = pygame.Surface((icon_size + 4, icon_size + 4), pygame.SRCALPHA)
        # 绘制黄色边框
        pygame.draw.rect(bordered_icon, (255, 255, 0), (0, 0, icon_size + 4, icon_size + 4), 2)
        # 绘制图标
        bordered_icon.blit(self.phase_icon, (2, 2))
        
        # 渲染图标
        screen.blit(bordered_icon, (x - 2, y - 2))
        
        # 如果CD中，渲染半透明遮罩和CD时间
        if self.phase_cooldown_timer > 0:
            # 创建半透明遮罩
            overlay = pygame.Surface((icon_size, icon_size), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 128))  # 半透明黑色
            screen.blit(overlay, (x, y))
            
            # 渲染CD时间
            font = pygame.font.Font(None, 24)
            cd_text = f"{self.phase_cooldown_timer:.1f}"
            text_surface = font.render(cd_text, True, (255, 255, 255))
            text_rect = text_surface.get_rect(center=(x + icon_size // 2, y + icon_size // 2))
            screen.blit(text_surface, text_rect)
    
    def _load_phase_animation(self):
        """加载穿墙时的特殊动画"""
        try:
            from .resource_manager import resource_manager
            # 加载穿墙时的特殊动画图片
            phase_image = resource_manager.load_image(
                "phase_animation", 
                "images/roles/finder/img_v3_02om_fdf9a462-f814-427b-9cb2-8d43bdad2c6g.png"
            )
            # 缩放图片到合适大小
            if phase_image and phase_image.get_size() != (1, 1):
                self.phase_animation_image = pygame.transform.scale(phase_image, (64, 64))
            else:
                print("穿墙动画图片加载失败")
                self.phase_animation_image = None
        except Exception as e:
            print(f"无法加载穿墙动画图片: {e}")
            self.phase_animation_image = None
    
    def toggle_weapon_mode(self):
        """切换武器模式（仅对神秘剑士）"""
        print(f"调试 - toggle_weapon_mode被调用，hero_type={self.hero_type}")
        if self.hero_type != "role2":
            print("调试 - 不是神秘剑士，退出")
            return
            
        self.is_ranged_mode = not self.is_ranged_mode
        print(f"调试 - 武器模式切换为: {'远程' if self.is_ranged_mode else '近战'}")
        
        if self.is_ranged_mode:
            print("切换到远程模式")
        else:
            print("切换到近战模式") 
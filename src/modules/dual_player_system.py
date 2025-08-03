import pygame
import math
from .player import Player
from .lighting_manager import LightingManager

class DualPlayerSystem:
    """双角色系统，管理两个玩家的独立控制和距离限制"""
    
    def __init__(self, screen, game):
        self.screen = screen
        self.game = game
        self.screen_width = screen.get_width()
        self.screen_height = screen.get_height()
        
        # 创建两个角色
        self.ninja_frog = None  # 忍者蛙 - 只能发光
        self.mystic_swordsman = None  # 神秘剑士 - 只能攻击
        
        # 距离限制（屏幕对角线长度）
        self.max_distance = math.sqrt(self.screen_width**2 + self.screen_height**2)
        
        # 强制拉回机制
        self.force_pull_distance = 1200  # 强制拉回距离阈值
        self.force_pull_duration = 0.5  # 拉回持续时间
        self.force_pull_timer = 0  # 拉回计时器
        self.is_force_pulling = False  # 是否正在强制拉回
        self.ninja_frog_start_pos = None  # 忍者蛙拉回起始位置
        self.ninja_frog_target_pos = None  # 忍者蛙拉回目标位置
        
        # 神秘剑士的攻击方向（用于武器渲染）
        self.mystic_attack_direction = (0, 0)
        
        # 神秘剑士的临时光圈效果
        self.mystic_flashlight_active = False
        self.mystic_flashlight_timer = 0
        self.mystic_flashlight_duration = 0.5  # 光圈持续时间（秒）
        
        # 光照类型管理
        self.light_mode = 1  # 当前光照类型：1-默认，2-战斗，3-探索，4-低能耗
        self.light_modes = {
            1: {"name": "default", "radius": 640, "angle": 30, "circle_radius": 80, "energy_drain": -4},
            2: {"name": "battle", "radius": 640, "angle": 60, "circle_radius": 165, "energy_drain": -10}, 
            3: {"name": "explore", "radius": 1000, "angle": 30, "circle_radius": 85, "energy_drain": -10},
            4: {"name": "low_energy", "radius": 80, "angle": 30, "circle_radius": 80, "energy_drain": 4}
        }
        
        # 电量系统
        self.energy = 100  # 当前电量 (0-100)
        self.energy_timer = 0  # 电量计时器
        self.energy_update_interval = 1.0  # 电量更新间隔（秒）
        
        # 传送道具系统
        self.teleport_item = None  # 当前传送道具实例
        self.is_teleporting = False  # 是否正在传送
        
        # 初始化角色
        self._init_players()
        
        # 光照管理器（由忍者蛙控制）
        self.lighting_manager = None
        self._init_lighting_system()
        
    def _init_players(self):
        """初始化两个角色"""
        # 忍者蛙 - 只能发光，不能攻击
        self.ninja_frog = Player(
            x=self.screen_width // 2 - 100,  # 稍微偏左
            y=self.screen_height // 2,
            hero_type="ninja_frog"
        )
        self.ninja_frog.game = self.game
        
        # 神秘剑士 - 只能攻击，不能发光
        self.mystic_swordsman = Player(
            x=self.screen_width // 2 + 100,  # 稍微偏右
            y=self.screen_height // 2,
            hero_type="role2"
        )
        self.mystic_swordsman.game = self.game
        
        # 禁用忍者蛙的攻击能力
        self.ninja_frog.weapon_manager.disable_all_weapons()
        
        # 确保神秘剑士有武器
        if len(self.mystic_swordsman.weapons) == 0:
            # 添加默认武器
            self.mystic_swordsman.add_weapon("bullet")
            self.mystic_swordsman.add_weapon("knife")
        
        # 禁用神秘剑士的光照能力（通过不调用光照相关方法）
        
    def _init_lighting_system(self):
        """初始化光照系统"""
        self.lighting_manager = LightingManager(
            self.screen_width, 
            self.screen_height, 
            preset_name="default"
        )
        
    def handle_event(self, event):
        """处理输入事件"""
        if event.type == pygame.KEYDOWN:
            if event.key in [pygame.K_w, pygame.K_a, pygame.K_s, pygame.K_d]:
                # 忍者蛙的移动控制
                self.ninja_frog.handle_event(event)
            elif event.key == pygame.K_SPACE:
                # 忍者蛙的穿墙技能
                if self.ninja_frog.hero_type == "ninja_frog" and not self.ninja_frog.phase_through_walls and self.ninja_frog.phase_cooldown_timer <= 0:
                    self.ninja_frog.activate_phase_through_walls()
            elif event.key in [pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT]:
                # 神秘剑士的移动控制（方向键）
                self._handle_mystic_movement(event)
            elif event.key in [pygame.K_KP2, pygame.K_KP4, pygame.K_KP6, pygame.K_KP8]:
                # 神秘剑士的攻击控制（数字键盘）
                self._handle_mystic_attack(event)
            elif event.key == pygame.K_u:  # U键远程攻击
                # 神秘剑士的远程攻击
                self.mystic_swordsman.weapon_manager.manual_attack(self.screen)
                # 激活神秘剑士的临时光圈
                self.mystic_flashlight_active = True
                self.mystic_flashlight_timer = self.mystic_flashlight_duration
            elif event.key == pygame.K_k:  # K键近战攻击
                # 神秘剑士的近战攻击
                self.mystic_swordsman.weapon_manager.melee_attack(self.screen)
                # 激活神秘剑士的临时光圈
                self.mystic_flashlight_active = True
                self.mystic_flashlight_timer = self.mystic_flashlight_duration
            elif event.key == pygame.K_KP5:  # 小键盘5键大招
                # 神秘剑士的大招
                print("调试 - 检测到大招按键")
                if self.mystic_swordsman.hero_type == "role2" and not self.mystic_swordsman.ultimate_active:
                    print("调试 - 激活大招")
                    self.mystic_swordsman.activate_ultimate()
                else:
                    print(f"调试 - 大招条件不满足: hero_type={self.mystic_swordsman.hero_type}, ultimate_active={self.mystic_swordsman.ultimate_active}")
            elif event.key == pygame.K_KP0:  # 小键盘0键使用传送道具
                # 使用传送道具
                self.use_teleport_item()
                
        elif event.type == pygame.KEYUP:
            if event.key in [pygame.K_w, pygame.K_a, pygame.K_s, pygame.K_d]:
                # 忍者蛙的移动控制
                self.ninja_frog.handle_event(event)
            elif event.key in [pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT]:
                # 神秘剑士的移动控制（方向键）
                self._handle_mystic_movement(event)
                
        # 鼠标事件（忍者蛙的光源控制）
        elif event.type == pygame.MOUSEMOTION:
            # 忍者蛙的光源方向跟随鼠标
            pass  # 在update中处理
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # 鼠标左键
                # 切换光照类型
                self.switch_light_mode()
                
    def _handle_mystic_movement(self, event):
        """处理神秘剑士的移动控制"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.mystic_swordsman.movement.moving['up'] = True
            elif event.key == pygame.K_DOWN:
                self.mystic_swordsman.movement.moving['down'] = True
            elif event.key == pygame.K_LEFT:
                self.mystic_swordsman.movement.moving['left'] = True
            elif event.key == pygame.K_RIGHT:
                self.mystic_swordsman.movement.moving['right'] = True
        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_UP:
                self.mystic_swordsman.movement.moving['up'] = False
            elif event.key == pygame.K_DOWN:
                self.mystic_swordsman.movement.moving['down'] = False
            elif event.key == pygame.K_LEFT:
                self.mystic_swordsman.movement.moving['left'] = False
            elif event.key == pygame.K_RIGHT:
                self.mystic_swordsman.movement.moving['right'] = False
                
        # 更新移动方向
        self.mystic_swordsman.movement._update_movement_direction()
            
    def _handle_mystic_attack(self, event):
        """处理神秘剑士的攻击"""
        if event.type == pygame.KEYDOWN:
            # 获取神秘剑士的位置
            swordsman_x = self.mystic_swordsman.world_x
            swordsman_y = self.mystic_swordsman.world_y
            
            # 根据按键确定攻击方向
            attack_direction = None
            if event.key == pygame.K_KP8:  # 上
                attack_direction = (0, -1)
                print("神秘剑士向上攻击")
            elif event.key == pygame.K_KP2:  # 下
                attack_direction = (0, 1)
                print("神秘剑士向下攻击")
            elif event.key == pygame.K_KP4:  # 左
                attack_direction = (-1, 0)
                print("神秘剑士向左攻击")
                # 更新角色朝向为朝左
                self.mystic_swordsman.movement.facing_right = False
            elif event.key == pygame.K_KP6:  # 右
                attack_direction = (1, 0)
                print("神秘剑士向右攻击")
                # 更新角色朝向为朝右
                self.mystic_swordsman.movement.facing_right = True
                
            if attack_direction:
                # 优先使用远程武器（bullet），如果没有弹药则使用近战武器（knife）
                bullet_weapon = None
                knife_weapon = None
                
                # 找到武器
                for weapon in self.mystic_swordsman.weapons:
                    if weapon.type == 'bullet':
                        bullet_weapon = weapon
                    elif weapon.type == 'knife':
                        knife_weapon = weapon
                
                # 保存攻击方向用于武器渲染
                self.mystic_attack_direction = attack_direction
                
                # 优先使用子弹攻击
                if bullet_weapon and hasattr(bullet_weapon, '_perform_attack'):
                    if bullet_weapon.ammo > 0:
                        print(f"执行子弹攻击，方向: {attack_direction}")
                        # 重置攻击计时器以允许立即攻击
                        bullet_weapon.attack_timer = bullet_weapon.attack_interval
                        bullet_weapon._perform_attack(attack_direction[0], attack_direction[1])
                        
                        # 激活神秘剑士的临时光圈
                        self.mystic_flashlight_active = True
                        self.mystic_flashlight_timer = self.mystic_flashlight_duration
                        
                        return  # 只执行一次攻击
                
                # 如果没有子弹或无法攻击，使用近战攻击
                if knife_weapon and hasattr(knife_weapon, '_perform_melee_attack'):
                    print(f"执行近战攻击，方向: {attack_direction}")
                    # 重置攻击计时器以允许立即攻击
                    knife_weapon.attack_timer = knife_weapon.attack_interval
                    knife_weapon._perform_melee_attack(attack_direction[0], attack_direction[1])
                    
                    # 激活神秘剑士的临时光圈（近战攻击也触发）
                    self.mystic_flashlight_active = True
                    self.mystic_flashlight_timer = self.mystic_flashlight_duration
                    
                    return  # 只执行一次攻击
                
    def update(self, dt):
        """更新双角色系统"""
        # 更新神秘剑士（始终更新）
        self.mystic_swordsman.update(dt)
        
        # 在强制拉回时，忍者蛙的位置由强制拉回逻辑控制
        if not self.is_force_pulling:
            self.ninja_frog.update(dt)
        
        # 应用距离限制
        self._apply_distance_constraint()
        
        # 更新光照系统（基于忍者蛙的位置和鼠标方向）
        self._update_lighting()
        
        # 更新神秘剑士的临时光圈计时器
        if self.mystic_flashlight_active:
            self.mystic_flashlight_timer -= dt
            if self.mystic_flashlight_timer <= 0:
                self.mystic_flashlight_active = False
                
        # 更新电量系统
        self._update_energy(dt)
        
        # 调试：每秒打印一次电量状态
        if hasattr(self, '_debug_timer'):
            self._debug_timer += dt
        else:
            self._debug_timer = 0
            
        if self._debug_timer >= 1.0:
            self._debug_timer = 0
            print(f"当前电量: {self.energy:.1f}%, 模式: {self.light_modes[self.light_mode]['name']}, 消耗: {self.light_modes[self.light_mode]['energy_drain']}")
            
        # 更新传送道具
        if self.teleport_item and self.is_teleporting:
            self.teleport_item.update_teleport(dt, self)
            if not self.teleport_item.is_teleport_active():
                self.is_teleporting = False
                self.teleport_item = None
                
    def switch_light_mode(self):
        """切换光照类型"""
        self.light_mode = (self.light_mode % 4) + 1
        current_mode = self.light_modes[self.light_mode]
        
        # 应用光照模式
        self._apply_light_mode()
        
        print(f"切换到{current_mode['name']}：视野{current_mode['radius']}像素，角度{current_mode['angle']}度，光圈{current_mode['circle_radius']}像素")
        
    def use_teleport_item(self):
        """使用传送道具"""
        if not hasattr(self.ninja_frog, 'teleport_items') or self.ninja_frog.teleport_items <= 0:
            
            return
            
        if self.is_teleporting:
           
            return
            
        # 创建传送道具实例并开始传送
        from .items.teleport_item import TeleportItem
        self.teleport_item = TeleportItem(0, 0)  # 位置不重要，因为我们直接使用传送功能
        
        if self.teleport_item.use_teleport(self):
            self.is_teleporting = True
           
        else:
            
            self.teleport_item = None
        
    def _update_energy(self, dt):
        """更新电量系统"""
        self.energy_timer += dt
        
        # 每秒更新一次电量
        if self.energy_timer >= self.energy_update_interval:
            self.energy_timer = 0
            
            current_mode = self.light_modes[self.light_mode]
            energy_change = current_mode["energy_drain"]
            
            # 更新电量
            old_energy = self.energy
            self.energy += energy_change
            
            # 限制电量范围
            if self.energy > 100:
                self.energy = 100
            elif self.energy < 0:
                self.energy = 0
                # 电量耗尽，强制切换到低能耗模式
                if self.light_mode != 4:
                    print("电量耗尽！强制切换到低能耗模式")
                    self.light_mode = 4
                    self._apply_light_mode()
                    
            # 调试信息
            print(f"电量更新: {old_energy:.1f}% -> {self.energy:.1f}% (变化: {energy_change}, 模式: {self.light_modes[self.light_mode]['name']})")
                    
    def _apply_light_mode(self):
        """应用当前光照模式"""
        current_mode = self.light_modes[self.light_mode]
        
        # 更新光照管理器的配置
        if self.lighting_manager:
            # 更新视野系统配置
            self.lighting_manager.vision_system.set_radius(current_mode["radius"])
            self.lighting_manager.vision_system.set_angle(current_mode["angle"])
            self.lighting_manager.vision_system.set_circle_radius(current_mode["circle_radius"])
            
            # 更新颜色透明度
            new_color = list(self.lighting_manager.vision_system.color)
            # 设置透明度
            self.lighting_manager.vision_system.set_color(tuple(new_color))
        
    def _apply_distance_constraint(self):
        """应用距离限制，确保两个角色不会离得太远"""
        # 计算两个角色之间的距离
        dx = self.mystic_swordsman.world_x - self.ninja_frog.world_x
        dy = self.mystic_swordsman.world_y - self.ninja_frog.world_y
        distance = math.sqrt(dx**2 + dy**2)
        
        # 检查是否需要强制拉回
        if distance > self.force_pull_distance and not self.is_force_pulling:
            # 开始强制拉回
            self.is_force_pulling = True
            self.force_pull_timer = 0
            self.ninja_frog_start_pos = (self.ninja_frog.world_x, self.ninja_frog.world_y)
            # 目标位置：神秘剑士身边（距离神秘剑士100像素）
            target_distance = 100
            if distance > 0:
                self.ninja_frog_target_pos = (
                    self.mystic_swordsman.world_x - (dx / distance) * target_distance,
                    self.mystic_swordsman.world_y - (dy / distance) * target_distance
                )
            else:
                self.ninja_frog_target_pos = (self.mystic_swordsman.world_x, self.mystic_swordsman.world_y)
            print(f"强制拉回启动！距离: {distance:.1f}像素")
        
        # 如果正在强制拉回
        if self.is_force_pulling:
            self.force_pull_timer += self.game.dt if hasattr(self.game, 'dt') else 0.016
            progress = min(self.force_pull_timer / self.force_pull_duration, 1.0)
            
            # 使用缓动函数使拉回更平滑
            ease_progress = 1 - (1 - progress) ** 3  # 缓出效果
            
            if self.ninja_frog_start_pos and self.ninja_frog_target_pos:
                # 插值计算忍者蛙的新位置
                start_x, start_y = self.ninja_frog_start_pos
                target_x, target_y = self.ninja_frog_target_pos
                
                self.ninja_frog.world_x = start_x + (target_x - start_x) * ease_progress
                self.ninja_frog.world_y = start_y + (target_y - start_y) * ease_progress
            
            # 拉回完成
            if progress >= 1.0:
                self.is_force_pulling = False
                self.force_pull_timer = 0
                self.ninja_frog_start_pos = None
                self.ninja_frog_target_pos = None
                print("强制拉回完成！")
                return  # 跳过普通距离约束
        
        # 普通距离约束（仅在非强制拉回时）
        if distance > self.max_distance and not self.is_force_pulling:
            # 计算需要调整的比例
            scale = self.max_distance / distance
            
            # 计算两个角色的中点
            center_x = (self.ninja_frog.world_x + self.mystic_swordsman.world_x) / 2
            center_y = (self.ninja_frog.world_y + self.mystic_swordsman.world_y) / 2
            
            # 重新计算两个角色的位置
            half_distance = self.max_distance / 2
            
            # 忍者蛙位置
            self.ninja_frog.world_x = center_x - (dx * scale) / 2
            self.ninja_frog.world_y = center_y - (dy * scale) / 2
            
            # 神秘剑士位置
            self.mystic_swordsman.world_x = center_x + (dx * scale) / 2
            self.mystic_swordsman.world_y = center_y + (dy * scale) / 2
            
    def _update_lighting(self):
        """更新光照系统"""
        if self.lighting_manager:
            # 更新光照管理器的墙壁数据
            if self.game.map_manager:
                walls = self.game.map_manager.get_collision_tiles()
                tile_width, tile_height = self.game.map_manager.get_tile_size()
                self.lighting_manager.set_walls(walls, tile_width)
            
    def render(self, screen, camera_x, camera_y):
        """渲染双角色系统"""
        # 计算屏幕坐标
        ninja_screen_x = self.ninja_frog.world_x - camera_x + screen.get_width() // 2
        ninja_screen_y = self.ninja_frog.world_y - camera_y + screen.get_height() // 2
        mystic_screen_x = self.mystic_swordsman.world_x - camera_x + screen.get_width() // 2
        mystic_screen_y = self.mystic_swordsman.world_y - camera_y + screen.get_height() // 2
        
        # 更新角色的屏幕位置
        self.ninja_frog.rect.center = (ninja_screen_x, ninja_screen_y)
        self.mystic_swordsman.rect.center = (mystic_screen_x, mystic_screen_y)
        
        # 渲染两个角色之间的连接线
        ninja_screen_x = self.ninja_frog.world_x - camera_x + screen.get_width() // 2
        ninja_screen_y = self.ninja_frog.world_y - camera_y + screen.get_height() // 2
        mystic_screen_x = self.mystic_swordsman.world_x - camera_x + screen.get_width() // 2
        mystic_screen_y = self.mystic_swordsman.world_y - camera_y + screen.get_height() // 2
        
        # 绘制连接线（虚线效果）
        self._draw_connection_line(screen, ninja_screen_x, ninja_screen_y, mystic_screen_x, mystic_screen_y)
        
        # 渲染两个角色
        self.ninja_frog.render(screen)
        self.mystic_swordsman.render(screen)
        
        # 渲染光照效果（基于忍者蛙的位置，方向由忍者蛙指向鼠标）
        if self.lighting_manager:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            
            # 计算忍者蛙在屏幕上的位置
            ninja_screen_x = self.ninja_frog.world_x - camera_x + screen.get_width() // 2
            ninja_screen_y = self.ninja_frog.world_y - camera_y + screen.get_height() // 2
            
            # 准备额外光源列表（神秘剑士的光源）
            additional_lights = []
            if self.mystic_flashlight_active:
                # 计算神秘剑士在屏幕上的位置
                mystic_screen_x = self.mystic_swordsman.world_x - camera_x + screen.get_width() // 2
                mystic_screen_y = self.mystic_swordsman.world_y - camera_y + screen.get_height() // 2
                
                # 计算光源强度（基于剩余时间）
                intensity = self.mystic_flashlight_timer / self.mystic_flashlight_duration
                radius = 80  # 光源半径（与忍者蛙的光圈一样大）
                
                additional_lights.append((mystic_screen_x, mystic_screen_y, intensity, radius))
            
            # 渲染光照（包括忍者蛙的主光照和神秘剑士的临时光源）
            self.lighting_manager.render(
                screen, 
                ninja_screen_x,  # 光源中心位置（忍者蛙）
                ninja_screen_y, 
                mouse_x,  # 鼠标位置
                mouse_y, 
                camera_x, 
                camera_y,
                additional_lights  # 额外光源
            )
            
    def render_weapons(self, screen, camera_x, camera_y):
        """渲染武器效果（只有神秘剑士的武器）"""
        # 只渲染神秘剑士的武器，传递攻击方向
        self.mystic_swordsman.render_weapons(screen, camera_x, camera_y, 
                                           self.mystic_attack_direction[0], 
                                           self.mystic_attack_direction[1])
        self.mystic_swordsman.render_melee_attacks(screen, camera_x, camera_y)
        
        # 渲染神秘剑士的大招
        self.mystic_swordsman.render_ultimate(screen)
        self.mystic_swordsman.render_ultimate_cooldown(screen)
        
        # 渲染忍者蛙的穿墙技能CD
        self.ninja_frog.render_phase_cooldown(screen)
        
        # 渲染神秘剑士的子弹数量显示
        self.render_ammo_display(screen)
        
        # 渲染当前光照类型显示
        self.render_light_mode_display(screen)
        
        # 渲染电量显示
        self.render_energy_display(screen)
        
        # 渲染传送道具数量显示
        self.render_teleport_display(screen)
        
    def get_players(self):
        """获取两个角色"""
        return [self.ninja_frog, self.mystic_swordsman]
        
    def get_center_position(self):
        """获取两个角色的中心位置（用于相机跟随）"""
        center_x = (self.ninja_frog.world_x + self.mystic_swordsman.world_x) / 2
        center_y = (self.ninja_frog.world_y + self.mystic_swordsman.world_y) / 2
        return center_x, center_y
        
    def check_collision_with_enemy(self, enemy):
        """检查敌人与任一角色的碰撞"""
        # 检查忍者蛙
        if self.ninja_frog.collision_rect.colliderect(enemy.rect):
            return self.ninja_frog
            
        # 检查神秘剑士
        if self.mystic_swordsman.collision_rect.colliderect(enemy.rect):
            return self.mystic_swordsman
            
        return None
        
    def add_experience_to_both(self, amount):
        """给两个角色都添加经验值"""
        self.ninja_frog.add_experience(amount)
        self.mystic_swordsman.add_experience(amount)
        
    def add_coins_to_both(self, amount):
        """给两个角色都添加金币"""
        self.ninja_frog.add_coins(amount)
        self.mystic_swordsman.add_coins(amount)
        
    def render_ammo_display(self, screen):
        """渲染神秘剑士的子弹数量显示"""
        # 获取神秘剑士的子弹武器
        bullet_weapon = None
        for weapon in self.mystic_swordsman.weapons:
            if weapon.type == 'bullet':
                bullet_weapon = weapon
                break
        
        if not bullet_weapon:
            return
        
        # 计算显示位置（左侧中央）
        icon_size = 48
        margin = 20
        x = margin
        y = screen.get_height() // 2 - icon_size // 2 + 100  # 稍微偏下，避免与技能图标重叠
        
        # 加载子弹图标
        try:
            bullet_icon = pygame.image.load("assets/images/weapons/bullet_8x8.png").convert_alpha()
            bullet_icon = pygame.transform.scale(bullet_icon, (icon_size, icon_size))
        except:
            # 如果加载失败，创建一个默认的子弹图标
            bullet_icon = pygame.Surface((icon_size, icon_size), pygame.SRCALPHA)
            pygame.draw.circle(bullet_icon, (255, 255, 0), (icon_size // 2, icon_size // 2), icon_size // 2)
        
        # 创建带红色边框的图标
        bordered_icon = pygame.Surface((icon_size + 4, icon_size + 4), pygame.SRCALPHA)
        # 绘制红色边框
        pygame.draw.rect(bordered_icon, (255, 0, 0), (0, 0, icon_size + 4, icon_size + 4), 2)
        # 绘制图标
        bordered_icon.blit(bullet_icon, (2, 2))
        
        # 渲染图标
        screen.blit(bordered_icon, (x - 2, y - 2))
        
        # 渲染子弹数量
        font = pygame.font.Font(None, 24)
        ammo_text = f"{bullet_weapon.ammo}/{bullet_weapon.max_ammo}"
        text_surface = font.render(ammo_text, True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=(x + icon_size // 2, y + icon_size + 15))
        screen.blit(text_surface, text_rect)
        
    def render_light_mode_display(self, screen):
        """渲染当前光照类型显示"""
        current_mode = self.light_modes[self.light_mode]
        
        # 显示位置（屏幕右上角）
        margin = 20
        x = screen.get_width() - 200
        y = margin
        
        # 创建背景
        bg_surface = pygame.Surface((180, 60), pygame.SRCALPHA)
        bg_surface.fill((0, 0, 0, 150))  # 半透明黑色背景
        
        # 渲染背景
        screen.blit(bg_surface, (x, y))
        
        # 渲染文本
        font = pygame.font.Font(None, 20)
        
        # 模式名称
        mode_text = f"mode:{current_mode['name']}"
        mode_surface = font.render(mode_text, True, (255, 255, 255))
        mode_rect = mode_surface.get_rect(topleft=(x + 10, y + 10))
        screen.blit(mode_surface, mode_rect)
        
        # 参数信息
        param_text = f"radius: {current_mode['radius']}px, angle: {current_mode['angle']}°"
        param_surface = font.render(param_text, True, (200, 200, 200))
        param_rect = param_surface.get_rect(topleft=(x + 10, y + 35))
        screen.blit(param_surface, param_rect)
        
    def render_energy_display(self, screen):
        """渲染电量显示"""
        # 显示位置（屏幕右侧中央）
        margin = 20
        x = screen.get_width() - 120
        y = screen.get_height() // 2 - 50
        
        # 创建背景
        bg_surface = pygame.Surface((100, 80), pygame.SRCALPHA)
        bg_surface.fill((0, 0, 0, 150))  # 半透明黑色背景
        
        # 渲染背景
        screen.blit(bg_surface, (x, y))
        
        # 渲染文本
        font = pygame.font.Font(None, 24)
        
        # 电量标题
        energy_title = "ENERGY"
        title_surface = font.render(energy_title, True, (255, 255, 255))
        title_rect = title_surface.get_rect(center=(x + 50, y + 20))
        screen.blit(title_surface, title_rect)
        
        # 电量数值
        energy_text = f"{int(self.energy)}%"
        # 根据电量设置颜色
        if self.energy > 50:
            energy_color = (0, 255, 0)  # 绿色
        elif self.energy > 20:
            energy_color = (255, 255, 0)  # 黄色
        else:
            energy_color = (255, 0, 0)  # 红色
            
        energy_surface = font.render(energy_text, True, energy_color)
        energy_rect = energy_surface.get_rect(center=(x + 50, y + 50))
        screen.blit(energy_surface, energy_rect)
        
    def render_teleport_display(self, screen):
        """渲染传送道具数量显示"""
        # 检查忍者蛙是否有传送道具
        if not hasattr(self.ninja_frog, 'teleport_items'):
            return
            
        # 显示位置（屏幕右侧，电量显示下方）
        margin = 20
        x = screen.get_width() - 120
        y = screen.get_height() // 2 + 50  # 电量显示下方
        
        # 创建背景
        bg_surface = pygame.Surface((100, 60), pygame.SRCALPHA)
        bg_surface.fill((0, 0, 0, 150))  # 半透明黑色背景
        
        # 渲染背景
        screen.blit(bg_surface, (x, y))
        
        # 渲染文本
        font = pygame.font.Font(None, 20)
        
        # 传送道具标题
        teleport_title = "TELEPORT"
        title_surface = font.render(teleport_title, True, (255, 255, 255))
        title_rect = title_surface.get_rect(center=(x + 50, y + 15))
        screen.blit(title_surface, title_rect)
        
        # 传送道具数量
        teleport_text = f"{self.ninja_frog.teleport_items}"
        teleport_color = (0, 255, 255) if self.ninja_frog.teleport_items > 0 else (128, 128, 128)
        
        teleport_surface = font.render(teleport_text, True, teleport_color)
        teleport_rect = teleport_surface.get_rect(center=(x + 50, y + 35))
        screen.blit(teleport_surface, teleport_rect)
    
    def _draw_connection_line(self, screen, x1, y1, x2, y2):
        """
        绘制两个角色之间的连接线（虚线效果）
        
        Args:
            screen: pygame屏幕表面
            x1, y1: 忍者蛙的屏幕坐标
            x2, y2: 神秘剑士的屏幕坐标
        """
        # 计算距离
        dx = x2 - x1
        dy = y2 - y1
        distance = math.sqrt(dx * dx + dy * dy)
        
        if distance == 0:
            return
            
        # 归一化方向向量
        dx /= distance
        dy /= distance
        
        # 虚线参数
        dash_length = 10  # 虚线长度
        gap_length = 5    # 间隙长度
        total_segment = dash_length + gap_length
        
        # 计算需要多少个虚线段
        num_segments = int(distance / total_segment)
        
        # 绘制虚线
        for i in range(num_segments):
            # 计算当前段的起始和结束位置
            start_x = x1 + dx * (i * total_segment)
            start_y = y1 + dy * (i * total_segment)
            end_x = x1 + dx * (i * total_segment + dash_length)
            end_y = y1 + dy * (i * total_segment + dash_length)
            
            # 绘制虚线段
            pygame.draw.line(screen, (255, 255, 0), (start_x, start_y), (end_x, end_y), 2)
        
        # 绘制最后一个虚线段（如果距离不够一个完整的段）
        remaining_distance = distance - (num_segments * total_segment)
        if remaining_distance > 0:
            start_x = x1 + dx * (num_segments * total_segment)
            start_y = y1 + dy * (num_segments * total_segment)
            end_x = x2
            end_y = y2
            pygame.draw.line(screen, (255, 255, 0), (start_x, start_y), (end_x, end_y), 2)
             
 
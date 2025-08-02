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
        
        # 神秘剑士的攻击方向（用于武器渲染）
        self.mystic_attack_direction = (0, 0)
        
        # 神秘剑士的临时光圈效果
        self.mystic_flashlight_active = False
        self.mystic_flashlight_timer = 0
        self.mystic_flashlight_duration = 0.5  # 光圈持续时间（秒）
        
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
        # 忍者蛙控制：WASD移动，鼠标控制光源方向
        if event.type == pygame.KEYDOWN:
            if event.key in [pygame.K_w, pygame.K_a, pygame.K_s, pygame.K_d]:
                # 忍者蛙的移动控制
                self.ninja_frog.handle_event(event)
            elif event.key in [pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT]:
                # 神秘剑士的移动控制（方向键）
                self._handle_mystic_movement(event)
            elif event.key in [pygame.K_KP2, pygame.K_KP4, pygame.K_KP6, pygame.K_KP8]:
                # 神秘剑士的攻击控制（数字键盘）
                self._handle_mystic_attack(event)
                
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
            
        # 处理鼠标点击事件（神秘剑士的攻击）
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # 左键
                # 神秘剑士的远程攻击
                self.mystic_swordsman.weapon_manager.manual_attack(self.screen)
                # 激活神秘剑士的临时光圈
                self.mystic_flashlight_active = True
                self.mystic_flashlight_timer = self.mystic_flashlight_duration
            elif event.button == 3:  # 右键
                # 神秘剑士的近战攻击
                self.mystic_swordsman.weapon_manager.melee_attack(self.screen)
                # 激活神秘剑士的临时光圈
                self.mystic_flashlight_active = True
                self.mystic_flashlight_timer = self.mystic_flashlight_duration
                
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
            elif event.key == pygame.K_KP6:  # 右
                attack_direction = (1, 0)
                print("神秘剑士向右攻击")
                
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
        # 更新两个角色
        self.ninja_frog.update(dt)
        self.mystic_swordsman.update(dt)
        
        # 应用距离限制
        self._apply_distance_constraint()
        
        # 更新光照系统（基于忍者蛙的位置和鼠标方向）
        self._update_lighting()
        
        # 更新神秘剑士的临时光圈计时器
        if self.mystic_flashlight_active:
            self.mystic_flashlight_timer -= dt
            if self.mystic_flashlight_timer <= 0:
                self.mystic_flashlight_active = False
        
    def _apply_distance_constraint(self):
        """应用距离限制，确保两个角色不会离得太远"""
        # 计算两个角色之间的距离
        dx = self.mystic_swordsman.world_x - self.ninja_frog.world_x
        dy = self.mystic_swordsman.world_y - self.ninja_frog.world_y
        distance = math.sqrt(dx**2 + dy**2)
        
        # 如果距离超过限制，调整位置
        if distance > self.max_distance:
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
             
 
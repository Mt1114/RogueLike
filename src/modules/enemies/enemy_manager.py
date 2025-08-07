import pygame
import random
import math
from .types import Ghost, Radish, Bat, Slime, Soul
from .spawn_marker import SpawnMarker
import time

class EnemyManager:
    def __init__(self):
        self.enemies = []
        self.spawn_timer = 0
        self.spawn_interval = 1.5  # 每1.5秒生成一个敌人（加快生成速度）
        self.difficulty = "normal"  # 默认难度为normal
        self.difficulty_level = 1   # 难度等级，随游戏时间增长
        self.game_time = 0  # 游戏进行时间
        
        # 关卡强度系统
        self.global_level = 1  # 全局关卡
        self.level_strength_multiplier = 1.0  # 关卡强度倍数
        self.bat_spawn_timer = 0  # 蝙蝠生成计时器
        
        # 波次系统
        self.current_round = 0  # 当前波次
        self.round_start_time = 0  # 当前波次开始时间
        self.round_messages = []  # 波次提示消息
        self.message_timer = 0  # 消息显示计时器
        
        # 出生点标记
        self.spawn_markers = []
        
        # 地图边界相关
        self.map_boundaries = None  # (min_x, min_y, max_x, max_y)
        
        # 敌人子弹列表
        self.enemy_projectiles = []
        
        # 波次UI回调函数
        self.on_round_start = None
        
        # 跟踪是否已经生成过soul敌人
        self.soul_spawned = False
        
    def set_map_boundaries(self, min_x, min_y, max_x, max_y):
        """设置地图边界
        
        Args:
            min_x: 最小X坐标
            min_y: 最小Y坐标
            max_x: 最大X坐标
            max_y: 最大Y坐标
        """
        self.map_boundaries = (min_x, min_y, max_x, max_y)
        
    def spawn_enemy(self, enemy_type, x, y, health=None):
        """在指定位置生成指定类型和生命值的敌人
        
        Args:
            enemy_type: 敌人类型 ('ghost', 'radish', 'bat', 'slime')
            x: 世界坐标系中的x坐标
            y: 世界坐标系中的y坐标
            health: 指定生命值，如果为None则使用该类型的默认生命值
            
        Returns:
            Enemy: 生成的敌人实例
        """
        # 根据类型创建对应的敌人实例
        enemy = None
        
        # 使用新的构造函数，传递敌人类型、难度和等级
        if enemy_type == 'ghost':
            enemy = Ghost(x, y, enemy_type, self.difficulty, self.difficulty_level)
        elif enemy_type == 'radish':
            enemy = Radish(x, y, enemy_type, self.difficulty, self.difficulty_level)
        elif enemy_type == 'bat':
            enemy = Bat(x, y, enemy_type, self.difficulty, self.difficulty_level)
        elif enemy_type == 'slime':
            enemy = Slime(x, y, enemy_type, self.difficulty, self.difficulty_level)
        elif enemy_type == 'soul':
            enemy = Soul(x, y, enemy_type, self.difficulty, self.difficulty_level)
            # 标记已经生成过soul敌人
            self.soul_spawned = True
            # 添加soul出现的警告消息
            self.round_messages.append({
                'text': "要当心！！！",
                'timer': 0,
                'duration': 3.0,
                'color': (255, 0, 0)  # 红色
            })
            
        # 应用波次属性加成
        if enemy and hasattr(self, 'health_multiplier') and hasattr(self, 'damage_multiplier'):
            # 应用生命值加成
            enemy.health = int(enemy.health * self.health_multiplier)
            enemy.max_health = int(enemy.max_health * self.health_multiplier)
            
            # 应用攻击力加成
            if hasattr(enemy, 'damage'):
                enemy.damage = int(enemy.damage * self.damage_multiplier)
        
        # 应用关卡强度倍数
        if enemy:
            # 应用关卡强度倍数到生命值
            enemy.health = int(enemy.health * self.level_strength_multiplier)
            enemy.max_health = int(enemy.max_health * self.level_strength_multiplier)
            
            # 应用关卡强度倍数到攻击力
            if hasattr(enemy, 'damage'):
                enemy.damage = int(enemy.damage * self.level_strength_multiplier)
            
        # 如果指定了生命值，覆盖配置的生命值
        if enemy and health is not None:
            enemy.health = health
            enemy.max_health = health
            
        if enemy:
            # 设置敌人的game属性，以便访问游戏对象
            if hasattr(self, 'game'):
                enemy.game = self.game
            self.enemies.append(enemy)
            
            
        return enemy
        
    def update(self, dt, player, second_player=None):
        self.game_time += dt
        self.spawn_timer += dt
        self.message_timer += dt
        
        # 更新波次系统
        self._update_round_system(dt, player)
        
        # 更新难度等级（根据游戏时间）
        old_difficulty_level = self.difficulty_level
        self.difficulty_level = max(1, int(self.game_time // 60) + 1)  # 每60秒提升一级
        
        # 如果难度等级发生变化，打印调试信息
       
        
        # 更新敌人子弹
        self._update_enemy_projectiles(dt)
        
        # 根据波次状态决定是否生成敌人
        if self.current_round > 0 and self.current_round <= 3:
            # 检查是否达到当前波次的最大敌人数
            if hasattr(self, 'max_enemies_for_round') and self.max_enemies_for_round is not None:
                if self.enemies_spawned_this_round >= self.max_enemies_for_round:
                    # 已达到最大敌人数，停止生成
                    pass  # 改为pass，不退出整个update方法
                else:
                    if self.spawn_timer >= self.spawn_interval:
                        self.spawn_timer = 0
                        if self.random_spawn_enemy(player):
                            # 成功生成敌人，增加计数
                            if hasattr(self, 'enemies_spawned_this_round'):
                                self.enemies_spawned_this_round += 1
            else:
                if self.spawn_timer >= self.spawn_interval:
                    self.spawn_timer = 0
                    if self.random_spawn_enemy(player):
                        # 成功生成敌人，增加计数
                        if hasattr(self, 'enemies_spawned_this_round'):
                            self.enemies_spawned_this_round += 1
        elif self.current_round == 0:  # 休息期，持续生成少量敌人
            # 休息期使用较慢的生成速度，并且有一定随机性
            rest_spawn_interval = 3.0 + random.uniform(0, 2.0)  # 3-5秒随机间隔
            if self.spawn_timer >= rest_spawn_interval:
                self.spawn_timer = 0
                # 休息期主要生成较弱的敌人
                enemy_types = ['ghost', 'radish']  # 休息期只生成幽灵和萝卜
                if random.random() < 0.3:  # 30%概率生成敌人
                    self.random_spawn_enemy(player, preferred_types=enemy_types)
            
        # 如果玩家等级达到1级，更新蝙蝠生成计时器
        if player.level >= 1:
            # 如果是刚达到1级,立即生成一只蝙蝠
            if self.bat_spawn_timer == 0:
                self.spawn_bat(player)
                self.bat_spawn_timer = 0.1  # 设置一个很小的值,避免重复触发初始生成
            
            self.bat_spawn_timer += dt
            if self.bat_spawn_timer >= 60:  # 每60秒生成一只蝙蝠
                self.bat_spawn_timer = 0.1  # 重置为0.1而不是0
                self.spawn_bat(player)
            
        # 更新出生点标记
        for marker in self.spawn_markers[:]:
            if not marker.update(dt):
                self.spawn_markers.remove(marker)
        
        # 更新所有敌人
        for enemy in self.enemies[:]:  # 使用切片创建副本以避免在迭代时修改列表
            enemy.update(dt, player, second_player)
            
    def _update_round_system(self, dt, player):
        """更新波次系统，根据关卡数调整怪物生成速度"""
        game_time_minutes = self.game_time / 60.0
        
        # 根据关卡数计算生成间隔倍数
        spawn_speed_multiplier = self._get_spawn_speed_multiplier()
        
        # 第一波：0:00-0:30，2.5秒生成一个
        if game_time_minutes >= 0 and game_time_minutes < 0.5 and self.current_round == 0:
            adjusted_interval = 2.5 / spawn_speed_multiplier
            self._start_round(1, f"第1波 (关卡{self.global_level})", adjusted_interval, 1.0, 1.0, 840)  # 1200 * 0.7 = 840
            
        # 第一波结束，进入休息期：0:30-1:00
        elif game_time_minutes >= 0.5 and game_time_minutes < 1.0 and self.current_round == 1:
            self._end_round()
            
        # 第二波：1:00-2:30，1.0秒生成一个
        elif game_time_minutes >= 1.0 and game_time_minutes < 2.5 and self.current_round == 0:
            adjusted_interval = 1.0 / spawn_speed_multiplier
            self._start_round(2, f"第2波 (关卡{self.global_level})", adjusted_interval, 1.2, 1.2, 840)  # 1200 * 0.7 = 840
            
        # 第二波结束，进入休息期：2:30-3:00
        elif game_time_minutes >= 2.5 and game_time_minutes < 3.0 and self.current_round == 2:
            self._end_round()
            
        # 第三波：3:00-5:00，1.0秒生成一个
        elif game_time_minutes >= 3.0 and game_time_minutes < 5.0 and self.current_round == 0:
            adjusted_interval = 1.0 / spawn_speed_multiplier
            self._start_round(3, f"第3波 (关卡{self.global_level})", adjusted_interval, 1.0, 1.1, 840)  # 1200 * 0.7 = 840
            
        # 修复2:00-2:30之间的空白期：如果第二波还在进行，继续生成敌人
        elif game_time_minutes >= 2.0 and game_time_minutes < 2.5 and self.current_round == 2:
            # 第二波继续进行，不执行任何操作
            pass
            
        # 游戏结束：5:00后
        elif game_time_minutes >= 5.0 and self.current_round != -1:
            self._end_game()
    
    def _get_spawn_speed_multiplier(self):
        """根据关卡数获取生成速度倍数
        
        Returns:
            float: 生成速度倍数
        """
        if self.global_level == 1:
            return 1.0  # 第一关：基础速度
        elif self.global_level == 2:
            return 2.0  # 第二关：2倍速度
        elif self.global_level >= 3:
            return 3.0  # 第三关及以上：3倍速度
        else:
            return 1.0  # 默认基础速度
        
    def _start_round(self, round_num, message, spawn_interval, health_multiplier, damage_multiplier, max_enemies=None):
        """开始新波次"""
        self.current_round = round_num
        self.round_start_time = self.game_time
        self.spawn_interval = spawn_interval
        self.health_multiplier = health_multiplier
        self.damage_multiplier = damage_multiplier
        self.max_enemies_for_round = max_enemies
        self.enemies_spawned_this_round = 0
        
        # 添加波次提示消息
        self.round_messages.append({
            'text': message,
            'timer': 0,
            'duration': 3.0,
            'color': (255, 255, 0)  # 黄色
        })
        
        
        
        # 触发波次UI显示
        if self.on_round_start:
            self.on_round_start(round_num)
        
    def _end_round(self):
        """结束当前波次"""
        self.current_round = 0
        
        
        # 添加休息期提示消息
        self.round_messages.append({
            'text': "休息期 - 敌人减少",
            'timer': 0,
            'duration': 2.0,
            'color': (0, 255, 255)  # 青色
        })
        
    def _end_game(self):
        """游戏结束"""
        self.current_round = -1
        self.round_messages.append({
            'text': "好像安全了吧",
            'timer': 0,
            'duration': 5.0,
            'color': (0, 255, 0)  # 绿色
        })
        
        
    def _render_round_messages(self, screen):
        """渲染波次消息"""
        # 更新消息计时器
        for message in self.round_messages[:]:
            message['timer'] += 0.016  # 假设60FPS
            
            # 移除过期的消息
            if message['timer'] >= message['duration']:
                self.round_messages.remove(message)
                continue
                
            # 渲染消息
            font = pygame.font.SysFont('simHei', 48)
            text_surface = font.render(message['text'], True, message['color'])
            
            # 计算消息位置（屏幕中央）
            text_rect = text_surface.get_rect()
            text_rect.centerx = screen.get_width() // 2
            text_rect.centery = screen.get_height() // 2
            
            # 添加透明度效果
            alpha = 255
            if message['timer'] > message['duration'] * 0.7:  # 最后30%时间开始淡出
                alpha = int(255 * (1 - (message['timer'] - message['duration'] * 0.7) / (message['duration'] * 0.3)))
            
            # 创建带透明度的表面
            if alpha < 255:
                text_surface.set_alpha(alpha)
            
            screen.blit(text_surface, text_rect)
            
            # 添加阴影效果
            shadow_surface = font.render(message['text'], True, (0, 0, 0))
            shadow_rect = shadow_surface.get_rect()
            shadow_rect.centerx = text_rect.centerx + 2
            shadow_rect.centery = text_rect.centery + 2
            if alpha < 255:
                shadow_surface.set_alpha(alpha)
            screen.blit(shadow_surface, shadow_rect)
            
    def render(self, screen, camera_x, camera_y, screen_center_x, screen_center_y, lighting_manager=None):
        # 渲染出生点标记
        for marker in self.spawn_markers[:]:  # 使用切片复制避免在迭代时修改
            marker.update(0.016)  # 假设60FPS
            if marker.timer >= marker.duration:  # 修复：检查timer而不是duration
                self.spawn_markers.remove(marker)
            else:
                marker.render(screen, camera_x, camera_y, screen_center_x, screen_center_y)
        
        # 渲染波次消息
        self._render_round_messages(screen)
        
        # 渲染敌人
        for enemy in self.enemies:
            # 计算敌人在屏幕上的位置
            screen_x = screen_center_x + (enemy.rect.x - camera_x)
            screen_y = screen_center_y + (enemy.rect.y - camera_y)
            
            # 性能优化：只渲染在屏幕范围内的敌人
            if (screen_x > -100 and screen_x < screen.get_width() + 100 and
                screen_y > -100 and screen_y < screen.get_height() + 100):
                
                # 检查敌人是否在光照范围内
                if lighting_manager and hasattr(lighting_manager, 'is_enabled') and lighting_manager.is_enabled():
                    # 性能优化：减少光照检测频率
                    # 只在敌人移动或光照系统变化时检测
                    if (not hasattr(enemy, '_last_light_check') or
                        abs(enemy.rect.centerx - getattr(enemy, '_last_light_x', 0)) > 10 or
                        abs(enemy.rect.centery - getattr(enemy, '_last_light_y', 0)) > 10):
                        
                        # 使用敌人的实际世界坐标进行光照检测
                        enemy_world_x = enemy.rect.centerx
                        enemy_world_y = enemy.rect.centery
                        enemy_screen_x = screen_center_x + (enemy_world_x - camera_x)
                        enemy_screen_y = screen_center_y + (enemy_world_y - camera_y)
                        
                        # 检查敌人是否在光照范围内
                        # 注意：光照系统使用的是屏幕坐标，所以需要转换
                        current_in_light = lighting_manager.is_in_light(enemy_screen_x, enemy_screen_y)
                        
                       
                        
                        # 临时修复：强制显示血条，直到光照系统问题解决
                        enemy.has_been_seen = True
                        enemy.render(screen, screen_x, screen_y, show_health_bar=True)
                        
                       
                        enemy._last_light_check = time.time()
                        enemy._last_light_x = enemy.rect.centerx
                        enemy._last_light_y = enemy.rect.centery
                        enemy._last_in_light = current_in_light
                    else:
                        # 临时修复：强制显示血条
                        enemy.has_been_seen = True
                        enemy.render(screen, screen_x, screen_y, show_health_bar=True)
                        
                        # 原始逻辑（暂时注释掉）
                        # if enemy._last_in_light:
                        #     # 上次在光照内，显示血条
                        #     enemy.render(screen, screen_x, screen_y, show_health_bar=True)
                        # elif enemy.has_been_seen:
                        #     # 曾经被看到过但当前不在光照内，显示怪物和血条
                        #     enemy.render(screen, screen_x, screen_y, show_health_bar=True)
                        # else:
                        #     # 如果从未被看到过且当前不在光照内，仍然渲染敌人（但可能半透明）
                        #     # 这样可以避免"看不见但能攻击"的问题
                        #     enemy.render(screen, screen_x, screen_y, show_health_bar=False)
                else:
                    # 如果没有光照系统或光照系统被禁用，正常渲染（包括血条）
                    enemy.render(screen, screen_x, screen_y, show_health_bar=True)
                
                # 显示碰撞圈（除了soul类型）
                # if enemy.type != 'soul':
                #     self._render_collision_circle(screen, enemy, screen_x, screen_y)
        
        # 渲染敌人子弹
        self._render_enemy_projectiles(screen, camera_x, camera_y, screen_center_x, screen_center_y)
            
    def remove_enemy(self, enemy):
        if enemy in self.enemies:
            self.enemies.remove(enemy)
            
    def random_spawn_enemy(self, player, preferred_types=None):
        """在多个位置随机生成敌人，根据关卡数增加出生点数量
        
        Args:
            player: 玩家对象
            preferred_types: 偏好的敌人类型列表，如果为None则使用默认逻辑
        """
        if not self.map_boundaries:
            return False  # 如果没有地图边界信息，无法生成敌人
            
        min_x, min_y, max_x, max_y = self.map_boundaries
        
        # 基础四个角落的生成区域
        corner_offset = 100
        base_corners = [
            (min_x + corner_offset, min_y + corner_offset),  # 左上角
            (max_x - corner_offset, min_y + corner_offset),  # 右上角
            (min_x + corner_offset, max_y - corner_offset),  # 左下角
            (max_x - corner_offset, max_y - corner_offset)   # 右下角
        ]
        
        # 根据关卡数增加出生点
        spawn_points = base_corners.copy()
        
        if self.global_level >= 2:
            # 第二关：增加8个随机出生点 + 1个中间出生点
            additional_points = self._generate_additional_spawn_points(8, min_x, min_y, max_x, max_y)
            middle_points = self._generate_middle_spawn_points(1, min_x, min_y, max_x, max_y)
            spawn_points.extend(additional_points)
            spawn_points.extend(middle_points)
            
        if self.global_level >= 3:
            # 第三关：再增加20个随机出生点 + 4个中间出生点
            additional_points = self._generate_additional_spawn_points(20, min_x, min_y, max_x, max_y)
            middle_points = self._generate_middle_spawn_points(4, min_x, min_y, max_x, max_y)
            spawn_points.extend(additional_points)
            spawn_points.extend(middle_points)
        
        # 随机选择一个出生点
        spawn_x, spawn_y = random.choice(spawn_points)
        
        # 在选定的位置周围添加一些随机偏移（±50像素）
        spawn_x += random.uniform(-50, 50)
        spawn_y += random.uniform(-50, 50)
        
        # 确保生成位置在地图边界内
        spawn_x = max(min_x, min(spawn_x, max_x))
        spawn_y = max(min_y, min(spawn_y, max_y))
        
        # 创建出生点标记
        spawn_marker = SpawnMarker(spawn_x, spawn_y, duration=2.0)
        self.spawn_markers.append(spawn_marker)
        
        # 根据偏好类型或游戏时间决定生成什么类型的敌人
        if preferred_types:
            enemy_type = random.choice(preferred_types)
        elif self.game_time < 10:  # 游戏开始10秒内
            enemy_type = 'slime'
        
        elif self.game_time>=120:
            # 如果还没有生成过soul敌人，可以生成soul
            available_types = ['ghost', 'radish', 'slime']
            if not self.soul_spawned:
                available_types.append('soul')
            enemy_type = random.choice(available_types)
        else:  # 10秒后可以生成幽灵和萝卜
            enemy_type = random.choice(['ghost', 'radish', 'slime'])
            
        self.spawn_enemy(enemy_type, spawn_x, spawn_y)
        return True  # 成功生成敌人
    
    def _generate_additional_spawn_points(self, count, min_x, min_y, max_x, max_y):
        """生成额外的随机出生点（边缘区域）
        
        Args:
            count: 要生成的出生点数量
            min_x, min_y, max_x, max_y: 地图边界
            
        Returns:
            list: 出生点坐标列表
        """
        spawn_points = []
        margin = 150  # 距离边界的边距
        
        for _ in range(count):
            # 在地图边缘区域随机生成位置
            x = random.uniform(min_x + margin, max_x - margin)
            y = random.uniform(min_y + margin, max_y - margin)
            spawn_points.append((x, y))
            
        return spawn_points
    
    def _generate_middle_spawn_points(self, count, min_x, min_y, max_x, max_y):
        """生成中间的出生点
        
        Args:
            count: 要生成的出生点数量
            min_x, min_y, max_x, max_y: 地图边界
            
        Returns:
            list: 出生点坐标列表
        """
        spawn_points = []
        
        # 计算地图中心区域
        center_x = (min_x + max_x) / 2
        center_y = (min_y + max_y) / 2
        
        # 中心区域的大小（地图的1/3）
        center_width = (max_x - min_x) / 3
        center_height = (max_y - min_y) / 3
        
        # 中心区域的边界
        center_min_x = center_x - center_width / 2
        center_max_x = center_x + center_width / 2
        center_min_y = center_y - center_height / 2
        center_max_y = center_y + center_height / 2
        
        for _ in range(count):
            # 在中心区域随机生成位置
            x = random.uniform(center_min_x, center_max_x)
            y = random.uniform(center_min_y, center_max_y)
            spawn_points.append((x, y))
            
        return spawn_points
            
    def set_difficulty(self, difficulty):
        """设置游戏难度
        
        Args:
            difficulty (str): 难度级别 ('easy', 'normal', 'hard', 'nightmare')
        """
        self.difficulty = difficulty
        
    def set_global_level(self, global_level):
        """设置全局关卡
        
        Args:
            global_level (int): 全局关卡数
        """
        self.global_level = global_level
        # 计算关卡强度倍数：每关增加30%
        self.level_strength_multiplier = 1.0 + (global_level - 1) * 0.3
        
    def get_level_strength_multiplier(self):
        """获取当前关卡强度倍数"""
        return self.level_strength_multiplier
        
    def reset_soul_spawn_flag(self):
        """重置soul生成标志，用于重新开始游戏时"""
        self.soul_spawned = False
            
    def spawn_bat(self, player):
        """在四个角落随机位置生成一个蝙蝠，确保在地图边界内"""
        if not self.map_boundaries:
            return  # 如果没有地图边界信息，无法生成蝙蝠
            
        min_x, min_y, max_x, max_y = self.map_boundaries
        
        # 定义四个角落的生成区域（距离边界100像素，调整为1倍缩放）
        corner_offset = 100
        corners = [
            (min_x + corner_offset, min_y + corner_offset),  # 左上角
            (max_x - corner_offset, min_y + corner_offset),  # 右上角
            (min_x + corner_offset, max_y - corner_offset),  # 左下角
            (max_x - corner_offset, max_y - corner_offset)   # 右下角
        ]
        
        # 随机选择一个角落
        spawn_x, spawn_y = random.choice(corners)
        
        # 在选定的角落周围添加一些随机偏移（±50像素）
        spawn_x += random.uniform(-50, 50)
        spawn_y += random.uniform(-50, 50)
        
        # 确保生成位置在地图边界内
        spawn_x = max(min_x, min(spawn_x, max_x))
        spawn_y = max(min_y, min(spawn_y, max_y))
        
        # 创建出生点标记
        spawn_marker = SpawnMarker(spawn_x, spawn_y, duration=2.0)
        self.spawn_markers.append(spawn_marker)
        
        self.spawn_enemy('bat', spawn_x, spawn_y)
        
    def _update_enemy_projectiles(self, dt):
        """更新敌人子弹"""
        for projectile in self.enemy_projectiles[:]:  # 使用切片避免在迭代时修改
            # 更新子弹位置
            # 使用正确的属性名（x, y 而不是 world_x, world_y）
            if hasattr(projectile, 'world_x'):
                projectile.world_x += projectile.direction_x * projectile.speed * dt
                projectile.world_y += projectile.direction_y * projectile.speed * dt
            elif hasattr(projectile, 'x'):
                projectile.x += projectile.direction_x * projectile.speed * dt
                projectile.y += projectile.direction_y * projectile.speed * dt
            
            # 检查子弹是否超出地图边界
            if self.map_boundaries:
                min_x, min_y, max_x, max_y = self.map_boundaries
                # 使用正确的属性名
                projectile_x = getattr(projectile, 'world_x', getattr(projectile, 'x', 0))
                projectile_y = getattr(projectile, 'world_y', getattr(projectile, 'y', 0))
                
                if (projectile_x < min_x or projectile_x > max_x or
                    projectile_y < min_y or projectile_y > max_y):
                    self.enemy_projectiles.remove(projectile)
                    continue
            
            # 检查子弹生命周期
            if hasattr(projectile, 'lifetime'):
                projectile.lifetime -= dt
                if projectile.lifetime <= 0:
                    self.enemy_projectiles.remove(projectile)
                    
    def _render_collision_circle(self, screen, enemy, screen_x, screen_y):
        """渲染敌人的碰撞圈
        
        Args:
            screen: 屏幕表面
            enemy: 敌人对象
            screen_x: 敌人在屏幕上的x坐标
            screen_y: 敌人在屏幕上的y坐标
        """
        import time
        
        # 获取当前时间用于动画
        current_time = time.time()
        
        # 计算碰撞圈的半径（基于敌人的rect大小）
        collision_radius = max(enemy.rect.width, enemy.rect.height) // 2
        
        # 获取敌人的碰撞偏移
        offset_x, offset_y = enemy._get_collision_offset()
        
        # 计算碰撞圈的中心位置（敌人rect的中心，加上偏移）
        circle_center_x = int(screen_x + enemy.rect.width // 2 + offset_x)
        circle_center_y = int(screen_y + enemy.rect.height // 2 + offset_y)
        
        # 根据敌人类型设置不同的光圈颜色和参数
        if enemy.type == 'bat':
            aura_color = (255, 100, 0)  # 橙色光圈（蝙蝠）
            size_multiplier = 1.2  # 蝙蝠光圈稍大
            animation_speed = 4    # 蝙蝠动画稍快
        elif enemy.type == 'ghost':
            aura_color = (150, 0, 255)  # 紫色光圈（幽灵）
            size_multiplier = 1.0  # 幽灵光圈正常大小
            animation_speed = 2    # 幽灵动画较慢
        elif enemy.type == 'radish':
            aura_color = (0, 255, 0)    # 绿色光圈（萝卜）
            size_multiplier = 0.8  # 萝卜光圈稍小
            animation_speed = 1.5  # 萝卜动画最慢
        elif enemy.type == 'slime':
            aura_color = (0, 255, 255)  # 青色光圈（史莱姆）
            size_multiplier = 1.1  # 史莱姆光圈稍大
            animation_speed = 3    # 史莱姆动画中等
        else:
            aura_color = (255, 0, 0)    # 红色光圈（默认）
            size_multiplier = 1.0  # 默认光圈大小
            animation_speed = 2.5  # 默认动画速度
        
        # 创建渐变光圈效果
        num_circles = 4  # 光圈层数
        base_alpha = 40  # 基础透明度
        
        for i in range(num_circles):
            # 计算当前圈的半径和透明度（应用大小倍数）
            radius = int((collision_radius + 10 - i * 8) * size_multiplier)  # 每圈递减8像素
            alpha = base_alpha - i * 8  # 每圈递减8透明度
            
            # 添加呼吸效果（使用敌人特定的动画速度）
            breath_factor = 0.6 + 0.4 * math.sin(current_time * animation_speed)  # 呼吸动画
            alpha = int(alpha * breath_factor)
            
            if alpha > 0 and radius > 0:
                # 创建带透明度的表面
                aura_surface = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
                
                # 绘制渐变圆
                for r in range(radius, 0, -2):
                    # 计算当前半径的透明度
                    current_alpha = int(alpha * (r / radius))
                    if current_alpha > 0:
                        color = (*aura_color, current_alpha)  # 使用敌人特定的颜色
                        pygame.draw.circle(aura_surface, color, (radius, radius), r, 2)
                
                # 将光圈绘制到屏幕上
                screen.blit(aura_surface, (circle_center_x - radius, circle_center_y - radius))
    
    def _render_enemy_projectiles(self, screen, camera_x, camera_y, screen_center_x, screen_center_y):
        """渲染敌人子弹"""
        for projectile in self.enemy_projectiles:
            # 计算子弹在屏幕上的位置
            # 使用正确的属性名（x, y 而不是 world_x, world_y）
            projectile_x = getattr(projectile, 'world_x', getattr(projectile, 'x', 0))
            projectile_y = getattr(projectile, 'world_y', getattr(projectile, 'y', 0))
            
            screen_x = screen_center_x + (projectile_x - camera_x)
            screen_y = screen_center_y + (projectile_y - camera_y)
            
            # 渲染子弹
            if hasattr(projectile, 'image'):
                projectile.rect.center = (screen_x, screen_y)
                screen.blit(projectile.image, projectile.rect)
            else:
                # 如果没有图像，绘制一个简单的圆形
                pygame.draw.circle(screen, (255, 0, 0), (int(screen_x), int(screen_y)), 5) 
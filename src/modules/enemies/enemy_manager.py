import pygame
import random
import math
from .types import Ghost, Radish, Bat, Slime
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
            
        # 应用波次属性加成
        if enemy and hasattr(self, 'health_multiplier') and hasattr(self, 'damage_multiplier'):
            # 应用生命值加成
            enemy.health = int(enemy.health * self.health_multiplier)
            enemy.max_health = int(enemy.max_health * self.health_multiplier)
            
            # 应用攻击力加成
            if hasattr(enemy, 'damage'):
                enemy.damage = int(enemy.damage * self.damage_multiplier)
            
        # 如果指定了生命值，覆盖配置的生命值
        if enemy and health is not None:
            enemy.health = health
            enemy.max_health = health
            
        if enemy:
            # 设置敌人的game属性，以便访问游戏对象
            if hasattr(self, 'game'):
                enemy.game = self.game
            self.enemies.append(enemy)
            
            # 打印调试信息
            print(f"🎯 生成敌人 - {enemy_type} (难度等级{self.difficulty_level}):")
            print(f"   位置: ({x}, {y})")
            print(f"   生命值: {enemy.health}/{enemy.max_health}")
            print(f"   伤害值: {enemy.damage}")
            print(f"   移动速度: {enemy.speed}")
            
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
        if self.difficulty_level != old_difficulty_level:
            print(f"🚀 难度等级提升: {old_difficulty_level} → {self.difficulty_level}")
            print(f"   游戏时间: {self.game_time:.1f}秒")
            print(f"   新生成的敌人将获得属性加成")
        
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
        """更新波次系统"""
        game_time_minutes = self.game_time / 60.0
        
        # 第一波：0:00-0:30，2.5秒生成一个，四个点位总共24个
        if game_time_minutes >= 0 and game_time_minutes < 0.5 and self.current_round == 0:
            self._start_round(1, "第1波", 2.5, 1.0, 1.0, 24)
            
        # 第一波结束，进入休息期：0:30-1:00（缩短休息期）
        elif game_time_minutes >= 0.5 and game_time_minutes < 1.0 and self.current_round == 1:
            self._end_round()
            
        # 第二波：1:00-2:30，1.5秒生成一个，四个点位总共40个
        elif game_time_minutes >= 1.0 and game_time_minutes < 2.5 and self.current_round == 0:
            self._start_round(2, "第2波", 1.5, 1.2, 1.2, 40)  # 生成速度加快，属性提升20%
            
        # 第二波结束，进入休息期：2:30-3:00（缩短休息期）
        elif game_time_minutes >= 2.5 and game_time_minutes < 3.0 and self.current_round == 2:
            self._end_round()
            
        # 第三波：3:00-5:00，1秒生成一个，四个点位总共120个
        elif game_time_minutes >= 3.0 and game_time_minutes < 5.0 and self.current_round == 0:
            self._start_round(3, "第3波", 1.0, 1.0, 1.5, 120)  # 生成速度加快，攻击力提升50%
            
        # 修复2:00-2:30之间的空白期：如果第二波还在进行，继续生成敌人
        elif game_time_minutes >= 2.0 and game_time_minutes < 2.5 and self.current_round == 2:
            # 第二波继续进行，不执行任何操作
            pass
            
        # 游戏结束：5:00后
        elif game_time_minutes >= 5.0 and self.current_round != -1:
            self._end_game()
            
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
        
        print(f"开始第{round_num}波！生成间隔: {spawn_interval}秒, 生命值倍数: {health_multiplier}, 攻击力倍数: {damage_multiplier}, 最大敌人数: {max_enemies}")
        
        # 触发波次UI显示
        if self.on_round_start:
            self.on_round_start(round_num)
        
    def _end_round(self):
        """结束当前波次"""
        self.current_round = 0
        print(f"波次结束，进入休息期")
        
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
            'text': "你安全了！",
            'timer': 0,
            'duration': 5.0,
            'color': (0, 255, 0)  # 绿色
        })
        print("游戏结束！你安全了！")
        
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
            if marker.duration <= 0:
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
                        
                        # 调试信息（可选）
                        # print(f"敌人 {enemy.type} 位置: ({enemy_world_x}, {enemy_world_y})")
                        # print(f"敌人屏幕坐标: ({enemy_screen_x}, {enemy_screen_y})")
                        # print(f"在光照内: {current_in_light}, 曾经被看到: {enemy.has_been_seen}")
                        # print(f"光照系统启用: {lighting_manager.is_enabled()}")
                        # print("---")
                        
                        # 临时修复：强制显示血条，直到光照系统问题解决
                        enemy.has_been_seen = True
                        enemy.render(screen, screen_x, screen_y, show_health_bar=True)
                        
                        # 原始逻辑（暂时注释掉）
                        # if current_in_light:
                        #     # 在光照内时，标记为已看到，显示怪物和血条
                        #     enemy.has_been_seen = True
                        #     enemy.render(screen, screen_x, screen_y, show_health_bar=True)
                        # elif enemy.has_been_seen:
                        #     # 曾经被看到过但当前不在光照内，显示怪物和血条
                        #     enemy.render(screen, screen_x, screen_y, show_health_bar=True)
                        # else:
                        #     # 如果从未被看到过且当前不在光照内，仍然渲染敌人（但可能半透明）
                        #     # 这样可以避免"看不见但能攻击"的问题
                        #     enemy.render(screen, screen_x, screen_y, show_health_bar=False)
                        
                        # 记录最后检测位置和光照状态
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
        
        # 渲染敌人子弹
        self._render_enemy_projectiles(screen, camera_x, camera_y, screen_center_x, screen_center_y)
            
    def remove_enemy(self, enemy):
        if enemy in self.enemies:
            self.enemies.remove(enemy)
            
    def random_spawn_enemy(self, player, preferred_types=None):
        """在四个角落随机位置生成敌人，确保在地图边界内
        
        Args:
            player: 玩家对象
            preferred_types: 偏好的敌人类型列表，如果为None则使用默认逻辑
        """
        if not self.map_boundaries:
            return False  # 如果没有地图边界信息，无法生成敌人
            
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
        
        # 根据偏好类型或游戏时间决定生成什么类型的敌人
        if preferred_types:
            enemy_type = random.choice(preferred_types)
        elif self.game_time < 10:  # 游戏开始10秒内
            enemy_type = 'slime'
        else:  # 10秒后可以生成幽灵和萝卜
            enemy_type = random.choice(['ghost', 'radish', 'slime'])
            
        self.spawn_enemy(enemy_type, spawn_x, spawn_y)
        return True  # 成功生成敌人
            
    def set_difficulty(self, difficulty):
        """设置游戏难度
        
        Args:
            difficulty (str): 难度级别 ('easy', 'normal', 'hard', 'nightmare')
        """
        self.difficulty = difficulty
            
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
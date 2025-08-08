import pygame
import math
from .player import Player
from .enemies.enemy_manager import EnemyManager
from .items.item_manager import ItemManager
from .items.ammo_supply_manager import AmmoSupplyManager
from .items.health_supply_manager import HealthSupplyManager
from .ui import UI
from .menu import PauseMenu, GameOverMenu, UpgradeMenu
from .menus.main_menu import MainMenu
from .menus.save_menu import SaveMenu
from .save_system import SaveSystem
from .resource_manager import resource_manager
from .upgrade_system import UpgradeManager, WeaponUpgradeLevel, PassiveUpgradeLevel
from .utils import apply_mask_collision
from .map_manager import MapManager
from .menus.map_hero_select_menu import MapHeroSelectMenu
from .lighting_manager import LightingManager
from .dual_player_system import DualPlayerSystem
from .game_buttons import GameButtons
from .game_result_ui import GameResultUI
from .main_menu_animation import MainMenuAnimation

from .minimap import Minimap
import time

class Game:
    def __init__(self, screen):
        self.screen = screen
        self.running = True
        self.paused = False
        self.game_over = False
        self.game_victory = False  # 游戏胜利状态
        self.in_main_menu = True  # 是否在主菜单
        self.in_map_hero_select = False  # 是否在地图和英雄选择界面
        
        # 获取屏幕中心点
        self.screen_center_x = self.screen.get_width() // 2
        self.screen_center_y = self.screen.get_height() // 2
        
        # 创建玩家在屏幕中心
        self.player = None
        self.dual_player_system = None  # 双角色系统
        
        # 相机位置（对应于世界坐标系中的位置）
        self.camera_x = 0
        self.camera_y = 0
        
        # 鼠标位置（用于视野系统）
        self.mouse_x = self.screen_center_x
        self.mouse_y = self.screen_center_y
        
        # 网格设置
        self.grid_size = 50  # 网格大小
        self.grid_color = (50, 50, 50)  # 网格颜色
        
        # 游戏管理器
        self.enemy_manager = None
        self.item_manager = None
        self.ammo_supply_manager = None  # 弹药补给管理器
        self.health_supply_manager = None  # 生命补给管理器
        self.teleport_manager = None  # 传送道具管理器
        self.escape_door = None  # 逃生门
        self.save_system = SaveSystem()
        self.upgrade_manager = UpgradeManager()
        self.map_manager = MapManager(screen, scale_factor=5.0)  # 创建地图管理器，使用5倍缩放
        
        # 消息提示系统
        self.message = ""
        self.message_timer = 0
        self.message_duration = 0
        
        # 创建UI和菜单
        self.ui = UI(screen)
        self.main_menu = MainMenu(screen)
        self.pause_menu = PauseMenu(screen)
        self.game_over_menu = GameOverMenu(screen)
        self.upgrade_menu = UpgradeMenu(screen)
        self.save_menu = SaveMenu(screen, True)  # 保存菜单
        self.load_menu = SaveMenu(screen, False)  # 读取菜单
        
        # 创建地图和英雄选择菜单
        self.map_hero_select_menu = MapHeroSelectMenu(
            screen,
            on_start_game=self._start_game_with_selection,
            on_back=self._back_to_main_menu
        )
        
        # 创建游戏按钮管理器
        self.game_buttons = GameButtons(screen, self)
        
        # 创建游戏结果UI
        self.game_result_ui = GameResultUI(screen)
        
        # 创建关卡过渡动画
        from .level_transition import LevelTransition
        self.level_transition = LevelTransition(screen)
        
        # 创建波次UI
        from .round_ui import RoundUI
        self.round_ui = RoundUI(screen)
        
        # 创建主页动画
        self.main_menu_animation = MainMenuAnimation(screen)
        self.showing_main_menu_animation = True  # 是否正在显示主页动画
        
        # 游戏状态
        self.game_time = 0
        self.kill_num = 0 # 击杀数
        self.level = 1
        
        # 全局关卡系统
        self.global_level = 1  # 全局关卡（每过一关+1）
        self.level_strength_multiplier = 1.0  # 关卡强度倍数（每关+30%）
        
        # 地图状态
        self.current_map = None  # 当前地图名称
        
        # 光照系统
        self.lighting_manager = None
        self.enable_lighting = True  # 是否启用光照系统
        
        # 调试模式
        self.debug_mode = False
        
        # 性能优化选项
        self.show_fps_display = True  # 是否显示FPS，默认开启
        
        # 帧数跟踪
        self.fps = 0
        self.fps_timer = 0
        self.fps_counter = 0
        self.fps_update_interval = 1.0  # 每1秒更新一次FPS
        
        # 鼠标光标相关
        self.light_cursor = None
        # self._load_light_cursor()
        
        # 小地图
        self.minimap = None
        
        # 伤害数字管理器
        from .damage_numbers import DamageNumberManager
        self.damage_number_manager = DamageNumberManager()
        
        # 初始化光照系统
        self._init_lighting_system()
        
        # 确保在菜单界面显示默认鼠标光标
        pygame.mouse.set_visible(True)
    
    def _load_light_cursor(self):
        """加载战斗中的鼠标光标"""
        try:
            from .resource_manager import resource_manager
            self.light_cursor = resource_manager.load_image('light_cursor', 'images/ui/light.png')
            if self.light_cursor:
                # 缩放光标到更大尺寸（从32x32增加到48x48）
                self.light_cursor = pygame.transform.scale(self.light_cursor, (48, 48))
                
            
        except Exception as e:
            
            self.light_cursor = None
        
    def _init_lighting_system(self):
        """初始化光照系统"""
        screen_width = self.screen.get_width()
        screen_height = self.screen.get_height()
        
        # 创建光照管理器（使用默认预设）
        self.lighting_manager = LightingManager(screen_width, screen_height, "default")
        

    
    def show_message(self, message, duration=3.0):
        """显示消息提示
        
        Args:
            message: 要显示的消息
            duration: 显示持续时间（秒）
        """
        self.message = message
        self.message_timer = 0
        self.message_duration = duration
        
    def _update_message(self, dt):
        """更新消息提示状态"""
        if self.message_timer < self.message_duration:
            self.message_timer += dt
        else:
            self.message = ""
            
    def _render_message(self):
        """渲染消息提示"""
        if self.message and self.message_timer < self.message_duration:
            # 创建支持中文的字体
            font = pygame.font.SysFont('simHei', 36)
            
            # 渲染文本
            text_surface = font.render(self.message, True, (255, 255, 255))
            text_rect = text_surface.get_rect()
            
            # 计算位置（屏幕顶部中央）
            text_rect.centerx = self.screen.get_width() // 2
            text_rect.y = 100
            
            # 绘制背景
            bg_rect = text_rect.inflate(20, 10)
            pygame.draw.rect(self.screen, (0, 0, 0, 128), bg_rect)
            pygame.draw.rect(self.screen, (255, 255, 255), bg_rect, 2)
            
            # 绘制文本
            self.screen.blit(text_surface, text_rect)
            
    def toggle_lighting(self):
        """切换光照系统开关"""
        self.enable_lighting = not self.enable_lighting
        
    def set_lighting_config(self, **kwargs):
        """设置光照配置"""
        if self.lighting_manager:
            self.lighting_manager.set_light_config(**kwargs)
    
    def set_lighting_preset(self, preset_name):
        """设置光照预设
        
        Args:
            preset_name (str): 预设名称
        """
        if self.lighting_manager:
            self.lighting_manager.set_preset(preset_name)
            preset_info = self.lighting_manager.get_preset_info(preset_name)
            if preset_info:
                self.show_message(f"已切换到: {preset_info['name']}", 2.0)
    
    def get_available_lighting_presets(self):
        """获取可用的光照预设列表"""
        if self.lighting_manager:
            return self.lighting_manager.get_available_presets()
        return []
    
    def get_current_lighting_preset(self):
        """获取当前光照预设"""
        if self.lighting_manager:
            return self.lighting_manager.get_current_preset()
        return "default"
        
    def _set_map_boundaries(self):
        """根据当前地图尺寸设置边界
        
        设置玩家的移动边界和敌人的生成边界
        """
        if not self.current_map:
            return
            
        # 获取地图尺寸
        map_width, map_height = self.map_manager.get_map_size()
        
        # 计算围栏宽度（两排32x32的围栏）
        fence_width = 2 * 32
        
        # 计算边界
        min_x = fence_width
        min_y = fence_width
        max_x = map_width - fence_width
        max_y = map_height - fence_width
        
        # 设置玩家移动边界
        if self.dual_player_system:
            # 双人模式：设置两个角色的边界
            self.dual_player_system.ninja_frog.movement.set_boundaries(min_x, min_y, max_x, max_y)
            self.dual_player_system.mystic_swordsman.movement.set_boundaries(min_x, min_y, max_x, max_y)
        elif self.player:
            # 单人模式：设置单个玩家的边界
            self.player.movement.set_boundaries(min_x, min_y, max_x, max_y)
            
        # 设置敌人生成边界
        if self.enemy_manager:
            self.enemy_manager.set_map_boundaries(min_x, min_y, max_x, max_y)
            
    def _set_player_boundaries(self):
        """设置玩家的移动边界
        
        根据当前地图的尺寸和围栏宽度设置玩家的移动边界
        """
        # 使用通用的边界设置方法
        self._set_map_boundaries()
        
    def _start_game_with_selection(self, map_id, hero_id):
        """从地图和英雄选择界面开始游戏
        
        Args:
            map_id: 地图ID
            hero_id: 英雄ID
        """
        self.in_map_hero_select = False
        self.game_over = False
        self.game_victory = False
        self.paused = False
        
        # 加载选中的地图
        self.load_map(map_id)
        
        # 获取地图尺寸
        map_width, map_height = self.map_manager.get_map_size()
        
        # 创建双角色系统
        self.dual_player_system = DualPlayerSystem(self.screen, self)
        
        # 设置两个角色的世界坐标为地图中心
        center_x = map_width // 2
        center_y = map_height // 2
        
        # 忍者蛙稍微偏左，神秘剑士稍微偏右，都往下移动32像素
        self.dual_player_system.ninja_frog.world_x = center_x - 100
        self.dual_player_system.ninja_frog.world_y = center_y + 32
        self.dual_player_system.mystic_swordsman.world_x = center_x + 100
        self.dual_player_system.mystic_swordsman.world_y = center_y + 32
        
        # 为了兼容性，设置player为忍者蛙（主要角色）
        self.player = self.dual_player_system.ninja_frog
        
        # 初始化游戏管理器
        self.enemy_manager = EnemyManager()
        self.enemy_manager.game = self  # 设置敌人管理器对游戏对象的引用
        self.enemy_manager.set_difficulty("normal")  # 设置初始难度
        self.enemy_manager.set_global_level(self.global_level)  # 设置全局关卡
        # 设置波次UI回调函数
        self.enemy_manager.on_round_start = self._on_round_start
        # 重置soul生成标志
        self.enemy_manager.reset_soul_spawn_flag()
        self.item_manager = ItemManager()
        self.ammo_supply_manager = AmmoSupplyManager(self)  # 初始化弹药补给管理器
        self.health_supply_manager = HealthSupplyManager(self)  # 初始化生命补给管理器
        
        # 初始化传送道具管理器
        from .items.teleport_manager import TeleportManager
        self.teleport_manager = TeleportManager(self.map_manager)
        
        # 生成一个初始传送道具
        self.teleport_manager.spawn_teleport_item()
        
        # 初始化钥匙管理器
        from .items.key_manager import KeyManager
        self.key_manager = KeyManager(self)
        
        # 生成逃生门（在地图右上角）
        from .items.escape_door import EscapeDoor
        door_x = map_width - 100  # 地图右上角X坐标
        door_y = 100  # 地图右上角Y坐标
        self.escape_door = EscapeDoor(door_x, door_y)
        
        # 设置边界
        self._set_map_boundaries()
        
        # 初始化玩家移动组件的碰撞数据
        if self.map_manager and self.map_manager.current_map:
            walls = self.map_manager.get_collision_tiles()
            tile_width, tile_height = self.map_manager.get_tile_size()
            
            # 设置两个角色的碰撞数据
            if self.dual_player_system:
                if hasattr(self.dual_player_system.ninja_frog, 'movement'):
                    self.dual_player_system.ninja_frog.movement.set_collision_tiles(walls, tile_width, tile_height)
                if hasattr(self.dual_player_system.mystic_swordsman, 'movement'):
                    self.dual_player_system.mystic_swordsman.movement.set_collision_tiles(walls, tile_width, tile_height)
        
        # 初始化小地图
        screen_width = self.screen.get_width()
        screen_height = self.screen.get_height()
        self.minimap = Minimap(map_width, map_height, screen_width, screen_height)
        
        # 重置游戏状态
        self.game_time = 0
        self.kill_num = 0
        self.level = 1
        

        
        # 设置相机位置为两个角色的中心位置
        center_x, center_y = self.dual_player_system.get_center_position()
        self.camera_x = center_x
        self.camera_y = center_y
        
        # 设置战斗中的鼠标光标
        if self.light_cursor:
            pygame.mouse.set_visible(False)  # 隐藏默认鼠标光标
            
        
        # 播放背景音乐
        resource_manager.play_music("background", loops=-1)
    
    def _on_round_start(self, round_number):
        """波次开始时的回调函数
        
        Args:
            round_number: 波次编号（1、2、3）
        """
        
        if self.round_ui:
            self.round_ui.show_round(round_number)
        
    def _back_to_main_menu(self):
        """从地图和英雄选择界面返回主菜单"""
        self.in_map_hero_select = False
        self.in_main_menu = True
        self.showing_main_menu_animation = True  # 重新显示主页动画
        self.main_menu_animation = MainMenuAnimation(self.screen)  # 重新创建动画
        
        # 恢复默认鼠标光标
        pygame.mouse.set_visible(True)
        
        
    def start_new_game(self):
        """显示地图和英雄选择界面"""
        self.in_main_menu = False
        self.in_map_hero_select = True
        self.map_hero_select_menu.show()
        
        # 确保在菜单界面显示默认鼠标光标
        pygame.mouse.set_visible(True)
    
    def _restart_game(self):
        """重启游戏"""
        # 重置游戏状态
        self.game_over = False
        self.game_victory = False
        self.game_result_ui.is_active = False
        
        # 重新开始游戏
        self.start_new_game()
    
    def _start_next_level(self, next_map):
        """开始下一关
        
        Args:
            next_map: 下一关的地图名称
        """
        print(f"开始下一关: {next_map}")
        
        # 重置游戏状态
        self.game_over = False
        self.game_victory = False
        self.game_result_ui.is_active = False
        
        # 加载下一关地图
        print(f"开始加载下一关地图: {next_map}")
        self.load_map(next_map)
        
        # 重置游戏时间和其他状态
        self.game_time = 0
        self.kill_num = 0
        
        # 重新初始化游戏管理器
        if self.dual_player_system:
            # 双人模式：重置两个角色的位置到地图中心
            map_width, map_height = self.map_manager.get_map_size()
            center_x = map_width // 2
            center_y = map_height // 2
            
            self.dual_player_system.ninja_frog.world_x = center_x - 100
            self.dual_player_system.ninja_frog.world_y = center_y + 32
            self.dual_player_system.mystic_swordsman.world_x = center_x + 100
            self.dual_player_system.mystic_swordsman.world_y = center_y + 32
            
            # 重置角色状态
            self.dual_player_system.ninja_frog.health = self.dual_player_system.ninja_frog.max_health
            self.dual_player_system.mystic_swordsman.health = self.dual_player_system.mystic_swordsman.max_health
            
            # 重置双人系统的能量
            self.dual_player_system.energy = 100.0
            
            # 重置角色经验值和等级
            self.dual_player_system.ninja_frog.progression.level = 1
            self.dual_player_system.ninja_frog.progression.experience = 0
            self.dual_player_system.mystic_swordsman.progression.level = 1
            self.dual_player_system.mystic_swordsman.progression.experience = 0
            
            # 重置角色金币
            self.dual_player_system.ninja_frog.progression.coins = 0
            self.dual_player_system.mystic_swordsman.progression.coins = 0
            
            # 重置角色钥匙状态
            self.dual_player_system.ninja_frog.keys_collected = 0
            self.dual_player_system.mystic_swordsman.keys_collected = 0
            
            # 重置角色移动状态
            self.dual_player_system.ninja_frog.movement.moving = {
                'up': False, 'down': False, 'left': False, 'right': False
            }
            self.dual_player_system.mystic_swordsman.movement.moving = {
                'up': False, 'down': False, 'left': False, 'right': False
            }
            # 重置移动方向和速度
            self.dual_player_system.ninja_frog.movement.direction = pygame.math.Vector2(0, 0)
            self.dual_player_system.ninja_frog.movement.velocity = pygame.math.Vector2(0, 0)
            self.dual_player_system.mystic_swordsman.movement.direction = pygame.math.Vector2(0, 0)
            self.dual_player_system.mystic_swordsman.movement.velocity = pygame.math.Vector2(0, 0)
           
            
        elif self.player:
            # 单人模式：重置玩家位置
            map_width, map_height = self.map_manager.get_map_size()
            self.player.world_x = map_width // 2
            self.player.world_y = map_height // 2
            self.player.health = self.player.max_health
            
            # 重置玩家经验值和等级
            self.player.progression.level = 1
            self.player.progression.experience = 0
            self.player.progression.coins = 0
            
            # 重置玩家钥匙状态
            self.player.keys_collected = 0
            
            # 重置玩家移动状态
            self.player.movement.moving = {
                'up': False, 'down': False, 'left': False, 'right': False
            }
            # 重置移动方向和速度
            self.player.movement.direction = pygame.math.Vector2(0, 0)
            self.player.movement.velocity = pygame.math.Vector2(0, 0)
            
        
        # 增加全局关卡
        self.global_level += 1
        
        
        # 重置敌人管理器
        if self.enemy_manager:
            self.enemy_manager.enemies.clear()
            self.enemy_manager.current_round = 0
            self.enemy_manager.game_time = 0
            # 设置新的全局关卡
            self.enemy_manager.set_global_level(self.global_level)
            # 重置soul生成标志
            self.enemy_manager.reset_soul_spawn_flag()
    
        
        # 重置物品管理器
        if self.item_manager:
            self.item_manager.items.clear()
            
        
        # 重置钥匙管理器
        if self.key_manager:
            self.key_manager.keys.clear()
            self.key_manager.spawned_keys_set.clear()
            
        
        # 重置逃生门状态
        if self.escape_door:
            self.escape_door.reset()
            
        
        # 重置弹药补给管理器
        if self.ammo_supply_manager:
            self.ammo_supply_manager.supplies.clear()
            
        
        # 重置生命补给管理器
        if self.health_supply_manager:
            self.health_supply_manager.supplies.clear()
            
        
        # 小地图已在load_map中重新创建，无需额外处理
        
        # 重置升级系统
        if self.upgrade_manager:
            self.upgrade_manager.reset()
            
        
        # 重置武器管理器
        if hasattr(self, 'weapon_manager') and self.weapon_manager:
            self.weapon_manager.reset()
            
        
        # 重置被动技能管理器
        if hasattr(self, 'passive_manager') and self.passive_manager:
            self.passive_manager.reset()
            
        
        # 重置相机位置
        if self.dual_player_system:
            # 双人模式：相机跟随两个角色的中心
            center_x = (self.dual_player_system.ninja_frog.world_x + self.dual_player_system.mystic_swordsman.world_x) // 2
            center_y = (self.dual_player_system.ninja_frog.world_y + self.dual_player_system.mystic_swordsman.world_y) // 2
        elif self.player:
            # 单人模式：相机跟随玩家
            center_x = self.player.world_x
            center_y = self.player.world_y
        
        self.camera_x = center_x
        self.camera_y = center_y
        
        # 设置战斗中的鼠标光标
        if self.light_cursor:
            pygame.mouse.set_visible(False)  # 隐藏默认鼠标光标
            
        
        print(f"下一关 {next_map} 初始化完成")
            
    def load_map(self, map_name):
        """加载指定名称的地图"""
        success = self.map_manager.load_map(map_name)
        if success:
            self.current_map = map_name
            
            # 获取地图尺寸
            map_width, map_height = self.map_manager.get_map_size()
            
            # 重新创建小地图以适应新地图尺寸
            if self.minimap:
                screen_width = self.screen.get_width()
                screen_height = self.screen.get_height()
                self.minimap = Minimap(map_width, map_height, screen_width, screen_height)
                
            
            # 重新创建逃生门
            from .items.escape_door import EscapeDoor
            door_x = map_width - 100  # 地图右上角X坐标
            door_y = 100  # 地图右上角Y坐标
            self.escape_door = EscapeDoor(door_x, door_y)
            
            
            # 根据地图尺寸设置玩家的起始位置和边界
            if self.player:
                # 将玩家放置在地图中心
                self.player.world_x = map_width // 2
                self.player.world_y = map_height // 2
                
                # 更新相机位置跟随玩家
                self.camera_x = self.player.world_x
                self.camera_y = self.player.world_y
                
                # 设置玩家和敌人边界
                self._set_map_boundaries()
            
            # 重新设置碰撞数据
            if self.map_manager and self.map_manager.current_map:
                walls = self.map_manager.get_collision_tiles()
                tile_width, tile_height = self.map_manager.get_tile_size()
                
                # 设置双人模式的碰撞数据
                if self.dual_player_system:
                    if hasattr(self.dual_player_system.ninja_frog, 'movement'):
                        self.dual_player_system.ninja_frog.movement.set_collision_tiles(walls, tile_width, tile_height)
                    if hasattr(self.dual_player_system.mystic_swordsman, 'movement'):
                        self.dual_player_system.mystic_swordsman.movement.set_collision_tiles(walls, tile_width, tile_height)
            
                
                # 设置单人模式的碰撞数据
                elif self.player and hasattr(self.player, 'movement'):
                    self.player.movement.set_collision_tiles(walls, tile_width, tile_height)
            
            
        else:
            print(f"加载地图 '{map_name}' 失败")
            
        return success

    def load_game_state(self, save_data):
        """从存档数据中加载游戏状态"""
        try:
            # 重置游戏状态
            self.in_main_menu = False
            self.game_over = False
            self.paused = False
            
            # 加载玩家数据
            player_data = save_data.get('player_data', {})
            if not player_data:
                
                return False
                
            # 创建新的玩家实例，使用存档中的英雄类型
            hero_type = player_data.get('hero_type', 'ninja_frog')
            self.player = Player(self.screen_center_x, self.screen_center_y, hero_type)

            # 设置玩家对游戏实例的引用
            self.player.game = self

            # 设置玩家属性
            self.player.health = player_data.get('health', self.player.health)
            self.player.health_component.max_health = player_data.get('max_health', self.player.health_component.max_health)
            self.player.progression.level = player_data.get('level', self.player.progression.level)
            self.player.progression.experience = player_data.get('experience', 0)
            self.player.progression.coins = player_data.get('coins', 0)
            self.player.world_x = player_data.get('world_x', self.screen_center_x)
            self.player.world_y = player_data.get('world_y', self.screen_center_y)
            
            # 加载组件状态
            component_states = player_data.get('component_states', {})
            if component_states:
                # 移动组件
                movement_states = component_states.get('movement', {})
                if movement_states:
                    self.player.movement.speed = movement_states.get('speed', self.player.movement.speed)
                    # 重置移动状态，确保加载存档后可以正常移动
                    self.player.movement.direction = pygame.math.Vector2(0, 0)
                    self.player.movement.velocity = pygame.math.Vector2(0, 0)
                    self.player.movement.moving = {
                        'up': False, 
                        'down': False, 
                        'left': False, 
                        'right': False
                    }
                    # 保留朝向状态，如果有的话
                    if 'facing_right' in movement_states:
                        self.player.movement.facing_right = movement_states.get('facing_right')
                    if 'last_direction_x' in movement_states and 'last_direction_y' in movement_states:
                        self.player.movement.last_movement_direction.x = movement_states.get('last_direction_x', 1)
                        self.player.movement.last_movement_direction.y = movement_states.get('last_direction_y', 0)
                
                # 生命值组件
                health_states = component_states.get('health', {})
                if health_states:
                    self.player.health_component.defense = health_states.get('defense', self.player.health_component.defense)
                    self.player.health_component.health_regen = health_states.get('health_regen', self.player.health_component.health_regen)
                
                # 进阶组件
                progression_states = component_states.get('progression', {})
                if progression_states:
                    self.player.progression.exp_multiplier = progression_states.get('exp_multiplier', self.player.progression.exp_multiplier)
                    self.player.progression.luck = progression_states.get('luck', self.player.progression.luck)
                
                # 被动组件
                passive_states = component_states.get('passive', {})
                if passive_states and 'passive_levels' in passive_states:
                    # 恢复被动技能状态
                    passive_levels = passive_states['passive_levels']
                    for passive_type, level in passive_levels.items():
                        # 获取被动技能对应等级的效果
                        if passive_type in self.upgrade_manager.passive_upgrades:
                            upgrade = self.upgrade_manager.passive_upgrades[passive_type]
                            # 查找对应等级的效果
                            effect = None
                            for lvl in upgrade.levels:
                                if lvl.level == level:
                                    effect = lvl.effects
                                    break
                            
                            # 应用被动技能效果
                            if effect:
                                self.player.apply_passive_upgrade(passive_type, level, effect)
                            else:
                                # 如果找不到具体效果，直接设置等级
                                self.player.passive_manager.passive_levels[passive_type] = level
                        else:
                            # 如果找不到具体升级，直接设置等级
                            self.player.passive_manager.passive_levels[passive_type] = level
                    
                    # 更新状态以应用所有被动效果
                    self.player._update_stats()
            
            # 加载武器
            weapons_data = player_data.get('weapons', [])
            if weapons_data:
                # 清空现有武器
                for weapon in list(self.player.weapons):
                    self.player.weapon_manager.remove_weapon(weapon.type)
                
                # 添加存档中的武器
                for weapon_type, level in weapons_data:
                    weapon = self.player.add_weapon(weapon_type)
                    if weapon:
                        weapon.level = level
            
            # 初始化游戏管理器
            self.enemy_manager = EnemyManager()
            self.enemy_manager.game = self  # 设置敌人管理器对游戏对象的引用
            # 设置波次UI回调函数
            self.enemy_manager.on_round_start = self._on_round_start
            # 重置soul生成标志
            self.enemy_manager.reset_soul_spawn_flag()
            self.item_manager = ItemManager()
            
            # 恢复游戏状态
            game_data = save_data.get('game_data', {})
            self.game_time = game_data.get('game_time', 0)
            self.kill_num = game_data.get('kill_num', 0)
            self.level = game_data.get('level', 1)
            self.global_level = game_data.get('global_level', 1)  # 加载全局关卡
            
            # 设置敌人管理器的难度和等级
            self.enemy_manager.difficulty_level = self.level
            self.enemy_manager.set_difficulty(game_data.get('difficulty', 'normal'))
            self.enemy_manager.set_global_level(self.global_level)  # 设置全局关卡
            
            # 恢复敌人状态
            enemies_data = save_data.get('enemies_data', [])
            for enemy_data in enemies_data:
                try:
                    self.enemy_manager.spawn_enemy(
                        enemy_data.get('type', 'normal'),
                        enemy_data.get('x', 0),
                        enemy_data.get('y', 0),
                        enemy_data.get('health', 50)
                    )
                except Exception as e:
        
                    continue
            
            # 设置相机位置
            self.camera_x = self.player.world_x
            self.camera_y = self.player.world_y
            
            # 设置边界
            self._set_map_boundaries()
            
            # 播放背景音乐
            resource_manager.play_music("background", loops=-1)
            
            # 设置战斗中的鼠标光标
            if self.light_cursor:
                pygame.mouse.set_visible(False)  # 隐藏默认鼠标光标
                
            
            return True
            
        except Exception as e:
            
            # 如果加载失败，重置到初始状态
            self.start_new_game()
            return False
        
    def handle_event(self, event):
        # 如果正在显示主页动画，只处理退出事件
        if self.showing_main_menu_animation:
            if event.type == pygame.QUIT:
                self.running = False
                return True
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE or event.key == pygame.K_ESCAPE:
                    # 允许跳过动画
                    self.showing_main_menu_animation = False
                    self.main_menu_animation.is_playing = False
                    return True
            return False
            
        # 如果在地图和英雄选择界面
        if self.in_map_hero_select:
            result = self.map_hero_select_menu.handle_event(event)
            # 不需要处理返回值，因为已经在回调函数中处理了
            return True
            
        # 如果在主菜单中
        if self.in_main_menu:
            # 如果读取菜单激活，优先处理读取菜单事件
            if self.load_menu.is_active:
                action = self.load_menu.handle_event(event)
                if action == "back":
                    self.load_menu.hide()
                elif isinstance(action, dict):  # 选择了存档
                    if self.load_game_state(action):
                        self.in_main_menu = False
                        self.load_menu.hide()
                    
                return
            
            # 处理主菜单事件
            action = self.main_menu.handle_event(event)
            if action == "start":
                self.start_new_game()
            elif action == "options":
                # 显示选项菜单（游戏介绍）
                self.main_menu.options_menu.show()
            elif action == "quit":
                self.running = False  # 设置running为False以退出游戏
            return True
            
        # 如果在暂停菜单中且读取菜单激活
        if self.load_menu.is_active:
            action = self.load_menu.handle_event(event)
            if action == "back":
                self.load_menu.hide()
            elif isinstance(action, dict):  # 选择了存档
                if self.load_game_state(action):
                    self.load_menu.hide()
                    self.paused = False  # 取消暂停状态
                
            return True
            
        # 处理保存菜单事件
        if self.save_menu.is_active:
            action = self.save_menu.handle_event(event)
            if action and action.startswith("slot_"):
                slot_id = int(action.split("_")[1])
                self.save_system.save_game(slot_id, self, self.screen)
                self.save_menu.hide()
                self.paused = False
            elif action == "back":
                self.save_menu.hide()
            return True
            
        # 处理游戏结束菜单事件（只在没有游戏结果UI时处理）
        if self.game_over and not self.game_result_ui.is_active:
            action = self.game_over_menu.handle_event(event)
            if action == "restart":
                self.start_new_game()
            elif action == "main_menu":
                self.in_main_menu = True
                self.game_over = False
                self.showing_main_menu_animation = True  # 重新显示主页动画
                self.main_menu_animation = MainMenuAnimation(self.screen)  # 重新创建动画
                resource_manager.stop_music()  # 停止游戏音乐
                # 恢复默认鼠标光标
                pygame.mouse.set_visible(True)
            elif action == "exit":
                self.running = False  # 退出游戏
            return True
            
            
        # 处理暂停菜单事件
        if self.paused:
            action = self.pause_menu.handle_event(event)
            if action == "continue":
                self.toggle_pause()
            elif action == "save":
                self.save_menu.show()
            elif action == "restart":
                self.start_new_game()
            elif action == "main_menu":  # 返回主菜单
                self.in_main_menu = True
                self.paused = False
                self.showing_main_menu_animation = True  # 重新显示主页动画
                self.main_menu_animation = MainMenuAnimation(self.screen)  # 重新创建动画
                resource_manager.stop_music()  # 停止游戏音乐
                # 恢复默认鼠标光标
                pygame.mouse.set_visible(True)
            elif action == "exit":  # 退出游戏
                self.running = False  # 直接退出游戏
            return True
               
        # 如果正在选择升级
        if self.upgrade_menu.is_active:
            selected_upgrade = self.upgrade_menu.handle_event(event)
            if selected_upgrade:
                self._apply_upgrade(selected_upgrade)
                self.upgrade_menu.hide()  # 关闭升级菜单，让游戏继续
            return True
            
        # 处理游戏结果UI事件
        if self.game_result_ui.is_active:
    
            result_action = self.game_result_ui.handle_event(event)
            if result_action:
    
                if result_action == 'restart':
                    self._restart_game()
                    return True
                elif result_action == 'main_menu':
                    self.in_main_menu = True
                    self.paused = False
                    self.game_over = False
                    self.game_victory = False
                    self.game_result_ui.is_active = False
                    self.showing_main_menu_animation = True  # 重新显示主页动画
                    self.main_menu_animation = MainMenuAnimation(self.screen)  # 重新创建动画
                    resource_manager.stop_music()
                    # 恢复默认鼠标光标
                    pygame.mouse.set_visible(True)
                    return True
                elif result_action == 'quit':
                    self.running = False
                    return True
                elif result_action == 'next_level':
                    # 进入下一关
                    if self.game_result_ui.next_map:
                        self._start_next_level(self.game_result_ui.next_map)
                    return True
            else:
                # 如果游戏结果UI激活但没有处理事件，也要消费掉事件，防止传递给其他系统
               
                return True
        
        # 处理游戏按钮事件（暂停时也能响应，但不在游戏结果UI激活时）
        if not self.game_over and not self.game_result_ui.is_active:
            button_action = self.game_buttons.handle_event(event)
            if button_action == 'pause':
                self.toggle_pause()
                return True
            elif button_action == 'restart_confirmed':
                self._restart_game()
                return True
            elif button_action == 'home_confirmed':
                self.in_main_menu = True
                self.paused = False
                self.showing_main_menu_animation = True  # 重新显示主页动画
                self.main_menu_animation = MainMenuAnimation(self.screen)  # 重新创建动画
                resource_manager.stop_music()
                # 恢复默认鼠标光标
                pygame.mouse.set_visible(True)
                return True
            elif button_action == 'setup':
                # TODO: 实现设置功能
               
                return True
            
        # ESC键暂停游戏
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.toggle_pause()
                return True
            elif event.key == pygame.K_F2:
                # 切换显示轮廓
                # TODO: 显示轮廓的逻辑放到全局的'设置'菜单中进行
                if self.player:
                    self.player.toggle_outline()
                    # 切换敌人的轮廓
                    for enemy in self.enemy_manager.enemies:
                        enemy.toggle_outline()
                return True
            elif event.key == pygame.K_F3:
                # 切换光照系统
                self.toggle_lighting()
                return True
            elif event.key == pygame.K_F4:
                # 循环切换光照预设
                if self.lighting_manager:
                    self.lighting_manager.cycle_preset()
                    current_preset = self.lighting_manager.get_current_preset()
                    preset_info = self.lighting_manager.get_preset_info(current_preset)
                    if preset_info:
                        self.show_message(f"光照预设: {preset_info['name']}", 2.0)
                return True
            
            elif event.key == pygame.K_F11:
                # 切换视野调试模式
                if self.enemy_manager:
                    self.enemy_manager.debug_vision = not getattr(self.enemy_manager, 'debug_vision', False)
                    
                return True
            elif event.key == pygame.K_F12:
                # 切换FPS显示
                self.show_fps_display = not self.show_fps_display
                return True
            
        # 更新鼠标位置（用于视野系统）
        if event.type == pygame.MOUSEMOTION:
            self.mouse_x, self.mouse_y = event.pos
        elif event.type == pygame.MOUSEBUTTONDOWN:
            # 确保鼠标点击时也更新位置
            self.mouse_x, self.mouse_y = event.pos
            
        # 处理双角色系统输入
        if self.dual_player_system:
            if self.dual_player_system.handle_event(event):
                return True  # 事件已被双角色系统处理
        elif self.player:  # 兼容单角色模式
            self.player.handle_event(event)
            
        return True
        
    def _apply_upgrade(self, upgrade_level):
        """应用升级效果
        
        Args:
            upgrade_level: WeaponUpgradeLevel 或 PassiveUpgradeLevel 实例
        """
        if isinstance(upgrade_level, WeaponUpgradeLevel):
            # 获取武器类型
            weapon_type = None
            for type_, upgrade in self.upgrade_manager.weapon_upgrades.items():
                if upgrade_level in upgrade.levels:
                    weapon_type = type_
                    break
                    
            if weapon_type:
                # 在双角色模式下，只对神秘剑士应用武器升级
                target_player = self.dual_player_system.mystic_swordsman if self.dual_player_system else self.player
                if target_player.apply_weapon_upgrade(weapon_type, upgrade_level.level, upgrade_level.effects):
                    # 如果是新武器，创建并添加到玩家的武器列表
                    if len([w for w in target_player.weapons if w.type == weapon_type]) == 0:
                        target_player.add_weapon(weapon_type)
                        
        elif isinstance(upgrade_level, PassiveUpgradeLevel):
            # 获取被动类型
            passive_type = None
            for type_, upgrade in self.upgrade_manager.passive_upgrades.items():
                if upgrade_level in upgrade.levels:
                    passive_type = type_
                    break
                    
            if passive_type:
                # 在双角色模式下，对两个角色都应用被动升级
                if self.dual_player_system:
                    # 对忍者蛙应用被动升级
                    self.dual_player_system.ninja_frog.apply_passive_upgrade(passive_type, upgrade_level.level, upgrade_level.effects)
                    # 对神秘剑士应用被动升级
                    self.dual_player_system.mystic_swordsman.apply_passive_upgrade(passive_type, upgrade_level.level, upgrade_level.effects)
                else:
                    # 单角色模式，只对当前玩家应用
                    self.player.apply_passive_upgrade(passive_type, upgrade_level.level, upgrade_level.effects)
                
    def toggle_pause(self):
        """切换游戏暂停状态"""
        self.paused = not self.paused
        if self.paused:
            self.pause_menu.show()
            resource_manager.pause_music()
        else:
            self.pause_menu.hide()
            resource_manager.unpause_music()
            # 清除所有玩家的移动状态，防止暂停时保留的键盘输入影响游戏
            self._clear_player_movement_states()
    
    def _clear_player_movement_states(self):
        """清除所有玩家的移动状态"""
        if self.dual_player_system:
            # 双人模式：清除两个角色的移动状态
            # 清除忍者蛙的移动状态
            self.dual_player_system.ninja_frog.movement.moving = {
                'up': False, 'down': False, 'left': False, 'right': False
            }
            self.dual_player_system.ninja_frog.movement.direction = pygame.math.Vector2(0, 0)
            self.dual_player_system.ninja_frog.movement.velocity = pygame.math.Vector2(0, 0)
            
            # 清除神秘剑士的移动状态
            self.dual_player_system.mystic_swordsman.movement.moving = {
                'up': False, 'down': False, 'left': False, 'right': False
            }
            self.dual_player_system.mystic_swordsman.movement.direction = pygame.math.Vector2(0, 0)
            self.dual_player_system.mystic_swordsman.movement.velocity = pygame.math.Vector2(0, 0)
          
        elif self.player:
            # 单人模式：清除玩家的移动状态
            self.player.movement.moving = {
                'up': False, 'down': False, 'left': False, 'right': False
            }
            self.player.movement.direction = pygame.math.Vector2(0, 0)
            self.player.movement.velocity = pygame.math.Vector2(0, 0)
          
        
    def update(self, dt):
        """更新游戏状态"""
        # 更新主页动画
        if self.showing_main_menu_animation:
            self.main_menu_animation.update(dt)
            if self.main_menu_animation.is_finished():
                self.showing_main_menu_animation = False
            return
            
        # 更新帧数计算
        self.fps_counter += 1
        self.fps_timer += dt
        if self.fps_timer >= self.fps_update_interval:
            self.fps = int(self.fps_counter / self.fps_timer)
    
            
            self.fps_counter = 0
            self.fps_timer = 0
        
        # 更新UI的FPS显示（仅在启用时）
        if self.ui and self.show_fps_display:
            self.ui.update_fps(dt)
            self.ui.set_fps(self.fps)
            self.ui.set_fps_display(True)  # 启用UI的FPS显示
        elif self.ui:
            self.ui.set_fps_display(False)  # 禁用UI的FPS显示
        
        # 保持游戏状态的更新
        if self.in_main_menu:
            return
            
        # 如果在地图和英雄选择界面，只更新菜单，不更新游戏逻辑
        if self.in_map_hero_select:
            return
            
        # 检查玩家是否死亡
        if self.dual_player_system:
            # 双角色模式：忍者蛙体力为零就判负
            ninja_dead = self.dual_player_system.ninja_frog.health <= 0
            
            if ninja_dead and not self.game_over:
                self.game_over = True
                self.game_result_ui.show(is_victory=False)
                resource_manager.play_sound("player_death")
                # 恢复默认鼠标光标
                pygame.mouse.set_visible(True)
                return
        elif self.player and self.player.health <= 0 and not self.game_over:
            self.game_over = True
            self.game_result_ui.show(is_victory=False)
            # 播放游戏结束音效
            resource_manager.play_sound("player_death")
            # 恢复默认鼠标光标
            pygame.mouse.set_visible(True)
            return
            
        # 检查游戏胜利
        if self.game_victory and not self.game_over:
            self.game_over = True
            
            
            # 确定下一关地图
            next_map = None
            is_final_level = False
            
            if self.current_map == "small_map":
                next_map = "test2_map"
                is_final_level = False
            elif self.current_map == "test2_map":
                next_map = "test3_map"
                is_final_level = False
            elif self.current_map == "test3_map":
                next_map = None
                is_final_level = True
            else:
                next_map = None
                is_final_level = False
            
            # 如果不是最终关卡且有下一关，直接开始关卡过渡动画
            if next_map and not is_final_level:
                
                self.level_transition.start(next_map)
            else:
                # 最终关卡或失败，显示游戏结果UI
                self.game_result_ui.show(is_victory=True, current_map=self.current_map)
                # 恢复默认鼠标光标
                pygame.mouse.set_visible(True)
            return
            
        # 更新波次UI
        if self.round_ui.is_active:
            self.round_ui.update(dt)
        
        # 如果游戏结束，更新游戏结果UI或关卡过渡动画
        if self.game_over:
            # 检查是否正在显示关卡过渡动画
            if self.level_transition.is_active:
                result = self.level_transition.update(dt)
                if result == "next_level":
                    # 关卡过渡动画结束，进入下一关
                    
                    self._start_next_level(self.level_transition.next_map)
                return
            else:
                # 更新游戏结果UI
                self.game_result_ui.update(dt)
                return
            
        # 更新双人系统的鼠标显示状态（无论是否暂停都要更新）
        if self.dual_player_system:
            self.dual_player_system.update_mouse_visibility()
        
        # 如果暂停或者正在选择升级，不更新游戏状态
        if self.paused or self.upgrade_menu.is_active or self.save_menu.is_active:
            return
            
        self.game_time += dt
        
        # 更新游戏按钮
        self.game_buttons.update(dt)
        
        # 更新消息提示
        self._update_message(dt)
        
        # 更新伤害数字管理器
        self.damage_number_manager.update(dt)
        
        # 确保玩家对象存在再更新
        if self.dual_player_system:
            # 更新双角色系统
            self.dual_player_system.update(dt)
            
            # 更新相机位置（跟随两个角色的中心）
            center_x, center_y = self.dual_player_system.get_center_position()
            self.camera_x = center_x
            self.camera_y = center_y
            
            # 更新逃生门
            if self.escape_door:
                # 双角色模式：任一角色到达逃生门即可
                self.escape_door.update(self.dual_player_system.ninja_frog)
                self.escape_door.update(self.dual_player_system.mystic_swordsman)
            
            # 更新物品管理器（双角色模式）
            if self.ammo_supply_manager:
                self.ammo_supply_manager.update(dt)
            if self.health_supply_manager:
                self.health_supply_manager.update(dt)
            if self.teleport_manager:
                # 传送道具两个角色都可以拾取，所以需要检查两个角色
                self.teleport_manager.update(dt, self.dual_player_system.ninja_frog)
                # 额外检查神秘剑士是否可以拾取传送道具（效果转移给忍者蛙）
                for teleport_item in self.teleport_manager.teleport_items[:]:
                    if teleport_item.check_collision(self.dual_player_system.mystic_swordsman):
                        if teleport_item.collect(self.dual_player_system.mystic_swordsman):
                            pass
            if self.key_manager:
                self.key_manager.update(dt, self.game_time)
                
            # 检查两个角色都可以拾取物品
       
            for player in self.dual_player_system.get_players():
           
                if self.ammo_supply_manager:
                    self.ammo_supply_manager.check_pickup(player)
                if self.health_supply_manager:
                    self.health_supply_manager.check_pickup(player)
                    
        elif self.player:  # 兼容单角色模式
            # 更新玩家位置（在世界坐标系中）
            self.player.update(dt)
            
            # 边界检测已在MovementComponent中处理
            # 如果需要，可以作为额外的保障措施
            # self._set_map_boundaries()
            
            # 更新相机位置（跟随玩家）
            self.camera_x = self.player.world_x
            self.camera_y = self.player.world_y
            
            # 更新逃生门
            if self.escape_door:
                self.escape_door.update(self.player)
            
            # 更新物品管理器（单角色模式）
            if self.ammo_supply_manager:
                self.ammo_supply_manager.update(dt)
                self.ammo_supply_manager.check_pickup(self.player)
            
            if self.health_supply_manager:
                self.health_supply_manager.update(dt)
                self.health_supply_manager.check_pickup(self.player)
            
            if self.key_manager:
                self.key_manager.update(dt, self.game_time)
            

            
            # 更新光照系统
            if self.lighting_manager and self.enable_lighting:
                # 获取当前鼠标位置
                current_mouse_x, current_mouse_y = pygame.mouse.get_pos()
                self.mouse_x, self.mouse_y = current_mouse_x, current_mouse_y

                # 更新墙壁数据
                if self.map_manager and self.map_manager.current_map:
                    walls = self.map_manager.get_collision_tiles()
                    tile_width, tile_height = self.map_manager.get_tile_size()
                    self.lighting_manager.set_walls(walls, tile_width)
                    
                    # 更新玩家移动组件的碰撞数据
                    if self.player and hasattr(self.player, 'movement'):
                        self.player.movement.set_collision_tiles(walls, tile_width, tile_height)
        
        # 更新其他游戏对象，注意检查player和enemy_manager是否存在
        if self.enemy_manager and self.player:
            # 更新敌人和武器
            if self.dual_player_system:
                # 双人模式：传递两个玩家参数
                self.enemy_manager.update(dt, self.dual_player_system.ninja_frog, self.dual_player_system.mystic_swordsman)
                self.dual_player_system.ninja_frog.update_weapons(dt)
                self.dual_player_system.mystic_swordsman.update_weapons(dt)
            else:
                # 单人模式：只传递一个玩家参数
                self.enemy_manager.update(dt, self.player)
                self.player.update_weapons(dt)
            
            # 处理死亡的敌人
            for enemy in list(self.enemy_manager.enemies):  # 使用列表复制避免在迭代时修改
                if enemy in self.enemy_manager.enemies and not enemy.alive():
                    # 防止重复处理：检查敌人是否已经被标记为死亡
                    if not hasattr(enemy, '_death_processed'):
                        enemy._death_processed = True
                        self.kill_num += 1
                        # 给玩家添加经验值奖励
                        if hasattr(enemy, 'config') and 'exp_value' in enemy.config:
                            exp_reward = enemy.config['exp_value']
                            self.player.add_experience(exp_reward)
                            print(f"击杀 {enemy.type} 获得 {exp_reward} 经验值")
                        # 在敌人死亡位置生成物品，传递player对象以应用幸运值加成
                        if self.item_manager:
                            self.item_manager.spawn_item(enemy.rect.x, enemy.rect.y, enemy.type, self.player)
                        # 移除敌人
                        self.enemy_manager.remove_enemy(enemy)
            
            # 更新物品
            if self.item_manager:
                if self.dual_player_system:
                    # 双角色模式：检查两个角色都可以拾取物品
                    # 先检查忍者蛙
                    self.item_manager.update(dt, self.dual_player_system.ninja_frog)
                    # 再检查神秘剑士
                    self.item_manager.update(dt, self.dual_player_system.mystic_swordsman)
                else:
                    self.item_manager.update(dt, self.player)
            
            # 检测碰撞
            self._check_collisions()
            
            # 检查是否可以升级（双角色模式）
            if self.dual_player_system:
                # 检查两个角色是否都可以升级
                ninja_can_upgrade = self.dual_player_system.ninja_frog.experience >= self.dual_player_system.ninja_frog.exp_to_next_level
                mystic_can_upgrade = self.dual_player_system.mystic_swordsman.experience >= self.dual_player_system.mystic_swordsman.exp_to_next_level
                
                if ninja_can_upgrade:
                    self.dual_player_system.ninja_frog.level_up()
                    self.upgrade_menu.show(self.dual_player_system.ninja_frog, self)
                elif mystic_can_upgrade:
                    self.dual_player_system.mystic_swordsman.level_up()
                    self.upgrade_menu.show(self.dual_player_system.mystic_swordsman, self)
            elif self.player:  # 兼容单角色模式
                if self.player.experience >= self.player.exp_to_next_level:
                    self.player.level_up()
                    self.upgrade_menu.show(self.player, self)
        
    def render(self):
        """渲染游戏画面"""
        # 清屏
        self.screen.fill((0, 0, 0))  # 黑色背景
        
        # 如果正在显示主页动画
        if self.showing_main_menu_animation:
            self.main_menu_animation.render()
            pygame.display.flip()
            return
        
        # 如果在主菜单
        if self.in_main_menu:
            # 如果读取菜单激活，只渲染读取菜单
            if self.load_menu.is_active:
                self.load_menu.render()
            else:
                # 否则渲染主菜单
                self.main_menu.render()
            pygame.display.flip()
            return
            
        # 如果在地图和英雄选择界面
        if self.in_map_hero_select:
            self.map_hero_select_menu.render()
            pygame.display.flip()
            return
            
        # 如果正在保存游戏
        if self.save_menu.is_active:
            self.save_menu.render()
            return
            
        # 绘制地图（如果已加载）
        if self.current_map:
            self.map_manager.render(self.camera_x, self.camera_y)
        else:
            # 如果没有地图，绘制网格作为背景
            self._draw_grid()
        
        # 确保游戏对象存在再渲染
        if self.enemy_manager:
            # 渲染游戏对象（考虑相机偏移）
            self.enemy_manager.render(self.screen, self.camera_x, self.camera_y, 
                                   self.screen_center_x, self.screen_center_y, self.lighting_manager)

        # 渲染道具（在光照系统之前，确保能被黑暗遮罩覆盖）
        if self.item_manager:
            self.item_manager.render(self.screen, self.camera_x, self.camera_y, 
                                   self.screen_center_x, self.screen_center_y, self.lighting_manager)
        
        # 渲染补给（在光照系统之前，确保能被黑暗遮罩覆盖）
        if self.ammo_supply_manager:
            self.ammo_supply_manager.render(self.screen, self.camera_x, self.camera_y, 
                                          self.screen_center_x, self.screen_center_y)
        if self.health_supply_manager:
            self.health_supply_manager.render(self.screen, self.camera_x, self.camera_y,
                                            self.screen_center_x, self.screen_center_y)
        if self.teleport_manager:
            self.teleport_manager.render(self.screen, self.camera_x, self.camera_y)
        
        # 渲染逃生门
        if self.escape_door:
            self.escape_door.render(self.screen, self.camera_x, self.camera_y, 
                                  self.screen_center_x, self.screen_center_y)
        
        # 渲染双角色系统
        if self.dual_player_system:
            self.dual_player_system.render(self.screen, self.camera_x, self.camera_y)
            self.dual_player_system.render_weapons(self.screen, self.camera_x, self.camera_y)
            
            # 为神秘剑客添加绿色三角形标记
            self._render_mystic_triangle()
            # 为忍者蛙添加粉红色三角形标记
            self._render_ninja_triangle()
        elif self.player:  # 兼容单角色模式
            self.player.render(self.screen)
            self.player.render_weapons(self.screen, self.camera_x, self.camera_y)
            self.player.render_melee_attacks(self.screen, self.camera_x, self.camera_y)
            self.player.render_ultimate(self.screen)
            # self.player.render_ultimate_cooldown(self.screen)
            self.player.render_phase_cooldown(self.screen)
            
        # 渲染光照系统（在所有游戏对象之后，UI之前）
        if self.lighting_manager and self.enable_lighting:
            try:
                # 双角色模式下，光照由双角色系统处理
                if not self.dual_player_system and self.player:
                    # 单角色模式的光照渲染
                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    self.lighting_manager.render(
                        self.screen, 
                        self.player.world_x, 
                        self.player.world_y, 
                        mouse_x, 
                        mouse_y, 
                        self.camera_x, 
                        self.camera_y
                    )
                    
            except Exception as e:
        
                # 如果光照系统出错，暂时禁用它
                self.enable_lighting = False
        # 渲染UI（在视野系统之后）
        if self.player:
            # 在双人模式下，传递双人系统参数给UI
            if self.dual_player_system:
                # 使用神秘剑士来渲染武器选择UI，并传递双人系统
                self.ui.render(self.dual_player_system.mystic_swordsman, self.game_time, self.kill_num, self.dual_player_system, self.enemy_manager)
            else:
                # 单角色模式使用普通玩家
                self.ui.render(self.player, self.game_time, self.kill_num, None, self.enemy_manager)
            
        # 渲染消息提示（在UI之后）
        self._render_message()
        
        # 渲染伤害数字（在UI之后，小地图之前）
        self.damage_number_manager.render(self.screen, self.camera_x, self.camera_y)
        
        # 渲染小地图（在UI之后）
        if self.minimap and self.player:
            # 找到所有钥匙物品
            key_items = []
            if self.item_manager:
                for item in self.item_manager.items:
                    if hasattr(item, 'item_type') and item.item_type == 'key':
                        key_items.append(item)
            
            # 添加补给物品到小地图
            ammo_supplies = None
            health_supplies = None
            teleport_items = None
            collision_tiles = None
            if self.ammo_supply_manager:
                ammo_supplies = self.ammo_supply_manager.get_supplies_for_minimap()
            if self.health_supply_manager:
                health_supplies = self.health_supply_manager.get_supplies_for_minimap()
            if self.teleport_manager:
                teleport_items = self.teleport_manager.get_items()
            if self.map_manager:
                collision_tiles = self.map_manager.get_collision_tiles()
            
            self.minimap.render(self.screen, self.player, key_items, self.escape_door, ammo_supplies, health_supplies, teleport_items, collision_tiles, self.dual_player_system)
            
        # 如果游戏暂停，渲染暂停菜单
        if self.paused:
            self.pause_menu.render()
            
        # 如果正在保存游戏，渲染保存菜单
        if self.save_menu.is_active:
            self.save_menu.render()
            
        # 如果正在选择升级，渲染升级菜单
        if self.upgrade_menu.is_active:
            self.upgrade_menu.render()
            
        # 渲染游戏按钮（在所有UI之后，最后渲染，暂停时也显示）
        if not self.game_over or self.game_result_ui.is_active:
            self.game_buttons.render()
            
        # 如果波次UI激活，渲染波次UI（在所有UI之上）
        if self.round_ui.is_active:
            self.round_ui.render()
        # 如果关卡过渡动画激活，渲染关卡过渡动画（在所有UI之上）
        elif self.level_transition.is_active:
            self.level_transition.render()
        # 如果游戏结果UI激活，渲染游戏结果UI（在所有UI之上）
        elif self.game_result_ui.is_active:
            self.game_result_ui.render()
            
        # 渲染自定义鼠标光标（在游戏进行中且不在菜单时）
        if (not self.in_main_menu and not self.in_map_hero_select and 
            not self.showing_main_menu_animation and not self.game_over and 
            self.light_cursor and not pygame.mouse.get_visible()):
            mouse_x, mouse_y = pygame.mouse.get_pos()
            # 计算光标位置（光标中心对齐鼠标位置）
            cursor_rect = self.light_cursor.get_rect()
            cursor_rect.center = (mouse_x, mouse_y)
            self.screen.blit(self.light_cursor, cursor_rect)
        
        # 更新显示
        pygame.display.flip()
        

        
    def _draw_grid(self):
        # 计算网格偏移量（基于相机位置）
        offset_x = (self.camera_x % self.grid_size)
        offset_y = (self.camera_y % self.grid_size)
        
        # 绘制垂直线
        for i in range(int(self.screen.get_width() / self.grid_size) + 2):
            x = i * self.grid_size - offset_x
            pygame.draw.line(self.screen, self.grid_color, (x, 0), (x, self.screen.get_height()))
            
        # 绘制水平线
        for i in range(int(self.screen.get_height() / self.grid_size) + 2):
            y = i * self.grid_size - offset_y
            pygame.draw.line(self.screen, self.grid_color, (0, y), (self.screen.get_width(), y))
        
    def _check_collisions(self):
        """检测碰撞"""
        # 确保敌人管理器存在
        if not self.enemy_manager:
            return
            
        # 双角色模式
        if self.dual_player_system:
            self._check_dual_player_collisions()
        # 单角色模式
        elif self.player:
            self._check_single_player_collisions()
            
    def _check_dual_player_collisions(self):
        """双角色模式的碰撞检测"""
        # 检测武器碰撞（只有神秘剑士的武器）
        for weapon in self.dual_player_system.mystic_swordsman.weapons:
            for projectile in weapon.get_projectiles():
                for enemy in self.enemy_manager.enemies:
                    # 使用碰撞半径进行检测
                    # 使用正确的属性名（x, y 而不是 world_x, world_y）
                    projectile_x = getattr(projectile, 'world_x', getattr(projectile, 'x', 0))
                    projectile_y = getattr(projectile, 'world_y', getattr(projectile, 'y', 0))
                    
                    dx = enemy.rect.centerx - projectile_x
                    dy = enemy.rect.centery - projectile_y
                    distance = (dx**2 + dy**2)**0.5
                    
                    # 使用敌人的碰撞半径和子弹的碰撞半径
                    enemy_radius = enemy.rect.width / 2
                    projectile_radius = getattr(projectile, 'collision_radius', projectile.rect.width / 2)
                    
                    if distance < enemy_radius + projectile_radius:
                        # 临时更新projectile的rect位置以进行像素级碰撞检测
                        original_projectile_rect = projectile.rect.copy()
                        projectile.rect.centerx = projectile_x
                        projectile.rect.centery = projectile_y
                        
                        # 使用像素完美碰撞检测
                        collision_detected = apply_mask_collision(enemy, projectile)
                        
                        # 恢复原始rect位置
                        projectile.rect = original_projectile_rect
                        
                        if collision_detected:
                            should_destroy = weapon.handle_collision(projectile, enemy, self.enemy_manager.enemies)
                            resource_manager.play_sound("hit")
                            
                            if enemy.health <= 0:
                                self.kill_num += 1
                                if hasattr(enemy, 'config') and 'exp_value' in enemy.config:
                                    exp_reward = enemy.config['exp_value']
                                    # 给两个角色都添加经验值
                                    self.dual_player_system.add_experience_to_both(exp_reward)
                                    print(f"击杀 {enemy.type} 获得 {exp_reward} 经验值")
                                if self.item_manager:
                                    # 使用神秘剑士作为物品生成的目标（因为只有他能攻击）
                                    self.item_manager.spawn_item(enemy.rect.x, enemy.rect.y, enemy.type, self.dual_player_system.mystic_swordsman)
                                self.enemy_manager.remove_enemy(enemy)
                                # 根据敌人类型播放不同的死亡音效
                                if enemy.type == 'bat':
                                    resource_manager.play_sound("bat_death")
                                elif enemy.type == 'ghost':
                                    resource_manager.play_sound("ghost_death")
                                elif enemy.type == 'slime':
                                    resource_manager.play_sound("slime_death")
                                elif enemy.type == 'radish':
                                    resource_manager.play_sound("radish_death")
                                elif enemy.type == 'soul':
                                    resource_manager.play_sound("soul_death")
                                else:
                                    resource_manager.play_sound("enemy_death")  # 默认音效
                                
                            if should_destroy:
                                projectile.kill()
        
        # 检测玩家和敌人的碰撞
        for enemy in self.enemy_manager.enemies:
            # 选择最近的目标（使用敌人中心坐标）
            enemy_center_x = enemy.rect.x + enemy.rect.width / 2
            enemy_center_y = enemy.rect.y + enemy.rect.height / 2
            ninja_distance = math.sqrt((enemy_center_x - self.dual_player_system.ninja_frog.world_x)**2 + 
                                     (enemy_center_y - self.dual_player_system.ninja_frog.world_y)**2)
            mystic_distance = math.sqrt((enemy_center_x - self.dual_player_system.mystic_swordsman.world_x)**2 + 
                                      (enemy_center_y - self.dual_player_system.mystic_swordsman.world_y)**2)
            
            # 选择最近的目标进行攻击
            if ninja_distance <= mystic_distance:
                target_player = self.dual_player_system.ninja_frog
            else:
                target_player = self.dual_player_system.mystic_swordsman
            
            # 检查与目标玩家的碰撞
            if not target_player.invincible:
                player_rect = target_player.rect.copy()
                player_rect.centerx = target_player.world_x
                player_rect.centery = target_player.world_y
                
                if hasattr(enemy, 'projectiles'):
                    enemy.attack_player(target_player)
                
                if player_rect.colliderect(enemy.rect):
                    
                    
                    # 临时更新玩家的rect位置以进行像素级碰撞检测
                    original_rect = target_player.rect.copy()
                    target_player.rect.centerx = target_player.world_x
                    target_player.rect.centery = target_player.world_y
                    
                    # 进行像素级碰撞检测
                    collision_detected = apply_mask_collision(target_player, enemy)
                    
                    # 恢复原始rect位置
                    target_player.rect = original_rect
                    
                    if collision_detected:
                        
                        if enemy.attack_player(target_player):
                            # 如果神秘剑客受到伤害，让忍者蛙扣血
                            
                            resource_manager.play_sound("player_hurt")
                            break
        
        # 检测敌人子弹和玩家的碰撞
        if hasattr(self.enemy_manager, 'enemy_projectiles'):
            
            for projectile in self.enemy_manager.enemy_projectiles[:]:
                # 计算子弹到两个玩家的距离
                # 使用正确的属性名（x, y 而不是 world_x, world_y）
                projectile_x = getattr(projectile, 'world_x', getattr(projectile, 'x', 0))
                projectile_y = getattr(projectile, 'world_y', getattr(projectile, 'y', 0))
                
                ninja_dx = self.dual_player_system.ninja_frog.world_x - projectile_x
                ninja_dy = self.dual_player_system.ninja_frog.world_y - projectile_y
                ninja_distance = (ninja_dx**2 + ninja_dy**2)**0.5
                
                mystic_dx = self.dual_player_system.mystic_swordsman.world_x - projectile_x
                mystic_dy = self.dual_player_system.mystic_swordsman.world_y - projectile_y
                mystic_distance = (mystic_dx**2 + mystic_dy**2)**0.5
                
                
                
                # 选择最近的目标进行攻击
                if ninja_distance <= mystic_distance:
                    target_player = self.dual_player_system.ninja_frog
                    distance = ninja_distance
                else:
                    target_player = self.dual_player_system.mystic_swordsman
                    distance = mystic_distance
                
               
                
                if distance < 50:  # 减小碰撞距离到50像素
                    
                    if hasattr(projectile, 'damage'):
                        # 如果神秘剑客受到伤害，让忍者蛙扣血
                        if target_player.hero_type == "role2":  # 神秘剑客被击中
                            self.dual_player_system.ninja_frog.take_damage(projectile.damage)
                            
                        else:  # 忍者蛙被击中
                            target_player.take_damage(projectile.damage)
                            
                            
                    
                    self.enemy_manager.enemy_projectiles.remove(projectile)
                    resource_manager.play_sound("player_hurt")
                
                    
    def _check_single_player_collisions(self):
        """单角色模式的碰撞检测"""
        # 确保玩家存在
        if not self.player:
            return
            
        # 检测武器碰撞
        for weapon in self.player.weapons:
            for projectile in weapon.get_projectiles():
                for enemy in self.enemy_manager.enemies:
                    # 首先使用矩形做快速检测
                    # 计算世界坐标系中的距离
                    # 使用正确的属性名（x, y 而不是 world_x, world_y）
                    projectile_x = getattr(projectile, 'world_x', getattr(projectile, 'x', 0))
                    projectile_y = getattr(projectile, 'world_y', getattr(projectile, 'y', 0))
                    
                    dx = enemy.rect.x - projectile_x
                    dy = enemy.rect.y - projectile_y
                    distance = (dx**2 + dy**2)**0.5
                    
                    if distance < enemy.rect.width / 2 + projectile.rect.width / 2:
                        # 进行更精确的像素级碰撞检测
                        # 临时更新projectile的rect位置以进行像素级碰撞检测
                        original_projectile_rect = projectile.rect.copy()
                        projectile.rect.centerx = projectile_x
                        projectile.rect.centery = projectile_y
                        
                        collision_detected = apply_mask_collision(enemy, projectile)
                        
                        # 恢复原始rect位置
                        projectile.rect = original_projectile_rect
                        
                        if collision_detected:
                            # 处理碰撞
                            should_destroy = weapon.handle_collision(projectile, enemy, self.enemy_manager.enemies)
                            # 播放击中音效
                            resource_manager.play_sound("hit")
                            
                            if enemy.health <= 0:
                                self.kill_num += 1
                                # 给玩家添加经验值奖励
                                if hasattr(enemy, 'config') and 'exp_value' in enemy.config:
                                    exp_reward = enemy.config['exp_value']
                                    self.player.add_experience(exp_reward)
                                    print(f"击杀 {enemy.type} 获得 {exp_reward} 经验值")
                                # 在敌人死亡位置生成物品，传递player对象以应用幸运值加成
                                if self.item_manager:
                                    self.item_manager.spawn_item(enemy.rect.x, enemy.rect.y, enemy.type, self.player)
                                self.enemy_manager.remove_enemy(enemy)
                                # 播放敌人死亡音效
                                resource_manager.play_sound("enemy_death")
                                
                            if should_destroy:
                                projectile.kill()
        
        # 检测玩家和敌人的碰撞
        for enemy in self.enemy_manager.enemies:
            if not self.player.invincible:  # 只在玩家不处于无敌状态时检测碰撞
                # 首先进行矩形快速检测
                player_rect = self.player.rect.copy()
                player_rect.centerx = self.player.world_x
                player_rect.centery = self.player.world_y
                
                # 对于Slime等远程攻击敌人，即使不直接碰撞也需要触发attack_player
                # 这样才能正确生成投射物并处理碰撞逻辑
                if hasattr(enemy, 'projectiles'):
                    enemy.attack_player(self.player)
                
                # 对于直接碰撞的敌人，进行常规碰撞检测
                if player_rect.colliderect(enemy.rect):
                    # 临时更新玩家的rect位置以进行像素级碰撞检测
                    original_rect = self.player.rect.copy()
                    self.player.rect.centerx = self.player.world_x
                    self.player.rect.centery = self.player.world_y
                    
                    # 进行像素级碰撞检测
                    collision_detected = apply_mask_collision(self.player, enemy)
                    
                    # 恢复原始rect位置
                    self.player.rect = original_rect
                    
                    if collision_detected:
                        if enemy.attack_player(self.player):
                            # 播放受伤音效
                            resource_manager.play_sound("player_hurt")
                            break  # 一次只处理一个碰撞
        
        # 检测敌人子弹和玩家的碰撞
        if hasattr(self.enemy_manager, 'enemy_projectiles'):
            for projectile in self.enemy_manager.enemy_projectiles[:]:  # 使用切片避免在迭代时修改
                # 计算子弹和玩家的距离
                dx = self.player.world_x - projectile.world_x
                dy = self.player.world_y - projectile.world_y
                distance = (dx**2 + dy**2)**0.5
                
                if distance < 80:  # 增大碰撞检测范围从30到80像素
                    # 对玩家造成伤害
                    if hasattr(projectile, 'damage'):
                        self.player.take_damage(projectile.damage)
                        print(f"玩家受到 {projectile.damage} 点伤害")
                    
                    # 移除子弹
                    self.enemy_manager.enemy_projectiles.remove(projectile)
                    
                    # 播放受伤音效
                    resource_manager.play_sound("player_hurt")
            
        # 检测武器碰撞
        for weapon in self.player.weapons:
            for projectile in weapon.get_projectiles():
                for enemy in self.enemy_manager.enemies:
                    # 首先使用矩形做快速检测
                    # 计算世界坐标系中的距离
                    dx = enemy.rect.x - projectile.world_x
                    dy = enemy.rect.y - projectile.world_y
                    distance = (dx**2 + dy**2)**0.5
                    
                    if distance < enemy.rect.width / 2 + projectile.rect.width / 2:
                        # 进行更精确的像素级碰撞检测
                        # 临时更新projectile的rect位置以进行像素级碰撞检测
                        original_projectile_rect = projectile.rect.copy()
                        projectile.rect.centerx = projectile.world_x
                        projectile.rect.centery = projectile.world_y
                        
                        collision_detected = apply_mask_collision(enemy, projectile)
                        
                        # 恢复原始rect位置
                        projectile.rect = original_projectile_rect
                        
                        if collision_detected:
                            # 处理碰撞
                            should_destroy = weapon.handle_collision(projectile, enemy, self.enemy_manager.enemies)
                            # 播放击中音效
                            resource_manager.play_sound("hit")
                            
                            if enemy.health <= 0:
                                self.kill_num += 1
                                # 给玩家添加经验值奖励
                                if hasattr(enemy, 'config') and 'exp_value' in enemy.config:
                                    exp_reward = enemy.config['exp_value']
                                    self.player.add_experience(exp_reward)
                                    print(f"击杀 {enemy.type} 获得 {exp_reward} 经验值")
                                # 在敌人死亡位置生成物品，传递player对象以应用幸运值加成
                                if self.item_manager:
                                    self.item_manager.spawn_item(enemy.rect.x, enemy.rect.y, enemy.type, self.player)
                                self.enemy_manager.remove_enemy(enemy)
                                # 播放敌人死亡音效
                                resource_manager.play_sound("enemy_death")
                                
                            if should_destroy:
                                projectile.kill()
        
        # 检测玩家和敌人的碰撞
        for enemy in self.enemy_manager.enemies:
            if not self.player.invincible:  # 只在玩家不处于无敌状态时检测碰撞
                # 首先进行矩形快速检测
                player_rect = self.player.rect.copy()
                player_rect.centerx = self.player.world_x
                player_rect.centery = self.player.world_y
                
                # 对于Slime等远程攻击敌人，即使不直接碰撞也需要触发attack_player
                # 这样才能正确生成投射物并处理碰撞逻辑
                if hasattr(enemy, 'projectiles'):
                    enemy.attack_player(self.player)
                
                # 对于直接碰撞的敌人，进行常规碰撞检测
                if player_rect.colliderect(enemy.rect):
                    # 临时更新玩家的rect位置以进行像素级碰撞检测
                    original_rect = self.player.rect.copy()
                    self.player.rect.centerx = self.player.world_x
                    self.player.rect.centery = self.player.world_y
                    
                    # 进行像素级碰撞检测
                    collision_detected = apply_mask_collision(self.player, enemy)
                    
                    # 恢复原始rect位置
                    self.player.rect = original_rect
                    
                    if collision_detected:
                        if enemy.attack_player(self.player):
                            # 播放受伤音效
                            resource_manager.play_sound("player_hurt")
                            break  # 一次只处理一个碰撞
        
        # 检测敌人子弹和玩家的碰撞
        if hasattr(self.enemy_manager, 'enemy_projectiles'):
            for projectile in self.enemy_manager.enemy_projectiles[:]:  # 使用切片避免在迭代时修改
                # 计算子弹和玩家的距离
                dx = self.player.world_x - projectile.world_x
                dy = self.player.world_y - projectile.world_y
                distance = (dx**2 + dy**2)**0.5
                
                if distance < 30:  # 碰撞检测范围
                    # 对玩家造成伤害
                    if hasattr(projectile, 'damage'):
                        self.player.take_damage(projectile.damage)
                        print(f"玩家受到 {projectile.damage} 点伤害")
                    
                    # 移除子弹
                    self.enemy_manager.enemy_projectiles.remove(projectile)
                    
                    # 播放受伤音效
                    resource_manager.play_sound("player_hurt")
        
    def _update_game_state(self):
        # 获取当前等级
        current_level = int(self.game_time // 60) + 1  # 每60秒提升一级
        
        # 如果等级提升了
        if current_level > self.level:
            # 播放升级音效
            resource_manager.play_sound("level_up")
            
        # 更新等级和难度
        self.level = current_level
        
        # 确保敌人管理器存在再更新难度
        if self.enemy_manager:
            self.enemy_manager.difficulty_level = self.level  # 更新敌人管理器中的难度等级
    
    def _render_mystic_triangle(self):
        """为神秘剑客渲染绿色三角形标记"""
        if not self.dual_player_system:
            return
            
        mystic = self.dual_player_system.mystic_swordsman
        
        # 计算神秘剑客在屏幕上的位置
        screen_x = mystic.world_x - self.camera_x + self.screen_center_x
        screen_y = mystic.world_y - self.camera_y + self.screen_center_y
        
        # 三角形参数
        triangle_size = 12
        triangle_color = (0, 200, 0)  # 深绿色
        border_color = (255, 255, 255)  # 白色边框
        
        # 计算三角形的三个顶点（向上指向的三角形）
        points = [
            (screen_x, screen_y-triangle_size-40),  # 顶点
            (screen_x - triangle_size//2, screen_y - triangle_size//2-60),  # 左下角
            (screen_x + triangle_size//2, screen_y - triangle_size//2-60)   # 右下角
        ]
        
        # 绘制三角形
        pygame.draw.polygon(self.screen, triangle_color, points)
        
        # 绘制边框
        pygame.draw.polygon(self.screen, border_color, points, 2)
        
    def _render_ninja_triangle(self):
        """为忍者蛙渲染粉红色三角形标记"""
        if not self.dual_player_system:
            return
            
        ninja = self.dual_player_system.ninja_frog
        
        # 计算忍者蛙在屏幕上的位置
        screen_x = ninja.world_x - self.camera_x + self.screen_center_x
        screen_y = ninja.world_y - self.camera_y + self.screen_center_y
        
        # 三角形参数
        triangle_size = 12
        triangle_color = (255, 20, 147)  # 粉红色
        border_color = (255, 255, 255)  # 白色边框
        
        # 计算三角形的三个顶点（向上指向的三角形）
        points = [
            (screen_x, screen_y - triangle_size - 40),  # 顶点
            (screen_x - triangle_size//2, screen_y - triangle_size//2 - 60),  # 左下角
            (screen_x + triangle_size//2, screen_y - triangle_size//2 - 60)   # 右下角
        ]
        
        # 绘制三角形
        pygame.draw.polygon(self.screen, triangle_color, points)
        
        # 绘制边框
        pygame.draw.polygon(self.screen, border_color, points, 2)
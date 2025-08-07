import pygame
import time
from .utils import FontManager
from .resource_manager import resource_manager
from .upgrade_system import UpgradeManager

class UI:
    def __init__(self, screen):
        self.screen = screen
        pygame.font.init()
        self.font = pygame.font.SysFont('simHei', 24)
        self.small_font = pygame.font.SysFont('simHei', 80)  # 较小的字体用于时间显示
        
        # FPS相关
        self.fps_font = pygame.font.SysFont('simHei', 20)  # FPS显示字体
        self.fps_timer = 0
        self.fps_counter = 0
        self.current_fps = 0
        self.last_fps_update = time.time()
        
        # UI颜色
        self.exp_bar_color = (0, 255, 255)    # 青色
        self.exp_back_color = (0, 100, 100)   # 深青色
        self.health_bar_color = (255, 0, 0)   # 红色
        self.health_back_color = (100, 0, 0)  # 深红色
        self.text_color = (255, 255, 255)     # 白色
        self.coin_color = (255, 215, 0)       # 金色
        self.fps_color = (0, 255, 0)          # 绿色FPS显示
        
        # UI尺寸和位置
        self.margin = 10  # 减小边距
        self.bar_height = 20
        self.icon_size = 32  # 技能图标大小
        self.icon_spacing = 10  # 图标之间的间距
        
        # 加载金币图标
        self.coin_icon = resource_manager.load_image('coin', 'images/items/coin_32x32.png')
        self.coin_icon = pygame.transform.scale(self.coin_icon, (24, 24))  # 调整金币图标大小
        
        # 加载击杀统计图标
        self.kill_icon = resource_manager.load_image('kill_count', 'images/enemy/enemy_kill_32x32.png')
        self.kill_icon = pygame.transform.scale(self.kill_icon, (24, 24))  # 调整击杀图标大小
        
        # 加载电量图标
        self.energy_icon = resource_manager.load_image('energy_icon', 'images/ui/light_icon.png')
        self.energy_icon = pygame.transform.scale(self.energy_icon, (24, 24))  # 调整电量图标大小
        
        # 加载传送道具图标
        try:
            self.teleport_icon = resource_manager.load_image('teleport_icon', 'images/ui/transport.png')
            self.teleport_icon = pygame.transform.scale(self.teleport_icon, (73, 64))  # 调整传送道具图标大小
            print("传送道具图标加载成功")
        except Exception as e:
            print(f"传送道具图标加载失败: {e}")
            # 创建一个默认的传送道具图标
            self.teleport_icon = pygame.Surface((73, 64), pygame.SRCALPHA)
            pygame.draw.circle(self.teleport_icon, (0, 255, 255), (36, 32), 30)  # 青色圆圈
            pygame.draw.circle(self.teleport_icon, (255, 255, 255), (36, 32), 15)  # 白色内圈
        
        # 加载心形血量图标
        try:
            self.heart_icon = resource_manager.load_image('heart_icon', 'images/ui/heart_icon.png')
            self.heart_icon = pygame.transform.scale(self.heart_icon, (32, 32))  # 调整心形图标大小
            print("心形血量图标加载成功")
        except Exception as e:
            print(f"心形血量图标加载失败: {e}")
            # 创建一个默认的心形图标
            self.heart_icon = pygame.Surface((32, 32), pygame.SRCALPHA)
            pygame.draw.circle(self.heart_icon, (255, 0, 0), (16, 16), 15)  # 红色圆圈作为替代
        
        # 加载武器选择图标
        self.knife_black = resource_manager.load_image('knife_black', 'images/ui/knife_black.png')
        self.knife_white = resource_manager.load_image('knife_white', 'images/ui/knife_white.png')
        self.gun_black = resource_manager.load_image('gun_black', 'images/ui/Gun_black.png')
        self.gun_white = resource_manager.load_image('gun_white', 'images/ui/Gun_white.png')
        
        # 调整武器图标大小
        self.weapon_icon_size = 40
        self.knife_black = pygame.transform.scale(self.knife_black, (self.weapon_icon_size, self.weapon_icon_size))
        self.knife_white = pygame.transform.scale(self.knife_white, (self.weapon_icon_size, self.weapon_icon_size))
        self.gun_black = pygame.transform.scale(self.gun_black, (self.weapon_icon_size, self.weapon_icon_size))
        self.gun_white = pygame.transform.scale(self.gun_white, (self.weapon_icon_size, self.weapon_icon_size))
        
        # 创建升级管理器实例用于获取图标
        self.upgrade_manager = UpgradeManager()
        
        # 武器模式显示相关
        self.weapon_mode_font = pygame.font.SysFont('simHei', 20)
        
    def update_fps(self, dt):
        """更新FPS计算"""
        self.fps_counter += 1
        self.fps_timer += dt
        
        # 每秒更新一次FPS显示
        if self.fps_timer >= 1.0:
            self.current_fps = self.fps_counter
            self.fps_counter = 0
            self.fps_timer = 0
    
    def set_fps(self, fps):
        """设置FPS值（从游戏类获取）"""
        self.current_fps = fps
            
    def _render_fps(self):
        """渲染FPS显示"""
        screen_width = self.screen.get_width()
        
        # 小地图位置：右上角 (screen_width - 270 - 60, 150)
        # FPS显示位置：小地图左边，距离小地图10像素
        minimap_x = screen_width - 270 - 60
        fps_x = minimap_x - 80  # 小地图左边80像素
        fps_y = 150  # 与小地图同高度
        
        # 渲染FPS文本
        fps_text = f"FPS: {self.current_fps}"
        fps_surface = self.fps_font.render(fps_text, True, self.fps_color)
        
        # 添加半透明背景
        text_rect = fps_surface.get_rect()
        text_rect.topleft = (fps_x, fps_y)
        
        # 创建背景矩形
        bg_rect = pygame.Rect(fps_x - 5, fps_y - 2, text_rect.width + 10, text_rect.height + 4)
        bg_surface = pygame.Surface((bg_rect.width, bg_rect.height))
        bg_surface.set_alpha(128)
        bg_surface.fill((0, 0, 0))
        self.screen.blit(bg_surface, bg_rect)
        
        # 渲染FPS文本
        self.screen.blit(fps_surface, text_rect)
        
    def _render_ammo_info(self, player):
        """渲染弹药信息
        
        Args:
            player: 玩家实例
        """
        # 检查是否有远程武器
        has_ranged_weapon = False
        total_ammo = 0
        max_ammo = 0
        
        # 统计所有远程武器的弹药
        if hasattr(player, 'weapon_manager'):
            for weapon in player.weapon_manager.weapons:
                if hasattr(weapon, 'ammo') and not weapon.is_melee:
                    has_ranged_weapon = True
                    total_ammo += weapon.ammo
                    if hasattr(weapon, 'max_ammo'):
                        max_ammo += weapon.max_ammo
                    else:
                        max_ammo += float('inf')
        
        # 如果没有远程武器，不显示弹药UI
        if not has_ranged_weapon:
            return
        
        # 显示弹药文本
        if max_ammo == float('inf'):
            ammo_text = f"弹药: {total_ammo}"
        else:
            ammo_text = f"弹药: {total_ammo}/{max_ammo}"
        
        # 渲染弹药文本
        ammo_surface = self.font.render(ammo_text, True, (255, 255, 255))
        ammo_rect = ammo_surface.get_rect()
        
        # 计算右下角位置
        screen_width = self.screen.get_width()
        screen_height = self.screen.get_height()
        
        # 使用金币图标
        ammo_icon = self.coin_icon
        icon_rect = ammo_icon.get_rect()
        
        # 计算图标和文本的位置（右下角）
        icon_rect.bottomright = (screen_width - 10, screen_height - 10)
        ammo_rect.right = icon_rect.left - 5
        ammo_rect.centery = icon_rect.centery
        
        # 添加背景
        bg_rect = pygame.Rect(ammo_rect.left - 5, ammo_rect.top - 2, 
                             ammo_rect.width + 10 + icon_rect.width + 5, ammo_rect.height + 4)
        bg_surface = pygame.Surface((bg_rect.width, bg_rect.height))
        bg_surface.set_alpha(128)
        bg_surface.fill((0, 0, 0))
        self.screen.blit(bg_surface, bg_rect)
        
        # 渲染图标和文本
        self.screen.blit(ammo_icon, icon_rect)
        self.screen.blit(ammo_surface, ammo_rect)
        
    def _render_key_info(self, player, game_time):
        """渲染钥匙信息
        
        Args:
            player: 玩家实例
            game_time: 当前游戏时间
        """
        # 检查玩家是否有钥匙系统
        if not hasattr(player, 'keys_collected') or not hasattr(player, 'total_keys_needed'):
            return
            
        # 获取钥匙管理器
        key_manager = None
        if hasattr(player, 'game') and player.game and hasattr(player.game, 'key_manager'):
            key_manager = player.game.key_manager
            
        # 显示钥匙数量
        key_text = f"钥匙: {player.keys_collected}/{player.total_keys_needed}"
        
        # 渲染钥匙文本
        key_surface = self.font.render(key_text, True, (255, 255, 0))  # 黄色
        key_rect = key_surface.get_rect()
        
        # 计算位置（向右500像素，向下100像素）
        key_rect.topleft = (10, 400)
        
        # 添加背景
        bg_rect = pygame.Rect(key_rect.left - 5, key_rect.top - 2, 
                             key_rect.width + 10, key_rect.height + 4)
        bg_surface = pygame.Surface((bg_rect.width, bg_rect.height))
        bg_surface.set_alpha(128)
        bg_surface.fill((0, 0, 0))
        self.screen.blit(bg_surface, bg_rect)
        
        # 渲染文本
        self.screen.blit(key_surface, key_rect)
        
        # 显示下一把钥匙倒计时
        if key_manager:
            countdown = key_manager.get_next_key_countdown(game_time)
            if countdown is not None:
                # 格式化倒计时显示
                if countdown >= 60:
                    countdown_text = f"下一把钥匙: {int(countdown // 60)}分{int(countdown % 60)}秒"
                else:
                    countdown_text = f"下一把钥匙: {int(countdown)}秒"
                
                # 渲染倒计时文本
                countdown_surface = self.font.render(countdown_text, True, (0, 255, 255))  # 青色
                countdown_rect = countdown_surface.get_rect()
                
                # 位置：在钥匙数量下方（向右500像素，向下100像素）
                countdown_rect.topleft = (10, key_rect.bottom + 5)
                
                # 添加背景
                countdown_bg_rect = pygame.Rect(countdown_rect.left - 5, countdown_rect.top - 2, 
                                             countdown_rect.width + 10, countdown_rect.height + 4)
                countdown_bg_surface = pygame.Surface((countdown_bg_rect.width, countdown_bg_rect.height))
                countdown_bg_surface.set_alpha(128)
                countdown_bg_surface.fill((0, 0, 0))
                self.screen.blit(countdown_bg_surface, countdown_bg_rect)
                
                # 渲染倒计时文本
                self.screen.blit(countdown_surface, countdown_rect)
    
    def _render_weapon_mode(self, player):
        """渲染武器模式信息（仅对神秘剑士）
        
        Args:
            player: 玩家实例
        """
        # 检查是否是神秘剑士
        if not hasattr(player, 'hero_type') or player.hero_type != "role2":
            return
            
        # 检查是否有武器模式属性
        if not hasattr(player, 'is_ranged_mode'):
            return
            
        # 确定当前模式文本（中文）
        if player.is_ranged_mode:
            mode_text = "远程模式"
            mode_color = (0, 255, 0)  # 绿色
        else:
            mode_text = "近战模式"
            mode_color = (255, 165, 0)  # 橙色
        
        # 渲染模式文本
        mode_surface = self.weapon_mode_font.render(mode_text, True, mode_color)
        mode_rect = mode_surface.get_rect()
        
        # 位置：右上角，在弹药信息下方
        screen_width = self.screen.get_width()
        screen_height = self.screen.get_height()
        mode_rect.topright = (screen_width - 10, screen_height - 50)
        
        # 添加背景
        bg_rect = pygame.Rect(mode_rect.left - 5, mode_rect.top - 2, 
                             mode_rect.width + 10, mode_rect.height + 4)
        bg_surface = pygame.Surface((bg_rect.width, bg_rect.height))
        bg_surface.set_alpha(128)
        bg_surface.fill((0, 0, 0))
        self.screen.blit(bg_surface, bg_rect)
        
        # 渲染模式文本
        self.screen.blit(mode_surface, mode_rect)
        
    def _render_weapon_selection_ui(self, player):
        """渲染武器选择UI
        
        Args:
            player: 玩家实例
        """
        # 检查是否是神秘剑士
        if not hasattr(player, 'hero_type') or player.hero_type != "role2":
            return
            
        # 检查是否有武器模式属性
        if not hasattr(player, 'is_ranged_mode'):
            return
        
        screen_width = self.screen.get_width()
        screen_height = self.screen.get_height()
        
        # 计算心形血条位置
        heart_y = screen_height - 100 - 40  # 与_render_heart_health中的位置保持一致
        
        # 武器选择UI位置：心形血条正上方160像素
        weapon_ui_y = heart_y - 160
        
        # 计算两个图标的位置（居中靠左分布）
        # 计算屏幕中心位置
        screen_center_x = screen_width // 2
        
        # 图标间距
        icon_spacing = 20
        
        # 计算两个图标的总宽度
        total_width = self.weapon_icon_size * 2 + icon_spacing
        
        # 计算起始位置（居中靠左）
        start_x = screen_center_x - total_width+50  # 从中心向左偏移，再往右移动100像素
        
        # 刀图标位置（左侧）
        knife_x = start_x
        knife_y = weapon_ui_y
        
        # 枪图标位置（右侧）
        gun_x = start_x + self.weapon_icon_size + icon_spacing
        gun_y = weapon_ui_y
        
        # 根据当前武器模式选择显示的图标
        if player.is_ranged_mode:
            # 远程模式：枪在左边（白色，放大2.5倍），刀在右边（灰色）
            # 放大枪的图标到2.5倍
            gun_icon_large = pygame.transform.scale(self.gun_white, 
                (int(self.weapon_icon_size * 2.5), int(self.weapon_icon_size * 2.5)))
            gun_x_large = knife_x - (gun_icon_large.get_width() - self.weapon_icon_size) // 2
            gun_y_large = knife_y - (gun_icon_large.get_height() - self.weapon_icon_size) // 2
            
            # 创建灰色的刀图标
            knife_gray = self.knife_black.copy()
            # 将黑色图标转换为灰色
            knife_gray.fill((128, 128, 128), special_flags=pygame.BLEND_RGB_MULT)
            
            # 渲染图标
            self.screen.blit(gun_icon_large, (gun_x_large, gun_y_large))  # 枪在左边
            self.screen.blit(knife_gray, (gun_x+10, gun_y))  # 刀在右边，灰色
        else:
            # 近战模式：刀在左边（白色，放大2.5倍），枪在右边（灰色）
            # 放大刀的图标到2.5倍
            knife_icon_large = pygame.transform.scale(self.knife_white, 
                (int(self.weapon_icon_size * 2.5), int(self.weapon_icon_size * 2.5)))
            knife_x_large = knife_x - (knife_icon_large.get_width() - self.weapon_icon_size) // 2
            knife_y_large = knife_y - (knife_icon_large.get_height() - self.weapon_icon_size) // 2
            
            # 创建灰色的枪图标
            gun_gray = self.gun_black.copy()
            # 将黑色图标转换为灰色
            gun_gray.fill((128, 128, 128), special_flags=pygame.BLEND_RGB_MULT)
            
            # 渲染图标
            self.screen.blit(knife_icon_large, (knife_x_large, knife_y_large))  # 刀在左边
            self.screen.blit(gun_gray, (gun_x+10, gun_y))  # 枪在右边，灰色

    def _render_ammo_display_left(self, player):
        """在左侧显示弹药信息（双人模式专用）
        
        Args:
            player: 玩家实例（神秘剑士）
        """
        # 检查是否有远程武器
        has_ranged_weapon = False
        total_ammo = 0
        max_ammo = 0
        is_reloading = False
        reload_progress = 0.0
        current_bullets = 0  # 当前子弹（还能打多少发需要装弹）
        total_bullets = 0    # 总子弹数
        
        # 统计所有远程武器的弹药
        if hasattr(player, 'weapon_manager'):
            for weapon in player.weapon_manager.weapons:
                if hasattr(weapon, 'ammo') and not weapon.is_melee:
                    has_ranged_weapon = True
                    total_ammo += weapon.ammo
                    if hasattr(weapon, 'max_ammo'):
                        max_ammo += weapon.max_ammo
                    else:
                        max_ammo += float('inf')
                    
                    # 检查装弹状态（针对子弹武器）
                    if hasattr(weapon, 'is_reloading') and weapon.is_reloading:
                        is_reloading = True
                        if hasattr(weapon, 'reload_timer') and hasattr(weapon, 'reload_duration'):
                            reload_progress = weapon.reload_timer / weapon.reload_duration
                    
                    # 计算当前子弹和总子弹数（针对子弹武器）
                    if hasattr(weapon, 'type') and weapon.type == 'bullet':
                        if hasattr(weapon, 'shots_before_reload') and hasattr(weapon, 'shots_fired'):
                            current_bullets = weapon.shots_before_reload - weapon.shots_fired
                            total_bullets = weapon.ammo
                        else:
                            current_bullets = total_ammo
                            total_bullets = max_ammo
                    else:
                        # 非子弹武器使用默认显示
                        current_bullets = total_ammo
                        total_bullets = max_ammo
        
        # 如果没有远程武器，不显示弹药UI
        if not has_ranged_weapon:
            return
        
        # 显示弹药文本
        if is_reloading:
            ammo_text = f"装弹中... {reload_progress:.1%}"
            text_color = (255, 255, 0)  # 黄色表示装弹中
        else:
            # 显示当前子弹/总子弹格式
            ammo_text = f"子弹: {current_bullets}/{total_bullets}"
            text_color = (255, 255, 255)  # 白色表示正常
        
        # 渲染弹药文本
        ammo_surface = self.font.render(ammo_text, True, text_color)
        ammo_rect = ammo_surface.get_rect()
        
        # 计算右侧位置
        margin = 20
        x = self.screen.get_width() - margin - ammo_rect.width
        y = self.screen.get_height() // 2 - 50  # 屏幕中央偏上
        
        # 添加背景
        bg_rect = pygame.Rect(x - 10, y - 5, ammo_rect.width + 20, ammo_rect.height + 10)
        bg_surface = pygame.Surface((bg_rect.width, bg_rect.height))
        bg_surface.set_alpha(150)
        bg_surface.fill((0, 0, 0))
        self.screen.blit(bg_surface, bg_rect)
        
        # 渲染文本
        ammo_rect.topleft = (x, y)
        self.screen.blit(ammo_surface, ammo_rect)

    def _render_teleport_info(self, player):
        """渲染传送道具信息
        
        Args:
            player: 玩家实例
        """
        # 检查玩家是否有传送道具属性
        if not hasattr(player, 'teleport_items'):
            return
            
        # 获取传送道具数量
        teleport_count = player.teleport_items
        
        # 显示传送道具文本
        teleport_text = f"传送道具: {teleport_count}"
        
        # 根据数量设置颜色
        if teleport_count > 0:
            text_color = (0, 255, 255)  # 青色表示有传送道具
        else:
            text_color = (128, 128, 128)  # 灰色表示没有传送道具
        
        # 渲染传送道具文本
        teleport_surface = self.font.render(teleport_text, True, text_color)
        teleport_rect = teleport_surface.get_rect()
        
        # 计算屏幕正中间位置
        screen_center_x = self.screen.get_width() -100
        screen_center_y = self.screen.get_height() // 2
        
        # 添加背景（居中显示）
        bg_rect = pygame.Rect(screen_center_x - teleport_rect.width // 2 - 10, 
                             screen_center_y - teleport_rect.height // 2 - 5,
                             teleport_rect.width + 20, teleport_rect.height + 10)
        bg_surface = pygame.Surface((bg_rect.width, bg_rect.height))
        bg_surface.set_alpha(200)  # 更不透明的背景
        bg_surface.fill((0, 0, 0))
        self.screen.blit(bg_surface, bg_rect)
        
        # 渲染图标（放在文字左边）
        if self.teleport_icon:
            icon_rect = self.teleport_icon.get_rect()
            icon_rect.right = teleport_rect.left - 10  # 图标在文字左边10像素
            icon_rect.centery = teleport_rect.centery  # 垂直居中对齐
            self.screen.blit(self.teleport_icon, icon_rect)
            
            # print("传送道具图标为空，无法渲染")
            # 绘制一个简单的测试图标
            test_icon = pygame.Surface((73, 64), pygame.SRCALPHA)
            pygame.draw.circle(test_icon, (255, 0, 0), (36, 32), 30)  # 红色圆圈
            test_rect = test_icon.get_rect()
            test_rect.right = teleport_rect.left - 10
            test_rect.centery = teleport_rect.centery
            self.screen.blit(test_icon, test_rect)
            # print("使用测试图标")
        
        # 渲染文本（居中显示）
        teleport_rect.center = (screen_center_x, screen_center_y)
        self.screen.blit(teleport_surface, teleport_rect)

    def _render_difficulty_level(self, enemy_manager):
        """渲染难度等级信息
        
        Args:
            enemy_manager: 敌人管理器实例
        """
        if not enemy_manager or not hasattr(enemy_manager, 'difficulty_level'):
            return
            
        # 获取难度等级
        difficulty_level = enemy_manager.difficulty_level
        
        # 渲染难度等级文本
        difficulty_text = f"难度等级: {difficulty_level}"
        difficulty_surface = self.font.render(difficulty_text, True, (255, 165, 0))  # 橙色
        difficulty_rect = difficulty_surface.get_rect()
        
        # 位置：左上角，在游戏时间下方
        difficulty_rect.topleft = (10, 480)  # 在时间显示下方
        
        # 添加背景
        bg_rect = pygame.Rect(difficulty_rect.left - 5, difficulty_rect.top - 2, 
                             difficulty_rect.width + 10, difficulty_rect.height + 4)
        bg_surface = pygame.Surface((bg_rect.width, bg_rect.height))
        bg_surface.set_alpha(128)
        bg_surface.fill((0, 0, 0))
        self.screen.blit(bg_surface, bg_rect)
        
        # 渲染难度等级文本
        self.screen.blit(difficulty_surface, difficulty_rect)

    def _render_flashlight_mode(self, dual_player_system):
        """渲染手电筒模式显示
        
        Args:
            dual_player_system: 双人系统实例
        """
        if not dual_player_system:
            return
            
        # 获取当前光照模式
        current_mode = dual_player_system.light_modes[dual_player_system.light_mode]
        
        # 模式名称映射（中文）
        mode_name_map = {
            "default": "默认模式",
            "battle": "战斗模式", 
            "explore": "探索模式",
            "low_energy": "充能模式"
        }
        mode_name = mode_name_map.get(current_mode['name'], current_mode['name'])
        
        # 渲染模式文本
        mode_text = f"手电筒: {mode_name}"
        mode_surface = self.font.render(mode_text, True, (0, 255, 255))  # 青色
        mode_rect = mode_surface.get_rect()
        
        # 计算位置：左侧，电量下方
        margin = 20
        x = margin
        # 计算电量显示的位置，然后在其下方显示手电筒模式
        coin_text_rect = self.font.render("0", True, (255, 255, 255)).get_rect()  # 临时获取文本高度
        energy_y = coin_text_rect.bottom + 5 + 210 + coin_text_rect.height + 10  # 电量显示位置
        y = energy_y + 430  # 电量下方30像素
        
        # 添加背景
        bg_rect = pygame.Rect(x - 5, y - 2, mode_rect.width + 10, mode_rect.height + 4)
        bg_surface = pygame.Surface((bg_rect.width, bg_rect.height))
        bg_surface.set_alpha(150)
        bg_surface.fill((0, 0, 0))
        self.screen.blit(bg_surface, bg_rect)
        
        # 渲染文本
        mode_rect.topleft = (x, y)
        self.screen.blit(mode_surface, mode_rect)

    def render(self, player, game_time, game_kill_num, dual_player_system=None, enemy_manager=None):
        screen_width = self.screen.get_width()
        screen_height = self.screen.get_height()
        
        # 在双人模式下，使用忍者蛙作为主要角色显示基础UI
        if dual_player_system:
            primary_player = dual_player_system.ninja_frog
            weapon_player = dual_player_system.mystic_swordsman
        else:
            primary_player = player
            weapon_player = player
        
        # 绘制经验条背景（顶部，向下移动100像素）
        exp_bar_y = 100
        pygame.draw.rect(self.screen, self.exp_back_color,
                        (0, exp_bar_y, screen_width, self.bar_height))
        
        # 绘制经验条
        exp_width = (primary_player.experience / primary_player.exp_to_next_level) * screen_width
        pygame.draw.rect(self.screen, self.exp_bar_color,
                        (0, exp_bar_y, exp_width, self.bar_height))
        
        # 渲染等级文本（嵌入在经验条中间，中文）
        level_text = f"等级 {primary_player.level}"
        
        # 创建文本对象以获取尺寸
        text = self.font.render(level_text, True, self.text_color)
        text_rect = text.get_rect()
        text_rect.centerx = screen_width // 2
        text_rect.centery = exp_bar_y + self.bar_height // 2
        
        # 渲染文本阴影（略微偏移）
        shadow_text = self.font.render(level_text, True, (0, 0, 0))
        shadow_rect = shadow_text.get_rect()
        shadow_rect.centerx = screen_width // 2 + 2
        shadow_rect.centery = exp_bar_y + self.bar_height // 2 + 2
        self.screen.blit(shadow_text, shadow_rect)
        
        # 渲染主文本
        self.screen.blit(text, text_rect)
        
        # 渲染心形血量显示
        self._render_heart_health(primary_player, screen_width, screen_height)
        
        # 显示弹药数量（在右上角）
        self._render_ammo_info(weapon_player)
        
        # 显示钥匙数量（在左上角）
        self._render_key_info(primary_player, game_time)
        
        # 显示武器模式（仅对神秘剑士）
        self._render_weapon_mode(weapon_player)
        
        # 显示武器选择UI
        self._render_weapon_selection_ui(weapon_player)
        
        # 在双人模式下，在左侧显示弹药信息
        if dual_player_system:
            self._render_ammo_display_left(weapon_player)
            # 显示传送道具数量
            self._render_teleport_info(primary_player)
            # 渲染手电筒模式
            self._render_flashlight_mode(dual_player_system)
        else:
            # 单人模式下也显示传送道具数量
            self._render_teleport_info(player)
        
        # 计算技能图标框的总宽度（每排3个）
        total_icons_width = 3 * (self.icon_size + self.icon_spacing) - self.icon_spacing
        start_x = (screen_width - total_icons_width) // 2
        
        # 计算心形血条位置作为参考
        heart_y = screen_height - 100 - 40  # 与_render_heart_health中的位置保持一致
        
        # 武器图标位于上排（相对于心形血条位置调整）
        weapon_y = heart_y - (self.icon_size + self.icon_spacing) * 2 - 5
        # 被动图标位于下排（相对于心形血条位置调整）
        passive_y = heart_y - self.icon_size - 5
        
        # 绘制3个武器图标框（上排）
        for i in range(3):
            icon_x = start_x + i * (self.icon_size + self.icon_spacing)
            icon_rect = pygame.Rect(icon_x, weapon_y, self.icon_size, self.icon_size)
            
            # 绘制半透明背景
            s = pygame.Surface((self.icon_size, self.icon_size))
            s.set_alpha(128)
            s.fill((50, 50, 50))
            self.screen.blit(s, icon_rect)
            
            # 绘制边框
            pygame.draw.rect(self.screen, (100, 100, 100), icon_rect, 1)
            
            # 如果有对应的武器，绘制其图标
            if i < len(weapon_player.weapons):
                weapon = weapon_player.weapons[i]
                weapon_type = weapon.type
                weapon_level = weapon_player.weapon_levels.get(weapon_type, 1)
                if weapon_type in self.upgrade_manager.weapon_upgrades:
                    upgrade = self.upgrade_manager.weapon_upgrades[weapon_type]
                    if weapon_level <= len(upgrade.levels):
                        icon = upgrade.levels[weapon_level - 1].icon
                        if icon:
                            # 缩放图标到合适大小
                            scaled_icon = pygame.transform.scale(icon, (self.icon_size, self.icon_size))
                            self.screen.blit(scaled_icon, icon_rect)
                            
        # 绘制3个被动技能图标框（下排）
        for i in range(3):
            icon_x = start_x + i * (self.icon_size + self.icon_spacing)
            icon_rect = pygame.Rect(icon_x, passive_y, self.icon_size, self.icon_size)
            
            # 绘制半透明背景
            s = pygame.Surface((self.icon_size, self.icon_size))
            s.set_alpha(128)
            s.fill((50, 50, 50))
            self.screen.blit(s, icon_rect)
            
            # 绘制边框
            pygame.draw.rect(self.screen, (100, 100, 100), icon_rect, 1)
            
            # 如果有对应的被动技能，绘制其图标
            if i < len(primary_player.passives):
                passive_type = list(primary_player.passives.keys())[i]
                passive_level = primary_player.passive_levels.get(passive_type, 1)
                if passive_type in self.upgrade_manager.passive_upgrades:
                    upgrade = self.upgrade_manager.passive_upgrades[passive_type]
                    if passive_level <= len(upgrade.levels):
                        icon = upgrade.levels[passive_level - 1].icon
                        if icon:
                            # 缩放图标到合适大小
                            scaled_icon = pygame.transform.scale(icon, (self.icon_size, self.icon_size))
                            self.screen.blit(scaled_icon, icon_rect)
        
        # 渲染游戏时间（左上角，紧贴经验条下方）
        minutes = int(game_time // 60)
        seconds = int(game_time % 60)
        time_text = self.small_font.render(f"{minutes:02d}:{seconds:02d}", True, self.text_color)
        time_rect = time_text.get_rect()
        time_rect.left = self.margin
        time_rect.top = self.bar_height + self.margin+200
        self.screen.blit(time_text, time_rect)
        
        # 渲染击杀统计（左上角，紧贴经验条下方）
        kill_count = game_kill_num

        kill_text = self.font.render(f"击杀: {kill_count}", True, self.text_color)
        kill_text_rect = kill_text.get_rect()
        kill_icon_rect = self.kill_icon.get_rect()
        
        # 计算击杀统计文本和图标的位置（左上角，往下移动400像素）
        kill_icon_rect.left = self.margin+900
        kill_icon_rect.top = self.bar_height + self.margin + 30 + 80  # 在时间下方，再往下400像素
        kill_text_rect.left = kill_icon_rect.right + 5
        kill_text_rect.centery = kill_icon_rect.centery
        

        
        # 渲染击杀统计文本和图标
        self.screen.blit(self.kill_icon, kill_icon_rect)
        self.screen.blit(kill_text, kill_text_rect)
        
        # 渲染金币数量和图标（右上角，紧贴经验条下方）
        coin_text = self.font.render(str(primary_player.coins), True, self.coin_color)
        coin_text_rect = coin_text.get_rect()
        coin_icon_rect = self.coin_icon.get_rect()
        
        # 计算金币文本和图标的位置（往下移动400像素，往左移动500像素）
        coin_text_rect.right = screen_width - self.margin - coin_icon_rect.width - 5 - 10  # 往左移动500像素
        coin_text_rect.top = self.bar_height + self.margin + 400  # 往下移动400像素
        coin_icon_rect.right = coin_text_rect.left - 5
        coin_icon_rect.centery = coin_text_rect.centery
        

        
        # 渲染金币文本和图标
        self.screen.blit(coin_text, coin_text_rect)
        self.screen.blit(self.coin_icon, coin_icon_rect)
        
        # 渲染剩余电量（右上角，金币下方）
        if dual_player_system:
    
            
            # 根据电量值确定颜色
            energy_value = dual_player_system.energy
            if energy_value < 20:
                energy_color = (255, 0, 0)  # 红色 (<20)
            elif energy_value < 50:
                energy_color = (255, 255, 0)  # 黄色 (<50)
            else:
                energy_color = (0, 255, 0)  # 绿色 (>=50)
            
            # 渲染电量图标和文本
            energy_text = self.font.render(f"电量: {int(energy_value)}%", True, energy_color)
            energy_rect = energy_text.get_rect()
            energy_icon_rect = self.energy_icon.get_rect()
            
            # 计算位置（图标在文本左侧）
            energy_icon_rect.right = self.margin + energy_icon_rect.width
            energy_rect.right = self.margin + energy_rect.width + energy_icon_rect.width + 5  # 往左移动400像素
            energy_rect.top = coin_text_rect.bottom + 5 + 210  # 往下移动300像素
            energy_icon_rect.centery = energy_rect.centery
            
            # 渲染电量图标和文本
            self.screen.blit(self.energy_icon, energy_icon_rect)
            self.screen.blit(energy_text, energy_rect)
    
        # 渲染难度等级信息
        self._render_difficulty_level(enemy_manager)
        
        # 渲染FPS显示
        self._render_fps()

    def _render_heart_health(self, player, screen_width, screen_height):
        """渲染心形血量显示
        
        Args:
            player: 玩家实例
            screen_width: 屏幕宽度
            screen_height: 屏幕高度
        """
        # 计算心形图标的显示位置（底部上方100像素）
        heart_y = screen_height - 100 - 40  # 40是心形图标的高度
        
        # 计算需要显示的心形数量
        max_hearts = int(player.max_health // 10)  # 每10点血量1个心形
        current_health = player.health
        
        # 心形图标尺寸和间距
        heart_size = 32
        heart_spacing = 5
        total_width = max_hearts * heart_size + (max_hearts - 1) * heart_spacing
        start_x = (screen_width - total_width) // 2  # 居中显示
        
        # 渲染每个心形
        for i in range(max_hearts):
            heart_x = start_x + i * (heart_size + heart_spacing)
            
            # 计算这个心形对应的血量范围
            heart_min_health = i * 10
            heart_max_health = (i + 1) * 10
            
            # 创建心形图标副本用于处理
            heart_surface = self.heart_icon.copy()
            
            if current_health <= heart_min_health:
                # 完全没血，显示灰色心形
                heart_surface.fill((50, 50, 50), special_flags=pygame.BLEND_RGB_MULT)
            elif current_health >= heart_max_health:
                # 满血，显示红色心形（保持原色）
                pass
            else:
                # 部分血量，按百分比置灰
                remaining_health = current_health - heart_min_health
                health_percentage = remaining_health / 10.0
                
                # 创建遮罩，从右到左置灰
                mask_width = int(heart_size * (1.0 - health_percentage))
                if mask_width > 0:
                    # 创建灰色遮罩
                    gray_overlay = pygame.Surface((mask_width, heart_size), pygame.SRCALPHA)
                    gray_overlay.fill((40, 40, 40, 255))  # 更深的灰色，完全不透明
                    
                    # 应用遮罩到心形的右侧
                    heart_surface.blit(gray_overlay, (heart_size - mask_width, 0), special_flags=pygame.BLEND_RGB_MULT)
            
            # 渲染心形图标
            self.screen.blit(heart_surface, (heart_x, heart_y))
        
        # 显示血量数值（在心形下方）
        health_text = f"{int(current_health)}/{int(player.max_health)}"
        health_text_surface = self.font.render(health_text, True, (255, 255, 255))
        health_text_rect = health_text_surface.get_rect()
        health_text_rect.centerx = screen_width // 2
        health_text_rect.top = heart_y + heart_size + 5
        
        # 渲染文字阴影
        shadow_surface = self.font.render(health_text, True, (0, 0, 0))
        shadow_rect = shadow_surface.get_rect()
        shadow_rect.centerx = screen_width // 2 + 2
        shadow_rect.top = health_text_rect.top + 2
        self.screen.blit(shadow_surface, shadow_rect)
        
        # 渲染主文字
        self.screen.blit(health_text_surface, health_text_rect)
        
        # 在左边显示血量比值
        health_ratio_text = f"血量：{int(current_health)}/{int(player.max_health)}"
        
        # 根据血量百分比选择颜色
        health_percentage = current_health / player.max_health
        if health_percentage > 0.8:
            ratio_color = (0, 255, 0)  # 绿色 (>80%)
        elif health_percentage > 0.5:
            ratio_color = (255, 255, 0)  # 黄色 (>50%)
        elif health_percentage > 0.2:
            ratio_color = (255, 165, 0)  # 橙色 (>20%)
        else:
            ratio_color = (255, 0, 0)  # 红色 (<=20%)
        
        # 渲染血量比值文本
        ratio_surface = self.font.render(health_ratio_text, True, ratio_color)
        ratio_rect = ratio_surface.get_rect()
        
        # 位置：左侧，与心形垂直居中对齐
        ratio_rect.left = 20  # 距离左边缘20像素
        ratio_rect.centery = heart_y + heart_size // 2  # 与心形中心对齐
        
        # 添加背景
        bg_rect = pygame.Rect(ratio_rect.left - 5, ratio_rect.top - 2, 
                             ratio_rect.width + 10, ratio_rect.height + 4)
        bg_surface = pygame.Surface((bg_rect.width, bg_rect.height))
        bg_surface.set_alpha(150)
        bg_surface.fill((0, 0, 0))
        self.screen.blit(bg_surface, bg_rect)
        
        # 渲染血量比值文字阴影
        ratio_shadow_surface = self.font.render(health_ratio_text, True, (0, 0, 0))
        ratio_shadow_rect = ratio_shadow_surface.get_rect()
        ratio_shadow_rect.left = ratio_rect.left + 2
        ratio_shadow_rect.top = ratio_rect.top + 2
        self.screen.blit(ratio_shadow_surface, ratio_shadow_rect)
        
        # 渲染血量比值主文字
        self.screen.blit(ratio_surface, ratio_rect) 
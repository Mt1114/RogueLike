import pygame
from .utils import FontManager
from .resource_manager import resource_manager
from .upgrade_system import UpgradeManager

class UI:
    def __init__(self, screen):
        self.screen = screen
        pygame.font.init()
        self.font = pygame.font.SysFont('simHei', 24)
        self.small_font = pygame.font.SysFont('simHei', 20)  # 较小的字体用于时间显示
        
        # UI颜色
        self.exp_bar_color = (0, 255, 255)    # 青色
        self.exp_back_color = (0, 100, 100)   # 深青色
        self.health_bar_color = (255, 0, 0)   # 红色
        self.health_back_color = (100, 0, 0)  # 深红色
        self.text_color = (255, 255, 255)     # 白色
        self.coin_color = (255, 215, 0)       # 金色
        
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
        
    def _render_key_info(self, player):
        """渲染钥匙信息
        
        Args:
            player: 玩家实例
        """
        # 检查玩家是否有钥匙系统
        if not hasattr(player, 'keys_collected') or not hasattr(player, 'total_keys_needed'):
            return
            
        key_text = f"钥匙: {player.keys_collected}/{player.total_keys_needed}"
        
        # 渲染钥匙文本
        key_surface = self.font.render(key_text, True, (255, 255, 0))  # 黄色
        key_rect = key_surface.get_rect()
        
        # 计算左上角位置
        key_rect.topleft = (10, 10)
        
        # 添加背景
        bg_rect = pygame.Rect(key_rect.left - 5, key_rect.top - 2, 
                             key_rect.width + 10, key_rect.height + 4)
        bg_surface = pygame.Surface((bg_rect.width, bg_rect.height))
        bg_surface.set_alpha(128)
        bg_surface.fill((0, 0, 0))
        self.screen.blit(bg_surface, bg_rect)
        
        # 渲染文本
        self.screen.blit(key_surface, key_rect)
    
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
        
        # 计算血条位置
        health_bar_y = screen_height - self.bar_height - 100
        
        # 武器选择UI位置：血条正上方160像素
        weapon_ui_y = health_bar_y - 160
        
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
        
        # 计算左侧位置
        margin = 20
        x = margin
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

    def render(self, player, game_time, game_kill_num, dual_player_system=None):
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
        
        # 绘制生命槽背景（底部，向上移动100像素）
        health_bar_y = screen_height - self.bar_height - 100
        pygame.draw.rect(self.screen, self.health_back_color,
                        (0, health_bar_y, screen_width, self.bar_height))
        
        # 绘制生命槽
        health_width = (primary_player.health / primary_player.max_health) * screen_width
        pygame.draw.rect(self.screen, self.health_bar_color,
                        (0, health_bar_y, health_width, self.bar_height))
        
        # 显示弹药数量（在右上角）
        self._render_ammo_info(weapon_player)
        
        # 显示钥匙数量（在左上角）
        self._render_key_info(primary_player)
        
        # 显示武器模式（仅对神秘剑士）
        self._render_weapon_mode(weapon_player)
        
        # 显示武器选择UI
        self._render_weapon_selection_ui(weapon_player)
        
        # 在双人模式下，在左侧显示弹药信息
        if dual_player_system:
            self._render_ammo_display_left(weapon_player)
        
        # 计算技能图标框的总宽度（每排3个）
        total_icons_width = 3 * (self.icon_size + self.icon_spacing) - self.icon_spacing
        start_x = (screen_width - total_icons_width) // 2
        
        # 武器图标位于上排（相对于新的血条位置调整）
        weapon_y = health_bar_y - (self.icon_size + self.icon_spacing) * 2 - 5
        # 被动图标位于下排（相对于新的血条位置调整）
        passive_y = health_bar_y - self.icon_size - 5
        
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
        print(f"UI渲染 - 击杀数: {kill_count}, 双人系统: {dual_player_system is not None}")  # 调试信息
        kill_text = self.font.render(f"击杀: {kill_count}", True, self.text_color)
        kill_text_rect = kill_text.get_rect()
        kill_icon_rect = self.kill_icon.get_rect()
        
        # 计算击杀统计文本和图标的位置（左上角，往下移动400像素）
        kill_icon_rect.left = self.margin+900
        kill_icon_rect.top = self.bar_height + self.margin + 30 + 80  # 在时间下方，再往下400像素
        kill_text_rect.left = kill_icon_rect.right + 5
        kill_text_rect.centery = kill_icon_rect.centery
        
        print(f"击杀图标位置: ({kill_icon_rect.left}, {kill_icon_rect.top})")  # 调试位置信息
        
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
        
        print(f"金币位置: ({coin_text_rect.right}, {coin_text_rect.top})")  # 调试位置信息
        
        # 渲染金币文本和图标
        self.screen.blit(coin_text, coin_text_rect)
        self.screen.blit(self.coin_icon, coin_icon_rect)
        
        # 渲染剩余电量（右上角，金币下方）
        if dual_player_system:
            print(f"UI渲染 - 电量: {dual_player_system.energy}%")  # 调试信息
            
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
            energy_rect.right = screen_width - self.margin - 10  # 往左移动400像素
            energy_rect.top = coin_text_rect.bottom + 5 + 250  # 往下移动300像素
            energy_icon_rect.right = energy_rect.left - 5
            energy_icon_rect.centery = energy_rect.centery
            
            print(f"电量位置: ({energy_rect.right}, {energy_rect.top})")  # 调试位置信息
            print(f"电量图标位置: ({energy_icon_rect.right}, {energy_icon_rect.centery})")  # 调试位置信息
            
            # 渲染电量图标和文本
            self.screen.blit(self.energy_icon, energy_icon_rect)
            self.screen.blit(energy_text, energy_rect) 
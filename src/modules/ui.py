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
        
        # 统计所有远程武器的弹药
        if hasattr(player, 'weapon_manager'):
            for weapon in player.weapon_manager.weapons:
                if hasattr(weapon, 'ammo') and not weapon.is_melee:
                    has_ranged_weapon = True
                    total_ammo += weapon.ammo
        
        # 如果没有远程武器，不显示弹药UI
        if not has_ranged_weapon:
            return
        
        ammo_text = f"弹药: {total_ammo}"
        
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
        
    def render(self, player, game_time, game_kill_num):
        screen_width = self.screen.get_width()
        screen_height = self.screen.get_height()
        
        # 绘制经验条背景（顶部）
        pygame.draw.rect(self.screen, self.exp_back_color,
                        (0, 0, screen_width, self.bar_height))
        
        # 绘制经验条
        exp_width = (player.experience / player.exp_to_next_level) * screen_width
        pygame.draw.rect(self.screen, self.exp_bar_color,
                        (0, 0, exp_width, self.bar_height))
        
        # 渲染等级文本（嵌入在经验条中间，中文）
        level_text = f"等级 {player.level}"
        
        # 创建文本对象以获取尺寸
        text = self.font.render(level_text, True, self.text_color)
        text_rect = text.get_rect()
        text_rect.centerx = screen_width // 2
        text_rect.centery = self.bar_height // 2
        
        # 渲染文本阴影（略微偏移）
        shadow_text = self.font.render(level_text, True, (0, 0, 0))
        shadow_rect = shadow_text.get_rect()
        shadow_rect.centerx = screen_width // 2 + 2
        shadow_rect.centery = self.bar_height // 2 + 2
        self.screen.blit(shadow_text, shadow_rect)
        
        # 渲染主文本
        self.screen.blit(text, text_rect)
        
        # 绘制生命槽背景（底部）
        pygame.draw.rect(self.screen, self.health_back_color,
                        (0, screen_height - self.bar_height, screen_width, self.bar_height))
        
        # 绘制生命槽
        health_width = (player.health / player.max_health) * screen_width
        pygame.draw.rect(self.screen, self.health_bar_color,
                        (0, screen_height - self.bar_height, health_width, self.bar_height))
        
        # 显示弹药数量（在右上角）
        self._render_ammo_info(player)
        
        # 显示钥匙数量（在左上角）
        self._render_key_info(player)
        
        # 显示武器模式（仅对神秘剑士）
        self._render_weapon_mode(player)
        
        # 计算技能图标框的总宽度（每排3个）
        total_icons_width = 3 * (self.icon_size + self.icon_spacing) - self.icon_spacing
        start_x = (screen_width - total_icons_width) // 2
        
        # 武器图标位于上排
        weapon_y = screen_height - self.bar_height - (self.icon_size + self.icon_spacing) * 2 - 5
        # 被动图标位于下排
        passive_y = screen_height - self.bar_height - self.icon_size - 5
        
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
            if i < len(player.weapons):
                weapon = player.weapons[i]
                weapon_type = weapon.type
                weapon_level = player.weapon_levels.get(weapon_type, 1)
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
            if i < len(player.passives):
                passive_type = list(player.passives.keys())[i]
                passive_level = player.passive_levels.get(passive_type, 1)
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
        time_rect.top = self.bar_height + self.margin
        self.screen.blit(time_text, time_rect)
        
        # 渲染击杀统计（中间，紧贴经验条下方）
        kill_count = game_kill_num
        kill_text = self.font.render(str(kill_count), True, self.text_color)
        kill_text_rect = kill_text.get_rect()
        kill_icon_rect = self.kill_icon.get_rect()
        
        # 计算击杀统计文本和图标的位置（居中）
        total_width = kill_icon_rect.width + 5 + kill_text_rect.width
        center_x = screen_width // 2
        kill_icon_rect.right = center_x - 5
        kill_icon_rect.top = self.bar_height + self.margin
        kill_text_rect.left = center_x + 5
        kill_text_rect.centery = kill_icon_rect.centery
        
        # 渲染击杀统计文本和图标
        self.screen.blit(self.kill_icon, kill_icon_rect)
        self.screen.blit(kill_text, kill_text_rect)
        
        # 渲染金币数量和图标（右上角，紧贴经验条下方）
        coin_text = self.font.render(str(player.coins), True, self.coin_color)
        coin_text_rect = coin_text.get_rect()
        coin_icon_rect = self.coin_icon.get_rect()
        
        # 计算金币文本和图标的位置
        coin_text_rect.right = screen_width - self.margin - coin_icon_rect.width - 5
        coin_text_rect.top = self.bar_height + self.margin
        coin_icon_rect.right = coin_text_rect.left - 5
        coin_icon_rect.centery = coin_text_rect.centery
        
        # 渲染金币文本和图标
        self.screen.blit(coin_text, coin_text_rect)
        self.screen.blit(self.coin_icon, coin_icon_rect) 
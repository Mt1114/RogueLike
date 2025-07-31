import pygame

class Minimap:
    def __init__(self, map_width, map_height, screen_width, screen_height):
        """创建小地图
        
        Args:
            map_width: 地图宽度
            map_height: 地图高度
            screen_width: 屏幕宽度
            screen_height: 屏幕高度
        """
        self.map_width = map_width
        self.map_height = map_height
        
        # 小地图尺寸和位置
        self.minimap_width = 200
        self.minimap_height = 150
        self.minimap_x = screen_width - self.minimap_width - 20  # 右上角
        self.minimap_y = 20
        
        # 缩放比例
        self.scale_x = self.minimap_width / map_width
        self.scale_y = self.minimap_height / map_height
        
        # 创建小地图表面
        self.surface = pygame.Surface((self.minimap_width, self.minimap_height))
        self.surface.set_alpha(180)  # 半透明
        
        # 颜色定义
        self.background_color = (0, 0, 0, 100)  # 黑色背景
        self.border_color = (255, 255, 255)     # 白色边框
        self.player_color = (0, 255, 0)         # 绿色玩家
        self.key_color = (255, 255, 0)          # 黄色钥匙
        self.door_color = (255, 0, 0)           # 红色逃生门
        self.ammo_supply_color = (0, 255, 255)  # 青色弹药补给
        self.health_supply_color = (255, 0, 255) # 紫色生命补给
        
        # 标记大小
        self.marker_size = 4
        
    def world_to_minimap(self, world_x, world_y):
        """将世界坐标转换为小地图坐标"""
        minimap_x = int(world_x * self.scale_x)
        minimap_y = int(world_y * self.scale_y)
        return minimap_x, minimap_y
    
    def draw_marker(self, x, y, color, size=None):
        """在小地图上绘制标记"""
        if size is None:
            size = self.marker_size
        
        # 确保标记在小地图范围内
        x = max(size, min(x, self.minimap_width - size))
        y = max(size, min(y, self.minimap_height - size))
        
        # 绘制标记
        pygame.draw.circle(self.surface, color, (x, y), size)
        
        # 添加边框
        pygame.draw.circle(self.surface, (255, 255, 255), (x, y), size, 1)
    
    def render(self, screen, player, key_item, escape_door, ammo_supplies=None, health_supplies=None):
        """渲染小地图
        
        Args:
            screen: 游戏屏幕
            player: 玩家对象
            key_item: 钥匙物品对象
            escape_door: 逃生门对象
            ammo_supplies: 弹药补给物品列表
            health_supplies: 生命补给物品列表
        """
        # 清空小地图表面
        self.surface.fill((0, 0, 0))
        
        # 绘制边框
        pygame.draw.rect(self.surface, self.border_color, 
                        (0, 0, self.minimap_width, self.minimap_height), 2)
        
        # 绘制玩家位置
        if player:
            player_x, player_y = self.world_to_minimap(player.world_x, player.world_y)
            self.draw_marker(player_x, player_y, self.player_color, 5)
        
        # 绘制钥匙位置
        if key_item and hasattr(key_item, 'world_x') and hasattr(key_item, 'world_y'):
            key_x, key_y = self.world_to_minimap(key_item.world_x, key_item.world_y)
            self.draw_marker(key_x, key_y, self.key_color, 4)
        
        # 绘制逃生门位置
        if escape_door and hasattr(escape_door, 'world_x') and hasattr(escape_door, 'world_y'):
            door_x, door_y = self.world_to_minimap(escape_door.world_x, escape_door.world_y)
            self.draw_marker(door_x, door_y, self.door_color, 6)
        
        # 绘制弹药补给位置
        if ammo_supplies:
            for supply in ammo_supplies:
                if hasattr(supply, 'world_x') and hasattr(supply, 'world_y'):
                    supply_x, supply_y = self.world_to_minimap(supply.world_x, supply.world_y)
                    self.draw_marker(supply_x, supply_y, self.ammo_supply_color, 3)
        
        # 绘制生命补给位置
        if health_supplies:
            for supply in health_supplies:
                if hasattr(supply, 'world_x') and hasattr(supply, 'world_y'):
                    supply_x, supply_y = self.world_to_minimap(supply.world_x, supply.world_y)
                    self.draw_marker(supply_x, supply_y, self.health_supply_color, 3)
        
        # 将小地图绘制到屏幕上
        screen.blit(self.surface, (self.minimap_x, self.minimap_y))
        
        # 绘制小地图标题
        font = pygame.font.Font(None, 24)
        title_text = font.render("map", True, (255, 255, 255))
        title_rect = title_text.get_rect()
        title_rect.centerx = self.minimap_x + self.minimap_width // 2
        title_rect.y = self.minimap_y - 25
        screen.blit(title_text, title_rect)
        
        # 绘制图例
        legend_y = self.minimap_y + self.minimap_height + 5
        legend_x = self.minimap_x
        
        # 使用更小的字体
        legend_font = pygame.font.Font(None, 16)  # 从24改为16
        
        # 玩家图例
        pygame.draw.circle(screen, self.player_color, (legend_x + 10, legend_y + 8), 3)
        player_text = legend_font.render("player", True, (255, 255, 255))
        screen.blit(player_text, (legend_x + 20, legend_y))
        
        # 钥匙图例
        pygame.draw.circle(screen, self.key_color, (legend_x + 60, legend_y + 8), 3)
        key_text = legend_font.render("key", True, (255, 255, 255))
        screen.blit(key_text, (legend_x + 70, legend_y))
        
        # 逃生门图例
        pygame.draw.circle(screen, self.door_color, (legend_x + 110, legend_y + 8), 3)
        door_text = legend_font.render("door", True, (255, 255, 255))
        screen.blit(door_text, (legend_x + 120, legend_y))
        
        # 弹药补给图例
        pygame.draw.circle(screen, self.ammo_supply_color, (legend_x + 160, legend_y + 8), 3)
        ammo_text = legend_font.render("ammo", True, (255, 255, 255))
        screen.blit(ammo_text, (legend_x + 170, legend_y)) 
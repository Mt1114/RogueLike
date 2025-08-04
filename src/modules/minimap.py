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
        
        # 小地图尺寸和位置（调整以避免遮挡）
        self.minimap_width = 180  # 稍微增加宽度以容纳图例
        self.minimap_height = 120  # 保持高度
        self.minimap_x = screen_width - self.minimap_width - 60  # 右上角，增加更多右边距
        self.minimap_y = 50  # 距离顶部50像素，避免与其他UI重叠
        
        # 缩放比例
        self.scale_x = self.minimap_width / map_width
        self.scale_y = self.minimap_height / map_height
        
        # 创建小地图表面
        self.surface = pygame.Surface((self.minimap_width, self.minimap_height))
        self.surface.set_alpha(180)  # 半透明
        
        # 颜色定义
        self.background_color = (0, 0, 0, 100)  # 黑色背景
        self.border_color = (255, 255, 255)     # 白色边框
        self.player_color = (0, 255, 0)         # 绿色玩家（忍者蛙）
        self.mystic_color = (0, 200, 0)         # 深绿色神秘剑客
        self.key_color = (255, 255, 0)          # 黄色钥匙
        self.door_color = (255, 0, 0)           # 红色逃生门
        self.ammo_supply_color = (0, 255, 255)  # 青色弹药补给
        self.health_supply_color = (255, 0, 255) # 紫色生命补给
        self.teleport_color = (0, 100, 255)     # 蓝色传送道具
        self.wall_color = (128, 128, 128)       # 灰色墙壁/碰撞地形
        
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
    
    def draw_triangle_marker(self, x, y, color, size=None):
        """在小地图上绘制三角形标记
        
        Args:
            x, y: 小地图坐标
            color: 三角形颜色
            size: 三角形大小
        """
        if size is None:
            size = 6
        
        # 确保标记在小地图范围内
        x = max(size, min(x, self.minimap_width - size))
        y = max(size, min(y, self.minimap_height - size))
        
        # 计算三角形的三个顶点
        points = [
            (x, y - size),  # 顶点
            (x - size//2, y + size//2),  # 左下角
            (x + size//2, y + size//2)   # 右下角
        ]
        
        # 绘制三角形
        pygame.draw.polygon(self.surface, color, points)
        
        # 添加边框
        pygame.draw.polygon(self.surface, (255, 255, 255), points, 1)
    
    def draw_wall(self, rect):
        """在小地图上绘制墙壁/碰撞地形
        
        Args:
            rect: pygame.Rect对象，表示墙壁的位置和大小
        """
        # 将世界坐标转换为小地图坐标
        minimap_x = int(rect.x * self.scale_x)
        minimap_y = int(rect.y * self.scale_y)
        minimap_width = max(1, int(rect.width * self.scale_x))
        minimap_height = max(1, int(rect.height * self.scale_y))
        
        # 确保墙壁在小地图范围内
        minimap_x = max(0, min(minimap_x, self.minimap_width - minimap_width))
        minimap_y = max(0, min(minimap_y, self.minimap_height - minimap_height))
        
        # 绘制墙壁
        pygame.draw.rect(self.surface, self.wall_color, 
                        (minimap_x, minimap_y, minimap_width, minimap_height))
    
    def render(self, screen, player, key_items, escape_door, ammo_supplies=None, health_supplies=None, teleport_items=None, collision_tiles=None, dual_player_system=None):
        """渲染小地图
        
        Args:
            screen: 游戏屏幕
            player: 玩家对象
            key_items: 钥匙物品对象列表
            escape_door: 逃生门对象
            ammo_supplies: 弹药补给物品列表
            health_supplies: 生命补给物品列表
            teleport_items: 传送道具物品列表
            collision_tiles: 碰撞地形列表
            dual_player_system: 双人系统对象
        """
        # 清空小地图表面
        self.surface.fill((0, 0, 0))
        
        # 绘制碰撞地形（墙壁）
        if collision_tiles:
            for wall_rect in collision_tiles:
                self.draw_wall(wall_rect)
        
        # 绘制边框
        pygame.draw.rect(self.surface, self.border_color, 
                        (0, 0, self.minimap_width, self.minimap_height), 2)
        
        # 绘制玩家位置
        if dual_player_system:
            # 双人模式：绘制两个角色
            # 绘制忍者蛙（圆形）
            ninja_x, ninja_y = self.world_to_minimap(dual_player_system.ninja_frog.world_x, dual_player_system.ninja_frog.world_y)
            self.draw_marker(ninja_x, ninja_y, self.player_color, 5)
            
            # 绘制神秘剑客（三角形）
            mystic_x, mystic_y = self.world_to_minimap(dual_player_system.mystic_swordsman.world_x, dual_player_system.mystic_swordsman.world_y)
            self.draw_triangle_marker(mystic_x, mystic_y, self.mystic_color, 6)
        elif player:
            # 单人模式：绘制单个玩家
            player_x, player_y = self.world_to_minimap(player.world_x, player.world_y)
            self.draw_marker(player_x, player_y, self.player_color, 5)
        
        # 绘制钥匙位置
        if key_items:
            for key_item in key_items:
                if hasattr(key_item, 'world_x') and hasattr(key_item, 'world_y'):
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
        
        # 绘制传送道具位置
        if teleport_items:
            for teleport_item in teleport_items:
                if hasattr(teleport_item, 'world_x') and hasattr(teleport_item, 'world_y'):
                    teleport_x, teleport_y = self.world_to_minimap(teleport_item.world_x, teleport_item.world_y)
                    self.draw_marker(teleport_x, teleport_y, self.teleport_color, 4)
        

        
        # 将小地图绘制到屏幕上
        screen.blit(self.surface, (self.minimap_x, self.minimap_y))
        
        # 绘制小地图标题
        font = pygame.font.SysFont('simHei', 24)
        title_text = font.render("小地图", True, (255, 255, 255))
        title_rect = title_text.get_rect()
        title_rect.centerx = self.minimap_x + self.minimap_width // 2
        title_rect.y = self.minimap_y - 25
        screen.blit(title_text, title_rect)
        
        # 绘制图例（优化布局，避免遮挡）
        legend_y = self.minimap_y + self.minimap_height + 5
        legend_x = self.minimap_x
        
        # 使用更小的字体
        legend_font = pygame.font.SysFont('simHei', 14)  # 进一步减小字体
        
        # 第一行图例
        # 玩家图例
        pygame.draw.circle(screen, self.player_color, (legend_x +7, legend_y + 5), 2)
        player_text = legend_font.render("忍者", True, (255, 255, 255))
        screen.blit(player_text, (legend_x + 15, legend_y))
        
        # 神秘剑客图例
        pygame.draw.polygon(screen, self.mystic_color, [
            (legend_x + 47, legend_y + 3),
            (legend_x + 44, legend_y + 7),
            (legend_x + 50, legend_y + 7)
        ])
        mystic_text = legend_font.render("剑客", True, (255, 255, 255))
        screen.blit(mystic_text, (legend_x + 55, legend_y))
        
        # 钥匙图例
        pygame.draw.circle(screen, self.key_color, (legend_x + 87, legend_y + 5), 2)
        key_text = legend_font.render("钥匙", True, (255, 255, 255))
        screen.blit(key_text, (legend_x + 95, legend_y))
        
        # 逃生门图例
        pygame.draw.circle(screen, self.door_color, (legend_x + 127, legend_y + 5), 2)
        door_text = legend_font.render("出口", True, (255, 255, 255))
        screen.blit(door_text, (legend_x + 135, legend_y))
        
        # 第二行图例
        legend_y2 = legend_y + 12
        # 弹药补给图例
        pygame.draw.circle(screen, self.ammo_supply_color, (legend_x+7, legend_y2 + 5), 2)
        ammo_text = legend_font.render("弹药", True, (255, 255, 255))
        screen.blit(ammo_text, (legend_x + 15, legend_y2))
        
        # 生命补给图例
        pygame.draw.circle(screen, self.health_supply_color, (legend_x + 47, legend_y2 + 5), 2)
        health_text = legend_font.render("生命", True, (255, 255, 255))
        screen.blit(health_text, (legend_x + 55, legend_y2))
        
        # 传送道具图例
        pygame.draw.circle(screen, self.teleport_color, (legend_x + 87, legend_y2 + 5), 2)
        teleport_text = legend_font.render("传送", True, (255, 255, 255))
        screen.blit(teleport_text, (legend_x + 95, legend_y2))
        
        # 墙壁图例
        pygame.draw.rect(screen, self.wall_color, (legend_x + 127, legend_y2 + 4, 4, 4))
        wall_text = legend_font.render("墙壁", True, (255, 255, 255))
        screen.blit(wall_text, (legend_x + 135, legend_y2))
        
 
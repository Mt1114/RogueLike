import pygame
from .resource_manager import resource_manager

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
        
        # 小地图尺寸和位置（放大1.5倍）
        self.minimap_width = 270  # 180 * 1.5 = 270
        self.minimap_height = 180  # 120 * 1.5 = 180
        self.minimap_x = screen_width - self.minimap_width - 60  # 右上角，增加更多右边距
        self.minimap_y = 150  # 距离顶部150像素，避免与经验条重叠
        
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
        
        # 标记大小（放大1.5倍）
        self.marker_size = 6  # 4 * 1.5 = 6
        
        # 加载小地图图标
        self._load_minimap_icons()
        
    def _load_minimap_icons(self):
        """加载小地图图标"""
        try:
            # 加载角色图标
            self.role1_icon = resource_manager.load_image('role1_map', 'images/ui/role1.png')
            self.role2_icon = resource_manager.load_image('role2_map', 'images/ui/role2.png')
            
            # 加载物品图标
            self.key_icon = resource_manager.load_image('key_map', 'images/ui/key.png')
            self.heart_icon = resource_manager.load_image('heart_map', 'images/ui/heart_map.png')
            self.transport_icon = resource_manager.load_image('transport_map', 'images/ui/transport_map.png')
            self.bullet_icon = resource_manager.load_image('bullet_map', 'images/ui/bullet.png')
            self.door_icon = resource_manager.load_image('door_map', 'images/ui/door.png')
            
            
        except Exception as e:
            print(f"加载小地图图标失败: {e}")
            self.role1_icon = None
            self.role2_icon = None
            self.key_icon = None
            self.heart_icon = None
            self.transport_icon = None
            self.bullet_icon = None
            self.door_icon = None
        
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
            size = 9  # 6 * 1.5 = 9
        
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
    
    def draw_icon(self, x, y, icon, size=None):
        """在小地图上绘制图标
        
        Args:
            x, y: 小地图坐标
            icon: 图标图片
            size: 图标大小
        """
        if size is None:
            size = 8
        
        # 确保图标在小地图范围内
        x = max(size, min(x, self.minimap_width - size))
        y = max(size, min(y, self.minimap_height - size))
        
        # 缩放图标到指定大小
        scaled_icon = pygame.transform.scale(icon, (size * 2, size * 2))
        
        # 计算图标位置（居中）
        icon_rect = scaled_icon.get_rect(center=(x, y))
        
        # 绘制图标
        self.surface.blit(scaled_icon, icon_rect)
    
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
            # 绘制忍者蛙（role1图标）
            ninja_x, ninja_y = self.world_to_minimap(dual_player_system.ninja_frog.world_x, dual_player_system.ninja_frog.world_y)
            if self.role1_icon:
                self.draw_icon(ninja_x, ninja_y, self.role1_icon, 8)
            else:
                self.draw_marker(ninja_x, ninja_y, self.player_color, 5)
            
            # 绘制神秘剑客（role2图标）
            mystic_x, mystic_y = self.world_to_minimap(dual_player_system.mystic_swordsman.world_x, dual_player_system.mystic_swordsman.world_y)
            if self.role2_icon:
                self.draw_icon(mystic_x, mystic_y, self.role2_icon, 8)
            else:
                self.draw_triangle_marker(mystic_x, mystic_y, self.mystic_color, 6)
        elif player:
            # 单人模式：绘制单个玩家
            player_x, player_y = self.world_to_minimap(player.world_x, player.world_y)
            if self.role1_icon:
                self.draw_icon(player_x, player_y, self.role1_icon, 8)
            else:
                self.draw_marker(player_x, player_y, self.player_color, 5)
        
        # 绘制钥匙位置
        if key_items:
            for key_item in key_items:
                if hasattr(key_item, 'world_x') and hasattr(key_item, 'world_y'):
                    key_x, key_y = self.world_to_minimap(key_item.world_x, key_item.world_y)
                    if self.key_icon:
                        self.draw_icon(key_x, key_y, self.key_icon, 6)
                    else:
                        self.draw_marker(key_x, key_y, self.key_color, 4)
        
        # 绘制逃生门位置
        if escape_door and hasattr(escape_door, 'world_x') and hasattr(escape_door, 'world_y'):
            door_x, door_y = self.world_to_minimap(escape_door.world_x, escape_door.world_y)
            if self.door_icon:
                self.draw_icon(door_x, door_y, self.door_icon, 9)  # 放大1.5倍：6 * 1.5 = 9
            else:
                self.draw_marker(door_x, door_y, self.door_color, 9)  # 放大1.5倍：6 * 1.5 = 9
        
        # 绘制弹药补给位置
        if ammo_supplies:
            for supply in ammo_supplies:
                if hasattr(supply, 'world_x') and hasattr(supply, 'world_y'):
                    supply_x, supply_y = self.world_to_minimap(supply.world_x, supply.world_y)
                    if self.bullet_icon:
                        self.draw_icon(supply_x, supply_y, self.bullet_icon, 6)
                    else:
                        self.draw_marker(supply_x, supply_y, self.ammo_supply_color, 3)
        
        # 绘制生命补给位置
        if health_supplies:
            for supply in health_supplies:
                if hasattr(supply, 'world_x') and hasattr(supply, 'world_y'):
                    supply_x, supply_y = self.world_to_minimap(supply.world_x, supply.world_y)
                    if self.heart_icon:
                        self.draw_icon(supply_x, supply_y, self.heart_icon, 6)
                    else:
                        self.draw_marker(supply_x, supply_y, self.health_supply_color, 3)
        
        # 绘制传送道具位置
        if teleport_items:
            for teleport_item in teleport_items:
                if hasattr(teleport_item, 'world_x') and hasattr(teleport_item, 'world_y'):
                    teleport_x, teleport_y = self.world_to_minimap(teleport_item.world_x, teleport_item.world_y)
                    if self.transport_icon:
                        self.draw_icon(teleport_x, teleport_y, self.transport_icon, 6)
                    else:
                        self.draw_marker(teleport_x, teleport_y, self.teleport_color, 4)
        

        
        # 将小地图绘制到屏幕上
        screen.blit(self.surface, (self.minimap_x, self.minimap_y))
        
        # 绘制小地图标题（放大字体）
        font = pygame.font.SysFont('simHei', 36)  # 从24增加到36
        title_text = font.render("小地图", True, (255, 255, 255))
        title_rect = title_text.get_rect()
        title_rect.centerx = self.minimap_x + self.minimap_width // 2
        title_rect.y = self.minimap_y - 35  # 调整位置
        screen.blit(title_text, title_rect)
        
        # 绘制图例（适应新的小地图规模）
        legend_y = self.minimap_y + self.minimap_height + 10
        legend_x = self.minimap_x
        
        # 使用更大的字体，适应小地图规模
        legend_font = pygame.font.SysFont('simHei', 18)  # 从14增加到18
        
        # 第一行图例 - 使用图片图标
        # 玩家图例（role1）
        if self.role1_icon:
            scaled_role1 = pygame.transform.scale(self.role1_icon, (12, 12))
            screen.blit(scaled_role1, (legend_x + 8, legend_y + 2))
        else:
            pygame.draw.circle(screen, self.player_color, (legend_x + 8, legend_y + 7), 3)
        player_text = legend_font.render("忍者", True, (255, 255, 255))
        screen.blit(player_text, (legend_x + 25, legend_y))
        
        # 神秘剑客图例（role2）
        if self.role2_icon:
            scaled_role2 = pygame.transform.scale(self.role2_icon, (12, 12))
            screen.blit(scaled_role2, (legend_x + 65, legend_y + 2))
        else:
            pygame.draw.polygon(screen, self.mystic_color, [
                (legend_x + 65, legend_y + 4),
                (legend_x + 60, legend_y + 10),
                (legend_x + 70, legend_y + 10)
            ])
        mystic_text = legend_font.render("剑客", True, (255, 255, 255))
        screen.blit(mystic_text, (legend_x + 82, legend_y))
        
        # 钥匙图例
        if self.key_icon:
            scaled_key = pygame.transform.scale(self.key_icon, (12, 12))
            screen.blit(scaled_key, (legend_x + 125, legend_y + 2))
        else:
            pygame.draw.circle(screen, self.key_color, (legend_x + 125, legend_y + 7), 3)
        key_text = legend_font.render("钥匙", True, (255, 255, 255))
        screen.blit(key_text, (legend_x + 142, legend_y))
        
        # 逃生门图例
        if self.door_icon:
            scaled_door = pygame.transform.scale(self.door_icon, (12, 12))
            screen.blit(scaled_door, (legend_x + 185, legend_y + 2))
        else:
            pygame.draw.circle(screen, self.door_color, (legend_x + 185, legend_y + 7), 3)
        door_text = legend_font.render("出口", True, (255, 255, 255))
        screen.blit(door_text, (legend_x + 200, legend_y))
        
        # 第二行图例 - 增加行间距
        legend_y2 = legend_y + 25
        # 弹药补给图例
        if self.bullet_icon:
            scaled_bullet = pygame.transform.scale(self.bullet_icon, (12, 12))
            screen.blit(scaled_bullet, (legend_x + 8, legend_y2 + 2))
        else:
            pygame.draw.circle(screen, self.ammo_supply_color, (legend_x + 8, legend_y2 + 7), 3)
        ammo_text = legend_font.render("弹药", True, (255, 255, 255))
        screen.blit(ammo_text, (legend_x + 25, legend_y2))
        
        # 生命补给图例
        if self.heart_icon:
            scaled_heart = pygame.transform.scale(self.heart_icon, (12, 12))
            screen.blit(scaled_heart, (legend_x + 65, legend_y2 + 2))
        else:
            pygame.draw.circle(screen, self.health_supply_color, (legend_x + 65, legend_y2 + 7), 3)
        health_text = legend_font.render("生命", True, (255, 255, 255))
        screen.blit(health_text, (legend_x + 82, legend_y2))
        
        # 传送道具图例
        if self.transport_icon:
            scaled_transport = pygame.transform.scale(self.transport_icon, (12, 12))
            screen.blit(scaled_transport, (legend_x + 125, legend_y2 + 2))
        else:
            pygame.draw.circle(screen, self.teleport_color, (legend_x + 125, legend_y2 + 7), 3)
        teleport_text = legend_font.render("传送", True, (255, 255, 255))
        screen.blit(teleport_text, (legend_x + 142, legend_y2))
        
        # 墙壁图例
        pygame.draw.rect(screen, self.wall_color, (legend_x + 185, legend_y2 + 5, 6, 6))
        wall_text = legend_font.render("墙壁", True, (255, 255, 255))
        screen.blit(wall_text, (legend_x + 200, legend_y2))
    
    def reset(self):
        """重置小地图状态"""
        # 清空小地图表面
        self.surface.fill((0, 0, 0, 100))
        print("小地图已重置")
    
    def update_map_size(self, map_width, map_height):
        """更新地图尺寸并重新计算缩放比例
        
        Args:
            map_width: 新地图宽度
            map_height: 新地图高度
        """
        self.map_width = map_width
        self.map_height = map_height
        
        # 重新计算缩放比例
        self.scale_x = self.minimap_width / map_width
        self.scale_y = self.minimap_height / map_height
        
        print(f"小地图尺寸已更新: {map_width}x{map_height}, 缩放比例: {self.scale_x:.3f}x{self.scale_y:.3f}")
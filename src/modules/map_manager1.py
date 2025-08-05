import os
import pygame
import pytmx
import pyscroll
from pytmx.util_pygame import load_pygame
from .resource_manager import resource_manager

class MapManager:
    """地图管理器类，用于加载和渲染TMX地图文件"""
    
    def __init__(self, screen, scale=2.0):
        """初始化地图管理器
        
        Args:
            screen: pygame显示屏幕
            scale: 地图缩放比例，默认为2.0（放大2倍）
        """
        self.screen = screen
        self.scale = scale  # 地图缩放比例
        self.current_map = None
        self.map_layer = None
        self.map_group = None
        self.tmx_data = None  # 保存原始TMX数据，用于直接渲染
        
        # 性能优化：添加图块缓存和视口计算
        self.tile_cache = {}  # 缓存已渲染的图块
        self.last_camera_pos = None  # 上一次相机位置，用于检测相机是否移动
        self.visible_tiles = []  # 当前视口可见的图块
        self.use_direct_render = False  # 是否使用直接渲染（作为后备方案）
        
    def get_tile_gid(self):
        # 直接解析 TMX 文件
        import xml.etree.ElementTree as ET
        import os
        collision_rects = []
        # 获取 TMX 文件路径
        map_name = self.current_map.get('name', 'simple_map')
        tmx_path = os.path.join("assets", "maps", f"{map_name}.tmx")
        
        if not os.path.exists(tmx_path):
            print(f"TMX 文件不存在: {tmx_path}")
            return collision_rects
        
        try:
            # 解析 XML
            tree = ET.parse(tmx_path)
            root = tree.getroot()
            
            # 查找所有图层
            for layer in root.findall('.//layer'):
                layer_name = layer.get('name', 'unnamed')
                print(f"=== 直接解析图层: {layer_name} ===")
                
                # 查找数据
                data_elem = layer.find('data')
                if data_elem is not None:
                    # 获取 CSV 数据
                    csv_data = data_elem.text.strip()
                    gid_list = csv_data.split(',')
                    
                    # 统计 GID 39
                    gid_39_count = 0
                    total_count = 0
                    
                    for i, gid_str in enumerate(gid_list):
                        try:
                            gid = int(gid_str)
                            total_count += 1
                            if gid == 39:
                                gid_39_count += 1
                                x = i % 100  # 假设宽度是100
                                y = i // 100
                                print(f"找到 GID 39 在位置 ({x}, {y})")
                                collision_rects.append(
                                    pygame.Rect(
                                        x * self.tile_width,
                                        y * self.tile_height,
                                        self.tile_width,
                                        self.tile_height
                                    )
                                )
                        except ValueError:
                            print(f"无法解析 GID: {gid_str}")
                    
        except Exception as e:
            print(f"解析 TMX 文件时出错: {e}")
        return collision_rects

    def load_map(self, map_name):
        """加载TMX地图文件
        
        Args:
            map_name: 地图文件名，不包含扩展名
            
        Returns:
            bool: 加载成功返回True，否则返回False
        """
        # 构建地图文件的完整路径
        map_path = os.path.join(resource_manager.resource_dir, "maps", f"{map_name}.tmx")
         
        try:
            # 使用pytmx.util_pygame直接加载TMX文件
            try:
                self.tmx_data = load_pygame(map_path)
                
                # 获取地图尺寸（应用缩放）
                self.tile_width = int(self.tmx_data.tilewidth * self.scale)
                self.tile_height = int(self.tmx_data.tileheight * self.scale)
                self.map_width = int(self.tmx_data.width * self.tile_width)
                self.map_height = int(self.tmx_data.height * self.tile_height)
                
                # 存储地图数据
                self.current_map = {
                    'name': map_name,
                    'tmx_data': self.tmx_data
                }
                
                # 性能优化：预缓存所有图块
                self._cache_all_tiles()
                
                # 尝试创建pyscroll的渲染器（可能会失败，但不影响直接渲染）
                try:
                    # 创建地图数据
                    map_data = pyscroll.data.TiledMapData(self.tmx_data)
                    
                    # 创建地图层
                    self.map_layer = pyscroll.orthographic.BufferedRenderer(
                        map_data,
                        self.screen.get_size(),
                        clamp_camera=True  # 限制相机不超出地图边界
                    )
                    
                    # 应用缩放比例
                    self.map_layer.zoom = self.scale
                    
                    # 创建地图精灵组
                    self.map_group = pyscroll.PyscrollGroup(map_layer=self.map_layer)
                    self.use_direct_render = False
                except Exception as e:
                    self.map_layer = None
                    self.map_group = None
                    self.use_direct_render = True
                
                return True
                
            except Exception as e:
                print(f"加载TMX文件时出错: {e}")
                import traceback
                traceback.print_exc()
                return False
                
        except Exception as e:
            print(f"加载地图 '{map_name}' 失败: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def _cache_all_tiles(self):
        """预缓存所有图块，提高渲染性能"""
        if not self.tmx_data:
            return
            
        self.tile_cache = {}
        
        # 遍历所有图层和图块，缓存它们
        for layer in self.tmx_data.visible_layers:
            if isinstance(layer, pytmx.TiledTileLayer):
                for x, y, gid in layer:
                    if gid:  # 图块ID不为0
                        if gid not in self.tile_cache:
                            tile = self.tmx_data.get_tile_image_by_gid(gid)
                            if tile:
                                # 应用缩放
                                scaled_tile = pygame.transform.scale(tile, (self.tile_width, self.tile_height))
                                self.tile_cache[gid] = scaled_tile
        
    
    def _calculate_visible_tiles(self, offset_x, offset_y):
        """计算当前视口内可见的图块
        
        Args:
            offset_x: 相机X位置的偏移量
            offset_y: 相机Y位置的偏移量
        """
        if not self.tmx_data:
            return
        
        # 计算视口边界（以图块为单位）
        # 使用偏移量计算起始位置
        viewport_left = max(0, int(-offset_x / self.tile_width))
        viewport_top = max(0, int(-offset_y / self.tile_height))
        
        # 计算视口右下角，多加几个图块确保覆盖整个屏幕
        viewport_right = min(
            self.tmx_data.width, 
            viewport_left + int(self.screen.get_width() / self.tile_width) + 2
        )
        viewport_bottom = min(
            self.tmx_data.height, 
            viewport_top + int(self.screen.get_height() / self.tile_height) + 2
        )
        
        # 存储可见的图块信息
        self.visible_tiles = []
        
        # 遍历所有图层
        for layer in self.tmx_data.visible_layers:
            if isinstance(layer, pytmx.TiledTileLayer):
                # 只处理视口内的图块
                layer_tiles = []
                for x in range(viewport_left, viewport_right):
                    for y in range(viewport_top, viewport_bottom):
                        gid = layer.data[y][x]  # 注意：在pytmx中y是行，x是列
                        if gid:
                            tile = self.tile_cache.get(gid)
                            if tile:
                                # 计算屏幕坐标
                                pos_x = x * self.tile_width + offset_x
                                pos_y = y * self.tile_height + offset_y
                                layer_tiles.append((tile, pos_x, pos_y))
                
                self.visible_tiles.append(layer_tiles)
    
    def render(self, camera_x, camera_y):
        """渲染地图
        
        Args:
            camera_x: 相机在世界坐标系中的X位置
            camera_y: 相机在世界坐标系中的Y位置
        """
        # 计算相机偏移量 - 将世界中心移动到屏幕中心
        offset_x = self.screen.get_width() // 2 - camera_x
        offset_y = self.screen.get_height() // 2 - camera_y
        
        # 使用pyscroll渲染
        if self.map_layer and self.map_group and not self.use_direct_render:
            try:
                # 设置相机位置
                self.map_layer.center((camera_x, camera_y))
                
                # 绘制地图
                self.map_group.draw(self.screen)
                return
            except Exception as e:
                print(f"pyscroll渲染失败，切换到优化的直接渲染: {e}")
                self.use_direct_render = True
        
        # 优化的直接渲染
        if self.tmx_data:
            # 检查相机是否移动，如果移动了才重新计算可见图块
            if self.last_camera_pos != (offset_x, offset_y):
                self._calculate_visible_tiles(offset_x, offset_y)
                self.last_camera_pos = (offset_x, offset_y)
            
            # 绘制所有可见图块
            for layer_tiles in self.visible_tiles:
                for tile, pos_x, pos_y in layer_tiles:
                    self.screen.blit(tile, (pos_x, pos_y))

    def render_layers_before_player(self, camera_x, camera_y):
        """渲染玩家之前的图层（地面图层）
        
        Args:
            camera_x: 相机在世界坐标系中的X位置
            camera_y: 相机在世界坐标系中的Y位置
        """
        # 计算相机偏移量
        offset_x = self.screen.get_width() // 2 - camera_x
        offset_y = self.screen.get_height() // 2 - camera_y
        
        if not self.tmx_data:
            return
        
        # 检查相机是否移动，如果移动了才重新计算可见图块
        if self.last_camera_pos != (offset_x, offset_y):
            self._calculate_visible_tiles(offset_x, offset_y)
            self.last_camera_pos = (offset_x, offset_y)
        
        # 定义应该渲染在玩家之前的图层名称
        ground_layer_names = [
            "Floor", "Floor_darker_surface", "Floor2_darker_surface", "Floor2_pool",
            "water_floor3", "water_detailization", "water_detailization2"
        ]
        
        # 根据图层名称动态确定渲染顺序
        for i, layer in enumerate(self.tmx_data.layers):
            if hasattr(layer, 'name') and layer.name in ground_layer_names:
                if i < len(self.visible_tiles):
                    layer_tiles = self.visible_tiles[i]
                    for tile, pos_x, pos_y in layer_tiles:
                        self.screen.blit(tile, (pos_x, pos_y))

    def render_layers_after_player(self, camera_x, camera_y):
        """渲染玩家之后的图层（墙壁和装饰图层）
        
        Args:
            camera_x: 相机在世界坐标系中的X位置
            camera_y: 相机在世界坐标系中的Y位置
        """
        # 计算相机偏移量
        offset_x = self.screen.get_width() // 2 - camera_x
        offset_y = self.screen.get_height() // 2 - camera_y
        
        if not self.tmx_data:
            return
        
        # 检查相机是否移动，如果移动了才重新计算可见图块
        if self.last_camera_pos != (offset_x, offset_y):
            self._calculate_visible_tiles(offset_x, offset_y)
            self.last_camera_pos = (offset_x, offset_y)
        
        # 定义应该渲染在玩家之后的图层名称
        wall_layer_names = [
            "Walls", "Objects", "Objects2", "Objects_under_wall",
            "Windows", "Lights", "traps"
        ]
        
        # 根据图层名称动态确定渲染顺序
        for i, layer in enumerate(self.tmx_data.layers):
            if hasattr(layer, 'name') and layer.name in wall_layer_names:
                if i < len(self.visible_tiles):
                    layer_tiles = self.visible_tiles[i]
                    for tile, pos_x, pos_y in layer_tiles:
                        self.screen.blit(tile, (pos_x, pos_y))

    def get_layer_count(self):
        """获取地图的图层数量
        
        Returns:
            int: 图层数量
        """
        if not self.tmx_data:
            return 0
        return len(self.tmx_data.visible_layers)

    def get_layer_names(self):
        """获取所有图层的名称
        
        Returns:
            list: 图层名称列表
        """
        if not self.tmx_data:
            return []
        
        layer_names = []
        for layer in self.tmx_data.visible_layers:
            if hasattr(layer, 'name'):
                layer_names.append(layer.name)
            else:
                layer_names.append(f"layer_{len(layer_names)}")
        
        return layer_names
    
    def get_map_size(self):
        """获取地图尺寸
        
        Returns:
            tuple: (宽度,高度) 地图的像素尺寸
        """
        if not self.current_map:
            return (0, 0)
        
        return (self.map_width, self.map_height)
    
    def get_tile_size(self):
        """获取地图的瓦片尺寸
        
        Returns:
            tuple: (宽度,高度) 瓦片的像素尺寸
        """
        if not self.current_map:
            return (0, 0)
        
        return (self.tile_width, self.tile_height)
    
    def get_collision_tiles(self, layer_name="collision"):
        """获取指定层上的碰撞图块
        
        Args:
            layer_name: 碰撞层的名称
            
        Returns:
            list: 包含所有碰撞图块的矩形列表
        """
        if not self.current_map:
            print("get_collision_tiles: 没有当前地图")
            return []
            
        tmx_data = self.current_map['tmx_data']
        collision_rects = []
        

        
        # 查找指定的碰撞层
        for layer in tmx_data.visible_layers:
            layer_name_actual = getattr(layer, 'name', 'unnamed')
           
            if hasattr(layer, 'name') and layer.name == layer_name:
                
                # 这是一个图块层
                if hasattr(layer, 'data'):                  
                    for x, y, gid in layer.iter_data():
                        if gid:  # 如果图块ID不为0
                            collision_rects.append(
                                pygame.Rect(
                                    int(x * self.tile_width),
                                    int(y * self.tile_height),
                                    self.tile_width,
                                    self.tile_height
                                )
                            )
                    
                break

        if not collision_rects:
            print(f"get_collision_tiles: 警告: 没有找到碰撞图块数据")
            
        return collision_rects
    
    def get_objects(self, layer_name):
        """获取指定对象层上的所有对象
        
        Args:
            layer_name: 对象层的名称
            
        Returns:
            list: 对象列表
        """
        if not self.current_map:
            return []
            
        tmx_data = self.current_map['tmx_data']
        objects = []
        
        # 查找指定的对象层
        try:
            object_layer = tmx_data.get_layer_by_name(layer_name)
            for obj in object_layer:
                objects.append({
                    'id': obj.id,
                    'name': getattr(obj, 'name', ''),
                    'type': getattr(obj, 'type', ''),
                    'x': obj.x,
                    'y': obj.y,
                    'width': getattr(obj, 'width', 0),
                    'height': getattr(obj, 'height', 0),
                    'properties': getattr(obj, 'properties', {})
                })
        except ValueError:
            # 如果找不到指定名称的层
            print(f"找不到名为 '{layer_name}' 的对象层")
        
        return objects
    
    def set_scale(self, scale):
        """设置地图缩放比例
        
        Args:
            scale (float): 缩放比例，1.0为原始大小，2.0为放大2倍
        """
        self.scale = scale
        if self.current_map:
            # 重新加载当前地图以应用新的缩放
            current_map_name = self.current_map['name']
            self.load_map(current_map_name)
    
    def get_scale(self):
        """获取当前缩放比例"""
        return self.scale 
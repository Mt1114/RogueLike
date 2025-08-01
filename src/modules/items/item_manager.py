import random
from .item import Item

class ItemManager:
    def __init__(self):
        self.items = []
        
        # 基础掉落概率
        self.base_coin_drop_rate = 0.1  # 10%概率掉落金币
        self.base_health_drop_rate = 0.05  # 5%概率掉落医疗包
        
    def spawn_item(self, x, y, enemy_type=None, player=None):
        # 必定掉落经验球
        self.items.append(Item(x, y, 'exp'))

        # 如果是boss，必定掉落宝箱
        if enemy_type == 'bat':
            self.items.append(Item(x, y, 'chest'))
            return
        
        # 如果没有提供player参数，使用基础掉落概率
        luck_multiplier = player.luck if player else 1.0
        
        # 随机掉落其他物品，受幸运值影响
        if random.random() < self.base_coin_drop_rate * luck_multiplier:  # 受幸运值加成的金币掉落概率
            self.items.append(Item(x + random.randint(-10, 10), y + random.randint(-10, 10), 'coin'))
            
        if random.random() < self.base_health_drop_rate * luck_multiplier:  # 受幸运值加成的医疗包掉落概率
            self.items.append(Item(x + random.randint(-10, 10), y + random.randint(-10, 10), 'health'))
            
    def update(self, dt, player):
        for item in self.items[:]:  # 使用切片创建副本以避免在迭代时修改列表
            item.update(dt, player)
            if item.collected:
                try:
                    self.items.remove(item)
                except ValueError:
                    # 物品可能已经被其他系统移除，忽略错误
                    pass
                
    def render(self, screen, camera_x, camera_y, screen_center_x, screen_center_y, lighting_manager=None):
        for item in self.items:
            # 检查物品是否在光照范围内
            if lighting_manager and hasattr(lighting_manager, 'is_enabled') and lighting_manager.is_enabled():
                # 将物品的世界坐标转换为屏幕坐标进行检查
                item_world_x = item.world_x
                item_world_y = item.world_y
                item_screen_x = screen_center_x + (item_world_x - camera_x)
                item_screen_y = screen_center_y + (item_world_y - camera_y)
                
                # 检查物品是否在光照范围内
                if lighting_manager.is_in_light(item_screen_x, item_screen_y):
                    item.render(screen, camera_x, camera_y, screen_center_x, screen_center_y)
            else:
                # 如果没有光照系统或光照系统被禁用，正常渲染
                item.render(screen, camera_x, camera_y, screen_center_x, screen_center_y) 
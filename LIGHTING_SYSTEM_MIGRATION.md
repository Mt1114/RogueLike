# 光照系统迁移文档

## 概述

已将光照系统从使用 `Pygame_Lights` 库迁移到使用 `VisionSystem`。这个迁移提供了更好的性能、更清晰的代码结构和更好的可维护性。

## 主要修改

### 1. `lighting_manager.py` 重写

**之前：**
- 使用 `Pygame_Lights` 库
- 复杂的像素着色器
- 难以调试和维护

**现在：**
- 使用 `VisionSystem` 作为核心
- 更清晰的代码结构
- 更好的性能优化

### 2. 核心功能保持不变

- ✅ 玩家圆形光照
- ✅ 鼠标扇形光照
- ✅ 墙壁遮挡效果
- ✅ 全局黑暗效果
- ✅ 光照检测功能

### 3. 性能改进

- 光线追踪算法优化
- 缓存机制减少重复计算
- 更高效的碰撞检测
- 减少内存使用

## 技术细节

### VisionSystem 特性

1. **光线追踪**
   - 支持墙壁遮挡
   - 性能优化的光线算法
   - 缓存机制

2. **视野系统**
   - 圆形光圈（玩家周围）
   - 扇形视野（鼠标方向）
   - 可配置的角度和半径

3. **黑暗遮罩**
   - 全局黑暗效果
   - 可调节的黑暗强度
   - 与视野系统集成

### 接口兼容性

新的 `LightingManager` 保持了与原有代码的接口兼容性：

```python
# 创建光照管理器
lighting_manager = LightingManager(screen_width, screen_height)

# 设置墙壁
lighting_manager.set_walls(walls, tile_size)

# 渲染光照
lighting_manager.render(screen, player_x, player_y, mouse_x, mouse_y, camera_x, camera_y)

# 检查光照状态
lighting_manager.is_enabled()
lighting_manager.is_in_light(x, y)
```

## 配置选项

### 视野配置
- `radius`: 视野半径
- `angle`: 视野角度（度）
- `color`: 视野颜色
- `circle_radius`: 圆形光圈半径

### 黑暗配置
- `darkness_alpha`: 黑暗强度 (0-255)

## 使用方法

### 在游戏中使用

```python
# 在 Game 类中
def _init_lighting_system(self):
    screen_width = self.screen.get_width()
    screen_height = self.screen.get_height()
    self.lighting_manager = LightingManager(screen_width, screen_height)

def render(self):
    # 渲染光照系统
    if self.lighting_manager and self.enable_lighting:
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
```

### 配置光照

```python
# 设置光照配置
lighting_manager.set_light_config(
    player_radius=150,      # 玩家光照半径
    mouse_radius=300,       # 鼠标视野半径
    mouse_angle=90,         # 鼠标视野角度
    light_color=(255, 255, 200),  # 光照颜色
    darkness_intensity=100  # 黑暗强度
)
```

## 优势

1. **性能提升**
   - 更高效的光线追踪
   - 智能缓存机制
   - 减少CPU使用

2. **代码质量**
   - 更清晰的代码结构
   - 更好的可维护性
   - 更容易调试

3. **功能增强**
   - 更精确的视野计算
   - 更好的墙壁遮挡效果
   - 可配置的视野参数

4. **依赖减少**
   - 不再依赖 `Pygame_Lights` 库
   - 减少外部依赖
   - 更好的跨平台兼容性

## 测试

使用 `test_lighting.py` 可以测试新的光照系统：

```bash
python test_lighting.py
```

这个测试会显示：
- 玩家位置（绿色圆圈）
- 鼠标位置（红色圆圈）
- 测试墙壁（灰色矩形）
- 光照效果（视野和黑暗）

## 注意事项

1. **性能监控**
   - 新的光照系统包含性能统计
   - 可以通过 `get_performance_stats()` 监控性能

2. **缓存管理**
   - 系统会自动管理缓存
   - 墙壁数据变化时会自动清除缓存

3. **错误处理**
   - 包含完整的错误处理机制
   - 光照系统出错时会自动禁用

## 新增功能

### 光照预设系统
- ✅ 9种预设配置（默认、宽视野、窄视野、夜视模式、隧道视野、聚光灯、泛光灯、最小视野、明亮模式）
- ✅ 实时预设切换（F4键）
- ✅ 预设参数可配置
- ✅ 性能优化建议

### 使用方法
```python
# 游戏内控制
# F3: 切换光照系统开关
# F4: 循环切换光照预设

# 编程接口
game.set_lighting_preset("night_vision")  # 设置夜视模式
game.set_lighting_preset("tunnel")        # 设置隧道视野
game.set_lighting_preset("spotlight")     # 设置聚光灯模式
```

## 迁移完成

✅ 光照系统已成功从 `Pygame_Lights` 迁移到 `VisionSystem`
✅ 保持了所有原有功能
✅ 提供了更好的性能和可维护性
✅ 接口保持兼容性
✅ 新增光照预设系统 
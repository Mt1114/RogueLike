# 视野系统使用说明

## 概述

视野系统为游戏添加了动态的扇形视野效果，玩家只能看到视野范围内的内容，增加了游戏的策略性和紧张感。

## 功能特点

### 1. 双重视野系统
- **圆形区域**: 玩家周围完全消除黑暗的范围（默认80像素）
- **扇形区域**: 可调整的指向性视野，部分消除黑暗（默认300像素半径，90度角度）
- **消除黑暗**: 在视野区域内从黑暗遮罩中减去光照
- **方向**: 扇形视野跟随鼠标移动，实时更新

### 2. 黑暗遮罩效果
- 视野外的区域被黑暗覆盖
- 可调整黑暗程度
- 平滑的视觉过渡效果

### 3. 实时交互
- 视野方向跟随鼠标移动
- 支持动态调整参数
- 性能优化的渲染系统

## 使用方法

### 游戏中的控制

| 按键 | 功能 |
|------|------|
| F3 | 切换视野系统开关 |
| F4 | 增加扇形视野半径 (+50) |
| F5 | 减少扇形视野半径 (-50) |
| F6 | 增加扇形视野角度 (+15°) |
| F7 | 减少扇形视野角度 (-15°) |
| F8 | 增加圆形光圈半径 (+20) |
| F9 | 减少圆形光圈半径 (-20) |

### 编程接口

```python
# 创建视野系统
vision_system = VisionSystem(
    radius=300,                    # 扇形视野半径
    angle=90,                     # 扇形视野角度（度）
    color=(255, 255, 255, 128),  # 扇形区域透明度 (R, G, B, A)
    circle_radius=80,             # 圆形区域半径
    circle_color=(255, 255, 255, 255)  # 圆形区域完全不透明 (R, G, B, A)
)

# 创建黑暗遮罩
dark_overlay = DarkOverlay(
    screen_width, screen_height,
    darkness_alpha=180            # 黑暗程度 (0-255)
)

# 更新视野位置和方向
vision_system.update(
    center_x, center_y,           # 视野中心（通常是玩家位置）
    mouse_x, mouse_y              # 鼠标位置
)

# 渲染视野系统
vision_system.render(screen, dark_overlay.get_overlay())

# 检查点是否在视野内
is_visible = vision_system.is_in_vision(x, y)
```

## 配置选项

### 视野系统参数

```python
# 扇形视野半径（像素）
vision_radius = 300

# 扇形视野角度（度）
vision_angle = 90

# 扇形区域透明度 (R, G, B, A)
vision_color = (255, 255, 255, 128)

# 圆形区域半径（像素）
circle_radius = 80

# 圆形区域透明度 (R, G, B, A)
circle_color = (255, 255, 255, 255)

# 黑暗程度 (0-255)
darkness_alpha = 180
```

### 动态调整

```python
# 设置扇形视野半径
vision_system.set_radius(400)

# 设置扇形视野角度
vision_system.set_angle(120)

# 设置扇形视野颜色
vision_system.set_color((255, 200, 100, 150))

# 设置圆形光圈半径
vision_system.set_circle_radius(100)

# 设置圆形光圈颜色
vision_system.set_circle_color((255, 200, 100, 120))

# 设置黑暗程度
dark_overlay.set_darkness(200)
```

## 测试

运行测试脚本来验证视野系统：

```bash
python test_vision.py
```

测试功能包括：
- 视野方向跟随鼠标
- 实时调整视野参数
- 视野范围检测
- 视觉效果预览

## 性能优化

### 渲染优化
- 使用 `pygame.SRCALPHA` 支持透明度
- 预计算视野顶点减少重复计算
- 根据半径动态调整顶点数量

### 碰撞检测优化
- 快速距离检测
- 角度计算优化
- 边界检查避免无效计算

## 集成到游戏

视野系统已经集成到主游戏中：

1. **自动初始化**: 游戏启动时自动创建视野系统
2. **实时更新**: 每帧更新视野位置和方向
3. **渲染集成**: 在游戏渲染流程中自动渲染视野效果
4. **键盘控制**: 支持实时调整视野参数

## 自定义扩展

### 添加新的视野效果

```python
class CustomVisionSystem(VisionSystem):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 添加自定义属性
        
    def custom_render(self, screen):
        # 自定义渲染逻辑
        pass
```

### 视野效果组合

```python
# 创建多个视野系统
vision_system_1 = VisionSystem(radius=200, angle=60)
vision_system_2 = VisionSystem(radius=400, angle=30)

# 组合渲染
for vision in [vision_system_1, vision_system_2]:
    vision.render(screen, dark_overlay.get_overlay())
```

## 故障排除

### 常见问题

1. **视野不显示**
   - 检查 `enable_vision` 是否为 `True`
   - 确认视野系统已正确初始化

2. **性能问题**
   - 减少视野半径
   - 降低视野角度
   - 减少顶点数量

3. **视觉效果异常**
   - 检查颜色值是否在有效范围
   - 确认透明度设置正确

### 调试模式

```python
# 启用调试信息
vision_system.debug = True

# 显示视野边界
vision_system.show_boundaries = True
```

## 配置文件

### 基础配置

所有视野系统参数都集中在 `src/modules/vision_config.py` 文件中：

```python
VISION_CONFIG = {
    "enabled": True,                    # 视野系统开关
    "sector": {                        # 扇形视野参数
        "radius": 300,                 # 半径
        "angle": 90,                   # 角度
        "color": (255, 255, 255, 128), # 颜色
    },
    "circle": {                        # 圆形区域参数
        "radius": 80,                  # 半径
        "color": (255, 255, 255, 128), # 颜色
    },
    "darkness": {                      # 黑暗遮罩参数
        "alpha": 200,                  # 透明度
    },
    # ... 更多配置
}
```

### 预设配置

系统提供了多种预设配置：

- **default**: 默认视野
- **wide**: 宽视野
- **narrow**: 窄视野
- **night_vision**: 夜视模式
- **tunnel**: 隧道视野

### 颜色主题

支持多种颜色主题：

- **default**: 白色
- **warm**: 暖黄色
- **cool**: 冷蓝色
- **green**: 绿色

### 配置管理

使用配置管理脚本：

```bash
python vision_config_manager.py
```

功能包括：
- 查看当前配置
- 修改参数
- 应用预设
- 应用颜色主题
- 保存/加载配置

## 版本历史

- v1.0: 基础扇形视野系统
- v1.1: 添加黑暗遮罩效果
- v1.2: 性能优化和键盘控制
- v1.3: 集成到主游戏系统
- v1.4: 添加配置文件系统 
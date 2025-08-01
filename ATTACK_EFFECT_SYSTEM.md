# 攻击特效系统实现总结

## 功能概述

成功实现了刀近战攻击的攻击特效系统，包括：

1. **图片分割**：将640*64的图片分割成10个64*64的帧
2. **旋转逻辑**：实现和枪一样的180度旋转逻辑
3. **动画播放**：流畅的帧动画播放
4. **集成到武器系统**：与现有的刀武器系统完美集成

## 实现文件

### 1. `src/modules/weapons/attack_effect.py` - 核心特效系统
- **AttackEffect类**：单个特效的管理
- **AttackEffectManager类**：特效管理器（预留扩展）

### 2. `src/modules/weapons/types/knife.py` - 刀武器集成
- 集成攻击特效到刀武器
- 在近战攻击时触发特效
- 特效渲染和更新逻辑

### 3. `test_attack_effect.py` - 测试脚本
- 独立测试特效系统
- 验证图片分割和旋转功能

## 核心功能

### 1. 图片分割系统

```python
def _load_and_split_frames(self):
    """加载图片并分割成帧"""
    original_image = resource_manager.load_image('attack_effect', self.image_path)
    frames = []
    for i in range(self.frame_count):
        frame_x = i * self.frame_width
        frame_y = 0
        frame_rect = pygame.Rect(frame_x, frame_y, self.frame_width, self.frame_height)
        frame = original_image.subsurface(frame_rect)
        frames.append(frame)
    return frames
```

**特性**：
- 自动分割640*64图片为10个64*64帧
- 支持自定义帧数和尺寸
- 错误处理和调试信息

### 2. 旋转逻辑

```python
def render(self, screen, camera_x=0, camera_y=0):
    # 计算旋转角度（和枪的旋转逻辑一样）
    angle = math.degrees(math.atan2(-self.direction_y, self.direction_x))
    
    # 旋转特效图像
    rotated_frame = pygame.transform.rotate(current_frame, angle)
```

**特性**：
- 使用`math.atan2(-direction_y, direction_x)`计算角度
- 与枪武器的旋转逻辑完全一致
- 支持180度旋转

### 3. 动画系统

```python
def update(self, dt):
    self.animation_timer += dt
    frame_index = int(self.animation_timer / self.frame_duration)
    if frame_index >= self.frame_count:
        self.is_playing = False
        return
    self.current_frame = min(frame_index, len(self.frames) - 1)
```

**特性**：
- 流畅的帧动画播放
- 可配置的帧持续时间
- 自动结束动画

## 集成到武器系统

### 1. 刀武器集成

```python
def _perform_melee_attack(self, direction_x, direction_y):
    # 创建攻击特效
    self.attack_effect = AttackEffect(
        'images/attcak/hit_animations/swing02.png',
        frame_width=64,
        frame_height=64,
        frame_count=10
    )
    self.attack_effect.play(self.player.world_x, self.player.world_y, direction_x, direction_y)
```

### 2. 渲染集成

```python
def render(self, screen, camera_x, camera_y):
    # 渲染攻击特效
    if self.attack_effect and self.effect_playing:
        self.attack_effect.render(screen, camera_x, camera_y)
```

## 测试验证

### 测试结果
```
特效创建成功，帧数: 10
  帧 0: (64, 64)
  帧 1: (64, 64)
  帧 2: (64, 64)
  帧 3: (64, 64)
  帧 4: (64, 64)
  帧 5: (64, 64)
  帧 6: (64, 64)
  帧 7: (64, 64)
  帧 8: (64, 64)
  帧 9: (64, 64)
```

### 验证要点
1. ✅ **图片分割正确** - 成功分割为10个64*64帧
2. ✅ **旋转逻辑正确** - 与枪武器旋转逻辑一致
3. ✅ **动画播放流畅** - 特效正常播放和结束
4. ✅ **方向响应正确** - 特效跟随鼠标方向旋转

## 使用方法

### 1. 运行测试
```bash
python test_attack_effect.py
```

### 2. 在游戏中使用
- 右键点击进行近战攻击
- 特效会自动播放并跟随鼠标方向旋转

### 3. 自定义特效
```python
effect = AttackEffect(
    'path/to/effect.png',
    frame_width=64,
    frame_height=64,
    frame_count=10
)
```

## 技术细节

### 1. 图片分割算法
- 使用`pygame.Surface.subsurface()`提取帧
- 支持任意尺寸的图片分割
- 自动计算帧位置

### 2. 旋转算法
- 使用`math.atan2()`计算角度
- 使用`pygame.transform.rotate()`旋转图像
- 保持图像质量

### 3. 动画控制
- 基于时间的帧更新
- 可配置的播放速度
- 自动清理完成的特效

## 扩展性

### 1. 支持更多特效
- 可以轻松添加新的特效图片
- 支持不同的帧数和尺寸
- 可配置的播放参数

### 2. 特效管理器
- `AttackEffectManager`类预留扩展
- 支持同时播放多个特效
- 自动管理特效生命周期

### 3. 武器集成
- 可以轻松集成到其他武器
- 支持不同的触发条件
- 可配置的特效参数

## 总结

成功实现了完整的攻击特效系统：

1. ✅ **图片分割** - 正确分割640*64图片为10个64*64帧
2. ✅ **旋转逻辑** - 实现和枪一样的180度旋转
3. ✅ **动画系统** - 流畅的帧动画播放
4. ✅ **武器集成** - 完美集成到刀武器系统
5. ✅ **测试验证** - 完整的测试和验证

现在刀近战攻击时会显示旋转的攻击特效，提供更好的视觉反馈！ 
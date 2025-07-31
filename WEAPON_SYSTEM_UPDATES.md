# 武器系统更新说明

## 概述

根据用户要求，对武器系统进行了以下更新：

1. **取消刀攻击特效**：移除了刀武器的 `swing02.png` 攻击特效
2. **手枪位置和朝向调整**：根据鼠标位置动态调整手枪的位置和朝向

## 详细修改

### 1. 刀武器修改 (`src/modules/weapons/types/knife.py`)

#### 移除攻击特效
- **移除特效加载**：删除了 `self.attack_effect = resource_manager.load_image('attack_effect', 'images/attcak/hit_animations/swing02.png')`
- **简化渲染方法**：`render` 方法现在只返回 `pass`，不再渲染特效
- **保留近战攻击**：刀武器仍然可以进行近战攻击，但不再显示特效动画

#### 修改内容：
```python
# 移除特效加载
# self.attack_effect = resource_manager.load_image('attack_effect', 'images/attcak/hit_animations/swing02.png')

# 简化渲染方法
def render(self, screen, camera_x, camera_y):
    # 刀武器只进行近战攻击，不渲染特效
    pass
```

### 2. 手枪武器修改 (`src/modules/weapons/types/bullet.py`)

#### 动态位置和朝向调整
- **移除固定偏移**：不再使用固定的 `weapon_offset_x` 和 `weapon_offset_y`
- **根据鼠标位置调整**：枪的位置根据鼠标相对于玩家的方向动态计算
- **实时朝向调整**：枪的旋转角度根据鼠标方向实时计算

#### 核心逻辑：
```python
def _render_weapon_attack(self, screen, camera_x, camera_y):
    # 获取鼠标位置
    mouse_x, mouse_y = pygame.mouse.get_pos()
    
    # 计算鼠标相对于玩家的方向
    direction_x = mouse_x - player_screen_x
    direction_y = mouse_y - player_screen_y
    
    # 标准化方向向量
    length = math.sqrt(direction_x**2 + direction_y**2)
    if length > 0:
        direction_x /= length
        direction_y /= length
    
    # 根据鼠标位置调整枪的位置
    weapon_distance = 25  # 枪与玩家的距离
    weapon_screen_x = player_screen_x + direction_x * weapon_distance
    weapon_screen_y = player_screen_y + direction_y * weapon_distance
    
    # 计算枪的旋转角度（枪口朝向鼠标）
    angle = math.degrees(math.atan2(-direction_y, direction_x))
    
    # 应用旋转
    rotated_image = pygame.transform.rotate(weapon_image, angle)
```

#### 移除复杂旋转逻辑
- **移除上抬30度限制**：不再强制枪上抬30度
- **简化攻击逻辑**：移除了复杂的旋转动画和状态管理
- **直接朝向鼠标**：枪直接朝向鼠标位置

### 3. 武器行为总结

#### 手枪（远程武器）
- **触发方式**：鼠标左键
- **位置调整**：
  - 鼠标在左 → 枪在玩家左侧
  - 鼠标在右 → 枪在玩家右侧
  - 鼠标在上 → 枪口朝上
  - 鼠标在下 → 枪口朝下
- **朝向**：枪口始终朝向鼠标位置
- **功能**：只进行远程攻击，无近战能力

#### 刀（近战武器）
- **触发方式**：鼠标右键
- **特效**：无攻击特效
- **功能**：只进行近战攻击，无远程能力

## 测试验证

### 运行测试脚本
```bash
python test_updated_weapon_system.py
```

### 测试功能
1. **手枪位置调整**：移动鼠标，观察枪的位置变化
2. **手枪朝向调整**：移动鼠标，观察枪口朝向变化
3. **刀攻击**：右键测试近战攻击（无特效）
4. **双武器系统**：确认左键触发手枪，右键触发刀

## 技术细节

### 坐标系统
- **屏幕坐标**：鼠标位置使用屏幕坐标
- **玩家中心**：玩家始终在屏幕中心
- **相对位置**：枪的位置相对于玩家中心计算

### 角度计算
- **鼠标方向**：`math.atan2(-direction_y, direction_x)`
- **枪的旋转**：`math.degrees(angle)`
- **标准化**：确保方向向量的长度为1

### 性能优化
- **简化渲染**：刀武器不再渲染特效，提高性能
- **减少计算**：手枪移除了复杂的旋转动画计算
- **实时更新**：枪的位置和朝向实时跟随鼠标

## 文件修改清单

1. `src/modules/weapons/types/knife.py` - 移除刀攻击特效
2. `src/modules/weapons/types/bullet.py` - 修改手枪位置和朝向逻辑
3. `test_updated_weapon_system.py` - 新增测试脚本

## 注意事项

1. **图像资源**：确保 `knife.png` 和 `gun.png` 文件存在
2. **鼠标灵敏度**：枪的位置变化跟随鼠标移动
3. **攻击范围**：刀的攻击范围保持不变
4. **子弹轨迹**：子弹仍然从枪口位置发射

## 未来扩展

1. **武器切换**：可以添加武器切换功能
2. **更多武器类型**：可以添加更多远程和近战武器
3. **特效系统**：可以为其他武器添加特效
4. **音效系统**：可以添加武器音效 
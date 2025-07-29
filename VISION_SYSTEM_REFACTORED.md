# 视野系统重构说明

## 🎯 **重构目标**

将视野系统的配置管理功能从游戏类移动到视野系统类本身，实现更好的面向对象设计。

## 📁 **文件结构**

```
src/modules/
├── vision_system.py          # 视野系统核心类（已重构）
├── vision_config.py          # 配置管理模块
└── game.py                   # 游戏主类（已简化）

vision_config_manager.py      # 配置管理脚本
vision_system_example.py      # 使用示例
```

## 🔧 **重构内容**

### 1. **VisionSystem 类增强**

#### **新增配置管理属性**
```python
self.config = {
    "sector": {"radius": radius, "angle": math.degrees(self.angle), "color": color},
    "circle": {"radius": circle_radius, "color": circle_color},
    "enabled": True
}
```

#### **新增配置管理方法**
```python
def set_radius(self, radius)           # 设置视野半径
def set_angle(self, angle)             # 设置视野角度
def toggle_enabled(self)               # 切换启用状态
def is_enabled(self)                   # 检查是否启用
def get_config(self)                   # 获取当前配置
def apply_config(self, config)         # 应用配置
```

### 2. **DarkOverlay 类增强**

#### **新增配置管理方法**
```python
def get_config(self)                   # 获取当前配置
def apply_config(self, config)         # 应用配置
```

### 3. **Game 类简化**

#### **移除的代码**
- 移除了 `self.vision_config` 属性
- 移除了 `_reinit_vision_system()` 方法
- 简化了所有视野系统相关方法

#### **简化的方法**
```python
def set_vision_radius(self, radius):
    if self.vision_system:
        self.vision_system.set_radius(radius)

def toggle_vision(self):
    if self.vision_system:
        self.enable_vision = self.vision_system.toggle_enabled()

def apply_vision_preset(self, preset_name):
    new_config = apply_preset(preset_name)
    if self.vision_system:
        self.vision_system.apply_config(new_config)
    if self.dark_overlay:
        self.dark_overlay.apply_config(new_config)
```

## 🎮 **使用方法**

### **1. 基本使用**

```python
# 创建视野系统
vision_system = VisionSystem()
dark_overlay = DarkOverlay(screen_width, screen_height)

# 更新视野
vision_system.update(player_x, player_y, mouse_x, mouse_y)

# 渲染
vision_system.render(screen, dark_overlay.get_overlay())
```

### **2. 配置管理**

```python
# 获取当前配置
config = vision_system.get_config()

# 应用配置
vision_system.apply_config(new_config)

# 切换启用状态
enabled = vision_system.toggle_enabled()

# 检查是否启用
if vision_system.is_enabled():
    # 渲染视野
    pass
```

### **3. 预设和主题**

```python
from src.modules.vision_config import apply_preset, apply_color_theme

# 应用预设
config = apply_preset("night_vision")
vision_system.apply_config(config)

# 应用颜色主题
config = apply_color_theme("warm")
vision_system.apply_config(config)
```

### **4. 在游戏中使用**

```python
# 键盘控制
if event.key == pygame.K_F3:
    self.toggle_vision()  # 切换视野系统

if event.key == pygame.K_F4:
    self.set_vision_radius(400)  # 设置视野半径

# 应用预设
self.apply_vision_preset("night_vision")
```

## 🚀 **优势**

### **1. 更好的封装**
- 配置管理逻辑集中在视野系统类中
- 游戏类不需要了解配置细节

### **2. 更简洁的接口**
- 游戏类的方法更简洁
- 减少了代码重复

### **3. 更好的可维护性**
- 配置变更只需要修改视野系统类
- 更容易进行单元测试

### **4. 更好的扩展性**
- 可以轻松添加新的配置选项
- 可以轻松添加新的预设和主题

## 📝 **示例运行**

### **运行示例程序**
```bash
python vision_system_example.py
```

### **运行配置管理器**
```bash
python vision_config_manager.py
```

### **在游戏中使用**
```bash
python src/main.py
```

## 🔄 **迁移指南**

如果你有现有的视野系统代码，迁移很简单：

### **旧代码**
```python
# 游戏类中的方法
def set_vision_radius(self, radius):
    self.vision_config["sector"]["radius"] = radius
    if self.vision_system:
        self.vision_system.set_radius(radius)
```

### **新代码**
```python
# 游戏类中的方法
def set_vision_radius(self, radius):
    if self.vision_system:
        self.vision_system.set_radius(radius)
```

配置管理现在由视野系统类自动处理！

## 🎯 **总结**

这次重构实现了：
- ✅ 更好的面向对象设计
- ✅ 更简洁的游戏类代码
- ✅ 更集中的配置管理
- ✅ 更好的可维护性和扩展性
- ✅ 保持了所有原有功能

视野系统现在更加模块化和易于使用！ 
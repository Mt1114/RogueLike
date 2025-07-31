# 波次系统功能说明

## 概述

根据用户要求，实现了完整的波次怪物生成系统：

1. **第一波**：0:00-0:30，正常生成速度，正常属性
2. **休息期**：0:30-1:30，不生成怪物
3. **第二波**：1:30-3:00，生成速度加快50%，怪物体力上升20%，攻击力上升20%
4. **休息期**：3:00-4:00，不生成怪物
5. **第三波**：4:00-5:00，生成速度加快100%，怪物攻击力上升50%，不提升体力
6. **游戏结束**：5:00后，显示"You are safe!!!!"

## 详细功能

### 1. 波次时间安排

#### 第一波（Round 1）
- **时间**：0:00-0:30
- **生成间隔**：3.0秒
- **属性加成**：无
- **提示消息**：Round 1

#### 休息期
- **时间**：0:30-1:30
- **生成**：停止生成怪物
- **状态**：清理现有敌人

#### 第二波（Round 2）
- **时间**：1:30-3:00
- **生成间隔**：2.0秒（加快50%）
- **生命值加成**：+20%
- **攻击力加成**：+20%
- **提示消息**：Round 2

#### 休息期
- **时间**：3:00-4:00
- **生成**：停止生成怪物
- **状态**：清理现有敌人

#### 第三波（Round 3）
- **时间**：4:00-5:00
- **生成间隔**：1.5秒（加快100%）
- **生命值加成**：无
- **攻击力加成**：+50%
- **提示消息**：Round 3

#### 游戏结束
- **时间**：5:00后
- **生成**：停止生成怪物
- **提示消息**：You are safe!!!!

### 2. 波次系统实现

#### 核心属性
```python
# 波次系统
self.current_round = 0  # 当前波次
self.round_start_time = 0  # 当前波次开始时间
self.round_messages = []  # 波次提示消息
self.message_timer = 0  # 消息显示计时器
```

#### 波次更新逻辑
```python
def _update_round_system(self, dt, player):
    """更新波次系统"""
    game_time_minutes = self.game_time / 60.0
    
    # 第一波：0:00-0:30
    if game_time_minutes >= 0 and game_time_minutes < 0.5 and self.current_round == 0:
        self._start_round(1, "Round 1", 3.0, 1.0, 1.0)
        
    # 第一波结束，进入休息期：0:30-1:30
    elif game_time_minutes >= 0.5 and game_time_minutes < 1.5 and self.current_round == 1:
        self._end_round()
        
    # 第二波：1:30-3:00
    elif game_time_minutes >= 1.5 and game_time_minutes < 3.0 and self.current_round == 0:
        self._start_round(2, "Round 2", 2.0, 1.2, 1.2)
        
    # 第二波结束，进入休息期：3:00-4:00
    elif game_time_minutes >= 3.0 and game_time_minutes < 4.0 and self.current_round == 2:
        self._end_round()
        
    # 第三波：4:00-5:00
    elif game_time_minutes >= 4.0 and game_time_minutes < 5.0 and self.current_round == 0:
        self._start_round(3, "Round 3", 1.5, 1.0, 1.5)
        
    # 游戏结束：5:00后
    elif game_time_minutes >= 5.0 and self.current_round != -1:
        self._end_game()
```

### 3. 敌人属性加成

#### 属性应用
```python
def spawn_enemy(self, enemy_type, x, y, health=None):
    # 应用波次属性加成
    if enemy and hasattr(self, 'health_multiplier') and hasattr(self, 'damage_multiplier'):
        # 应用生命值加成
        enemy.health = int(enemy.health * self.health_multiplier)
        enemy.max_health = int(enemy.max_health * self.health_multiplier)
        
        # 应用攻击力加成
        if hasattr(enemy, 'damage'):
            enemy.damage = int(enemy.damage * self.damage_multiplier)
```

#### 波次属性配置
- **Round 1**：生命值倍数 1.0，攻击力倍数 1.0
- **Round 2**：生命值倍数 1.2，攻击力倍数 1.2
- **Round 3**：生命值倍数 1.0，攻击力倍数 1.5

### 4. 消息显示系统

#### 消息渲染
```python
def _render_round_messages(self, screen):
    """渲染波次消息"""
    for message in self.round_messages[:]:
        # 更新消息计时器
        message['timer'] += 0.016
        
        # 移除过期的消息
        if message['timer'] >= message['duration']:
            self.round_messages.remove(message)
            continue
            
        # 渲染消息
        font = pygame.font.Font(None, 48)
        text_surface = font.render(message['text'], True, message['color'])
        
        # 计算消息位置（屏幕中央）
        text_rect = text_surface.get_rect()
        text_rect.centerx = screen.get_width() // 2
        text_rect.centery = screen.get_height() // 2
        
        # 添加透明度效果
        alpha = 255
        if message['timer'] > message['duration'] * 0.7:
            alpha = int(255 * (1 - (message['timer'] - message['duration'] * 0.7) / (message['duration'] * 0.3)))
        
        if alpha < 255:
            text_surface.set_alpha(alpha)
        
        screen.blit(text_surface, text_rect)
```

#### 消息类型
- **波次开始**：黄色文字，显示3秒
- **游戏结束**：绿色文字，显示5秒

### 5. 生成控制

#### 生成条件
```python
# 根据波次状态决定是否生成敌人
if self.current_round > 0 and self.current_round <= 3:
    if self.spawn_timer >= self.spawn_interval:
        self.spawn_timer = 0
        self.random_spawn_enemy(player)
```

#### 生成间隔
- **Round 1**：3.0秒
- **Round 2**：2.0秒（加快50%）
- **Round 3**：1.5秒（加快100%）

## 使用方法

### 1. 游戏流程
1. **开始游戏**：立即开始第一波
2. **第一波**：0:00-0:30，正常难度
3. **休息期**：0:30-1:30，清理敌人
4. **第二波**：1:30-3:00，难度提升
5. **休息期**：3:00-4:00，清理敌人
6. **第三波**：4:00-5:00，最高难度
7. **游戏结束**：5:00后，显示胜利消息

### 2. 测试功能
```bash
python test_round_system.py
```

### 3. 测试控制
- **空格**：暂停/继续
- **1-4**：时间加速 (1x, 2x, 5x, 10x)
- **ESC**：退出

## 技术细节

### 文件修改清单

1. **`src/modules/enemies/enemy_manager.py`**：
   - 添加波次系统属性
   - 实现波次更新逻辑
   - 添加敌人属性加成
   - 实现消息显示系统
   - 修改生成控制逻辑

2. **`test_round_system.py`**：
   - 新增波次系统测试脚本
   - 支持时间加速测试
   - 显示波次状态信息

### 系统集成

#### 敌人管理器
- 支持波次时间控制
- 自动应用属性加成
- 管理消息显示

#### 游戏主循环
- 调用波次更新
- 渲染波次消息
- 控制敌人生成

## 注意事项

1. **时间精度**：使用分钟为单位进行时间计算
2. **属性加成**：整数化处理，避免小数
3. **消息显示**：支持透明度和阴影效果
4. **生成控制**：只在波次期间生成敌人

## 未来扩展

1. **更多波次**：可以添加更多波次
2. **特殊敌人**：在特定波次生成特殊敌人
3. **奖励系统**：完成波次获得奖励
4. **难度调整**：根据玩家表现调整难度

## 性能优化

1. **消息管理**：及时清理过期消息
2. **生成控制**：只在需要时生成敌人
3. **属性缓存**：缓存波次属性避免重复计算
4. **渲染优化**：只渲染可见消息 
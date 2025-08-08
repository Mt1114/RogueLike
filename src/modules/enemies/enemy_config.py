"""
敌人配置文件
定义所有敌人的基础属性、技能和难度相关的缩放系数
"""

# 全局难度系数设置
DIFFICULTY_MULTIPLIERS = {
    "health": {  # 健康值随难度增长的系数
        "easy": 0.8,
        "normal": 1.0,
        "hard": 1.3,
        "nightmare": 1.8
    },
    "damage": {  # 伤害值随难度增长的系数
        "easy": 0.7,
        "normal": 1.0,
        "hard": 1.5,
        "nightmare": 2.0
    },
    "speed": {  # 速度随难度增长的系数
        "easy": 0.9,
        "normal": 1.0,
        "hard": 1.2,
        "nightmare": 1.5
    }
}

# 敌人等级系数 (游戏时间增加时应用)
LEVEL_SCALING = {
    "health_per_level": 0.15,  # 每级增加15%生命值
    "damage_per_level": 0.1,  # 每级增加8%伤害
    "speed_per_level": 0.01,   # 每级增加3%速度
}

# 敌人基础配置
ENEMY_CONFIGS = {
    # 幽灵 - 基础敌人
    "ghost": {
        "health": 80,           # 基础生命值
        "damage": 4,           # 基础伤害
        "speed": 150,           # 基础移动速度
        "score_value": 50,      # 击败后获得的分数
        "exp_value": 5,        # 击败后获得的经验值（5个敌人升一级）
        "animation_speed": 0.0333, # 动画速度
        "scale": 1.0,           # 缩放大小
    },
    
    # 萝卜 - 较慢但更健壮的敌人
    "radish": {
        "health": 150,
        "damage": 5,
        "speed": 120,
        "score_value": 15,
        "exp_value": 5,        # 击败后获得的经验值（5个敌人升一级）
        "animation_speed": 0.0333,
        "scale": 1.0,
    },
    
    # 蝙蝠 - 快速但脆弱的敌人
    "bat": {
        "health": 60,
        "damage": 7,
        "speed": 160,
        "score_value": 80,
        "exp_value": 5,        # 击败后获得的经验值（5个敌人升一级）
        "animation_speed": 0.0333,
        "scale": 2.0,
    },
    
    # 史莱姆 - 远程攻击敌人
    "slime": {
        "health": 40,
        "damage": 6,
        "speed": 120,
        "score_value": 150,
        "exp_value": 5,        # 击败后获得的经验值（5个敌人升一级）
        "animation_speed": 0.0333,
        "scale": 1.0,
        "attack_range": 800,    # 攻击范围
        "min_attack_range": 300, # 最小攻击距离
        "attack_cooldown": 2.0,  # 攻击冷却时间(秒)
        "projectile_speed": 180, # 投射物速度
    },
    
    # 灵魂 - 最强大的敌人
    "soul": {
        "health": 1000,
        "damage": 50,
        "speed": 100,
        "score_value": 150,
        "exp_value": 200,        
        "animation_speed": 0.0333,
        "scale": 1.0,
        "attack_range": 1800,    # 攻击范围
        "min_attack_range": 0, # 最小攻击距离
        "attack_cooldown": 0.5,  # 攻击冷却时间(秒)
        "projectile_speed": 150, # 投射物速度
    },
    

}

def get_enemy_config(enemy_type, difficulty="normal", level=1):
    """
    获取指定类型、难度和等级的敌人配置
    
    Args:
        enemy_type (str): 敌人类型
        difficulty (str): 游戏难度 ('easy', 'normal', 'hard', 'nightmare')
        level (int): 游戏当前等级
        
    Returns:
        dict: 包含敌人属性的字典
    """
    # 获取基础配置
    if enemy_type not in ENEMY_CONFIGS:
        raise ValueError(f"未知的敌人类型: {enemy_type}")
    
    config = ENEMY_CONFIGS[enemy_type].copy()
    
    # 记录基础属性
    base_health = config["health"]
    base_damage = config["damage"]
    base_speed = config["speed"]
    
    # 应用难度系数
    if difficulty in DIFFICULTY_MULTIPLIERS["health"]:
        config["health"] *= DIFFICULTY_MULTIPLIERS["health"][difficulty]
        config["damage"] *= DIFFICULTY_MULTIPLIERS["damage"][difficulty]
        config["speed"] *= DIFFICULTY_MULTIPLIERS["speed"][difficulty]
    
    # 应用等级系数
    if level > 1:
        level_factor = level - 1  # 从第2级开始计算额外加成
        config["health"] *= (1 + LEVEL_SCALING["health_per_level"] * level_factor)
        config["damage"] *= (1 + LEVEL_SCALING["damage_per_level"] * level_factor)
        config["speed"] *= (1 + LEVEL_SCALING["speed_per_level"] * level_factor)
        
        
    
    # 确保数值合理
    config["health"] = round(config["health"])
    config["damage"] = round(config["damage"])
    config["speed"] = round(config["speed"])
    
    return config 
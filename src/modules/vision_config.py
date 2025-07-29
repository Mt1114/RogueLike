"""
视野系统配置文件
包含所有视野相关的参数设置
"""

# 视野系统基础配置
VISION_CONFIG = {
    # 视野开关
    "enabled": True,
    
    # 扇形视野参数
    "sector": {
        "radius": 300,        # 扇形视野半径（像素）
        "angle": 90,          # 扇形视野角度（度）
        "color": (255, 255, 255, 128),  # 扇形区域透明度 (R, G, B, A)
    },
    
    # 圆形区域参数
    "circle": {
        "radius": 80,         # 圆形区域半径（像素）
        "color": (255, 255, 255, 128),  # 圆形区域透明度 (R, G, B, A)
    },
    
    # 黑暗遮罩参数
    "darkness": {
        "alpha": 200,         # 黑暗程度 (0-255)
    },
    
    # 键盘控制配置
    "controls": {
        "toggle_key": "F3",           # 切换视野系统
        "sector_radius_up": "F4",     # 增加扇形视野半径
        "sector_radius_down": "F5",   # 减少扇形视野半径
        "sector_angle_up": "F6",      # 增加扇形视野角度
        "sector_angle_down": "F7",    # 减少扇形视野角度
        "circle_radius_up": "F8",     # 增加圆形区域半径
        "circle_radius_down": "F9",   # 减少圆形区域半径
    },
    
    # 调整步长
    "adjustments": {
        "sector_radius_step": 50,     # 扇形视野半径调整步长
        "sector_angle_step": 15,      # 扇形视野角度调整步长（度）
        "circle_radius_step": 20,     # 圆形区域半径调整步长
        "darkness_step": 20,          # 黑暗程度调整步长
    },
    
    # 限制范围
    "limits": {
        "sector_radius_min": 100,     # 扇形视野半径最小值
        "sector_radius_max": 800,     # 扇形视野半径最大值
        "sector_angle_min": 30,       # 扇形视野角度最小值（度）
        "sector_angle_max": 360,      # 扇形视野角度最大值（度）
        "circle_radius_min": 20,      # 圆形区域半径最小值
        "circle_radius_max": 200,     # 圆形区域半径最大值
        "darkness_min": 0,            # 黑暗程度最小值
        "darkness_max": 255,          # 黑暗程度最大值
    }
}

# 预设配置
VISION_PRESETS = {
    "default": {
        "name": "默认视野",
        "sector_radius": 300,
        "sector_angle": 90,
        "circle_radius": 80,
        "darkness_alpha": 200,
    },
    "wide": {
        "name": "宽视野",
        "sector_radius": 400,
        "sector_angle": 120,
        "circle_radius": 100,
        "darkness_alpha": 180,
    },
    "narrow": {
        "name": "窄视野",
        "sector_radius": 200,
        "sector_angle": 60,
        "circle_radius": 60,
        "darkness_alpha": 220,
    },
    "night_vision": {
        "name": "夜视模式",
        "sector_radius": 500,
        "sector_angle": 180,
        "circle_radius": 120,
        "darkness_alpha": 150,
    },
    "tunnel": {
        "name": "隧道视野",
        "sector_radius": 250,
        "sector_angle": 45,
        "circle_radius": 40,
        "darkness_alpha": 240,
    }
}

# 颜色主题
VISION_COLORS = {
    "default": {
        "sector_color": (255, 255, 255, 128),  # 白色半透明
        "circle_color": (255, 255, 255, 128),  # 白色半透明
    },
    "warm": {
        "sector_color": (255, 255, 200, 128),  # 暖黄色
        "circle_color": (255, 255, 200, 128),
    },
    "cool": {
        "sector_color": (200, 200, 255, 128),  # 冷蓝色
        "circle_color": (200, 200, 255, 128),
    },
    "green": {
        "sector_color": (200, 255, 200, 128),  # 绿色
        "circle_color": (200, 255, 200, 128),
    }
}

def get_vision_config():
    """获取视野配置"""
    return VISION_CONFIG.copy()

def get_vision_presets():
    """获取视野预设"""
    return VISION_PRESETS.copy()

def get_vision_colors():
    """获取颜色主题"""
    return VISION_COLORS.copy()

def apply_preset(preset_name):
    """应用预设配置"""
    if preset_name in VISION_PRESETS:
        preset = VISION_PRESETS[preset_name]
        config = VISION_CONFIG.copy()
        
        # 应用预设参数
        config["sector"]["radius"] = preset["sector_radius"]
        config["sector"]["angle"] = preset["sector_angle"]
        config["circle"]["radius"] = preset["circle_radius"]
        config["darkness"]["alpha"] = preset["darkness_alpha"]
        
        return config
    return VISION_CONFIG.copy()

def apply_color_theme(theme_name):
    """应用颜色主题"""
    if theme_name in VISION_COLORS:
        theme = VISION_COLORS[theme_name]
        config = VISION_CONFIG.copy()
        
        # 应用颜色主题
        config["sector"]["color"] = theme["sector_color"]
        config["circle"]["color"] = theme["circle_color"]
        
        return config
    return VISION_CONFIG.copy()

def validate_config(config):
    """验证配置参数"""
    limits = config["limits"]
    
    # 检查扇形视野半径
    sector_radius = config["sector"]["radius"]
    if not (limits["sector_radius_min"] <= sector_radius <= limits["sector_radius_max"]):
        config["sector"]["radius"] = max(limits["sector_radius_min"], 
                                       min(sector_radius, limits["sector_radius_max"]))
    
    # 检查扇形视野角度
    sector_angle = config["sector"]["angle"]
    if not (limits["sector_angle_min"] <= sector_angle <= limits["sector_angle_max"]):
        config["sector"]["angle"] = max(limits["sector_angle_min"], 
                                      min(sector_angle, limits["sector_angle_max"]))
    
    # 检查圆形区域半径
    circle_radius = config["circle"]["radius"]
    if not (limits["circle_radius_min"] <= circle_radius <= limits["circle_radius_max"]):
        config["circle"]["radius"] = max(limits["circle_radius_min"], 
                                       min(circle_radius, limits["circle_radius_max"]))
    
    # 检查黑暗程度
    darkness_alpha = config["darkness"]["alpha"]
    if not (limits["darkness_min"] <= darkness_alpha <= limits["darkness_max"]):
        config["darkness"]["alpha"] = max(limits["darkness_min"], 
                                        min(darkness_alpha, limits["darkness_max"]))
    
    return config 
# 光照系统配置文件

# 默认光照配置
DEFAULT_LIGHTING_CONFIG = {
    # 基础光照设置
    "light_size": 200,           # 光照大小
    "light_intensity": 100,      # 光照强度 (0-255)
    "light_color": (255, 255, 255),  # 光照颜色 (R, G, B)
    
    # 玩家光照设置
    "player_light_radius": 100,  # 玩家光照半径
    
    # 鼠标光照设置
    "mouse_light_angle": 90,     # 扇形角度 (度)
    "mouse_light_radius": 150,   # 鼠标光照半径
    
    # 全局黑暗设置
    "darkness_intensity": 150,   # 黑暗强度 (0-255)
}

# 光照预设
LIGHTING_PRESETS = {
    "default": {
        "name": "默认",
        "config": DEFAULT_LIGHTING_CONFIG.copy()
    },
    
    "night_vision": {
        "name": "夜视模式",
        "config": {
            "light_size": 300,
            "light_intensity": 150,
            "light_color": (0, 255, 0),  # 绿色夜视
            "player_light_radius": 150,
            "mouse_light_angle": 120,
            "mouse_light_radius": 200,
            "darkness_intensity": 200,
        }
    },
    
    "tunnel_vision": {
        "name": "隧道视野",
        "config": {
            "light_size": 150,
            "light_intensity": 80,
            "light_color": (255, 255, 255),
            "player_light_radius": 60,
            "mouse_light_angle": 45,
            "mouse_light_radius": 100,
            "darkness_intensity": 180,
        }
    },
    
    "warm_light": {
        "name": "温暖光照",
        "config": {
            "light_size": 250,
            "light_intensity": 120,
            "light_color": (255, 200, 100),  # 暖黄色
            "player_light_radius": 120,
            "mouse_light_angle": 90,
            "mouse_light_radius": 180,
            "darkness_intensity": 120,
        }
    },
    
    "cold_light": {
        "name": "冷光模式",
        "config": {
            "light_size": 200,
            "light_intensity": 100,
            "light_color": (100, 150, 255),  # 冷蓝色
            "player_light_radius": 100,
            "mouse_light_angle": 90,
            "mouse_light_radius": 150,
            "darkness_intensity": 150,
        }
    }
}

# 颜色主题
LIGHTING_COLORS = {
    "white": (255, 255, 255),
    "green": (0, 255, 0),
    "blue": (100, 150, 255),
    "yellow": (255, 255, 0),
    "orange": (255, 150, 0),
    "red": (255, 100, 100),
    "purple": (200, 100, 255),
    "cyan": (0, 255, 255),
}

def get_lighting_config():
    """获取默认光照配置"""
    return DEFAULT_LIGHTING_CONFIG.copy()

def apply_preset(preset_name, lighting_manager):
    """应用光照预设
    
    Args:
        preset_name (str): 预设名称
        lighting_manager: 光照管理器实例
    """
    if preset_name in LIGHTING_PRESETS:
        config = LIGHTING_PRESETS[preset_name]["config"]
        lighting_manager.set_light_config(**config)
        return True
    return False

def apply_color_theme(color_name, lighting_manager):
    """应用颜色主题
    
    Args:
        color_name (str): 颜色名称
        lighting_manager: 光照管理器实例
    """
    if color_name in LIGHTING_COLORS:
        lighting_manager.set_light_config(light_color=LIGHTING_COLORS[color_name])
        return True
    return False

def get_available_presets():
    """获取可用的预设列表"""
    return list(LIGHTING_PRESETS.keys())

def get_available_colors():
    """获取可用的颜色列表"""
    return list(LIGHTING_COLORS.keys())

def validate_config(config):
    """验证光照配置
    
    Args:
        config (dict): 光照配置
        
    Returns:
        bool: 配置是否有效
    """
    required_keys = [
        "light_size", "light_intensity", "light_color",
        "player_light_radius", "mouse_light_angle", "mouse_light_radius",
        "darkness_intensity"
    ]
    
    for key in required_keys:
        if key not in config:
            return False
    
    # 验证数值范围
    if not (0 <= config["light_intensity"] <= 255):
        return False
    if not (0 <= config["darkness_intensity"] <= 255):
        return False
    if not (0 <= config["mouse_light_angle"] <= 360):
        return False
    
    return True 
"""
英雄配置模块
定义不同英雄的基础属性和能力
"""

# 默认英雄配置（忍者蛙）
DEFAULT_HERO_CONFIG = {
    "name": "忍者蛙",
    "description": "平衡型英雄，适合初学者",
    "animations": {
        "idle": {
            "sprite_sheet": "images/player/Ninja_frog_Idle_32x32.png",
            "frame_count": 11,
            "frame_duration": 0.0333,
            "frame_width": 32,
            "frame_height": 32
        },
        "run": {
            "sprite_sheet": "images/player/Ninja_frog_Run_32x32.png",
            "frame_count": 12,
            "frame_duration": 0.0333,
            "frame_width": 32,
            "frame_height": 32
        },
        "hurt": {
            "sprite_sheet": "images/player/Ninja_frog_Hit_32x32.png",
            "frame_count": 7,
            "frame_duration": 0.0333,
            "frame_width": 32,
            "frame_height": 32
        }
    },
    "base_stats": {
        "max_health": 100,
        "speed": 200,
        "defense": 0,
        "health_regen": 0,
        "exp_multiplier": 1.0,
        "pickup_range": 50,
        "attack_power": 1.0,
        "luck": 1.0
    },
    "starting_weapon": "bullet",
    "unlock_condition": None  # 默认解锁
}

# 新的忍者蛙配置（使用角色图片）
NINJA_FROG_NEW_CONFIG = {
    "name": "忍者蛙",
    "description": "平衡型英雄，适合初学者",
    "animations": {
        "idle": {
            "sprite_sheet": "images/roles/finder/img_v3_02om_86c9f994-b2c4-430b-b5e4-ba47b143415g.png",
            "frame_count": 1,  # 只使用1帧，保持不动
            "frame_duration": 1.0,  # 持续时间很长，基本不动
            "frame_width": 64,
            "frame_height": 64,
            "row": 0,  # 使用第一行
            "col": 0   # 使用第一列
        },
        "run": {
            "sprite_sheet": "images/roles/finder/img_v3_02om_23010a0c-0b5b-4a06-ab7c-da477c12604g.png",
            "frame_count": 1,  # 第一张图片
            "frame_duration": 0.1,
            "frame_width": 64,
            "frame_height": 64,
            "row": 0,
            "col": 0
        },
        "run2": {
            "sprite_sheet": "images/roles/finder/img_v3_02om_86c9f994-b2c4-430b-b5e4-ba47b143415g.png",
            "frame_count": 1,  # 第二张图片
            "frame_duration": 0.1,
            "frame_width": 64,
            "frame_height": 64,
            "row": 0,
            "col": 0
        },
        "run3": {
            "sprite_sheet": "images/roles/finder/img_v3_02om_fdf9a462-f814-427b-9cb2-8d43bdad2c6g.png",
            "frame_count": 1,  # 第三张图片
            "frame_duration": 0.1,
            "frame_width": 64,
            "frame_height": 64,
            "row": 0,
            "col": 0
        },
        "run4": {
            "sprite_sheet": "images/roles/finder/img_v3_02om_3d6a419a-5471-44e4-944e-5d790c431dfg.png",
            "frame_count": 1,  # 第四张图片
            "frame_duration": 0.1,
            "frame_width": 64,
            "frame_height": 64,
            "row": 0,
            "col": 0
        },
        "hurt": {
            "sprite_sheet": "images/roles/finder/img_v3_02om_fdf9a462-f814-427b-9cb2-8d43bdad2c6g.png",
            "frame_count": 6,  # 使用前6帧作为受伤动画
            "frame_duration": 0.05,
            "frame_width": 64,
            "frame_height": 64,
            "row": 0,  # 使用第一行
            "col": 0   # 使用第一列
        },
        "attack": {
            "sprite_sheet": "images/roles/finder/img_v3_02om_3d6a419a-5471-44e4-944e-5d790c431dfg.png",
            "frame_count": 8,  # 使用前8帧作为攻击动画
            "frame_duration": 0.06,
            "frame_width": 64,
            "frame_height": 64,
            "row": 0,  # 使用第一行
            "col": 0   # 使用第一列
        }
    },
    "base_stats": {
        "max_health": 100,
        "speed": 200,
        "defense": 0,
        "health_regen": 0,
        "exp_multiplier": 1.0,
        "pickup_range": 50,
        "attack_power": 1.0,
        "luck": 1.0
    },
    "starting_weapon": "bullet",
    "unlock_condition": None  # 默认解锁
}

# 新角色配置（role2）
ROLE2_CONFIG = {
    "name": "神秘剑士",
    "description": "神秘的剑士，拥有强大的战斗能力",
    "animations": {
        "idle": {
            "sprite_sheet": "images/roles/role2/normal_frames/frame_01.png",
            "frame_count": 4,
            "frame_duration": 0.2,
            "frame_width": 96,
            "frame_height": 96,
            "use_sprite_sheet": False  # 使用单独的帧文件
        },
        "run": {
            "sprite_sheet": "images/roles/role2/run_frames/frame_01.png",
            "frame_count": 4,
            "frame_duration": 0.15,
            "frame_width": 96,
            "frame_height": 96,
            "use_sprite_sheet": False  # 使用单独的帧文件
        },
        "hurt": {
            "sprite_sheet": "images/roles/role2/attacked.png",
            "frame_count": 1,
            "frame_duration": 0.2,
            "frame_width": 96,
            "frame_height": 96
        },
        "ultimate": {
            "sprite_sheet": "images/roles/role2/attack_frames/frame_01.png",
            "frame_count": 4,
            "frame_duration": 0.25,  # 1秒内播放完4帧
            "frame_width": 96,
            "frame_height": 96,
            "use_sprite_sheet": False  # 使用单独的帧文件
        }
    },
    "base_stats": {
        "max_health": 100,
        "speed": 200,
        "defense": 0,
        "health_regen": 0,
        "exp_multiplier": 1.0,
        "pickup_range": 50,
        "attack_power": 1.0,
        "luck": 1.0
    },
    "starting_weapon": "bullet",
    "unlock_condition": None  # 默认解锁
}

# 英雄配置字典
HERO_CONFIGS = {
    "ninja_frog": NINJA_FROG_NEW_CONFIG,  # 使用新的配置
    "role2": ROLE2_CONFIG,  # 新角色
    
    "masked_dude": {
        "name": "蒙面侠",
        "description": "高速度，低血量的敏捷型英雄",
        "animations": {
            "idle": {
                "sprite_sheet": "images/player/Masked_Dude_Idle_32x32.png",
                "frame_count": 11,
                "frame_duration": 0.0333,
                "frame_width": 32,
                "frame_height": 32
            },
            "run": {
                "sprite_sheet": "images/player/Masked_Dude_Run_32x32.png",
                "frame_count": 12,
                "frame_duration": 0.0333,
                "frame_width": 32,
                "frame_height": 32
            },
            "hurt": {
                "sprite_sheet": "images/player/Masked_Dude_Hit_32x32.png",
                "frame_count": 7,
                "frame_duration": 0.0333,
                "frame_width": 32,
                "frame_height": 32
            }
        },
        "base_stats": {
            "max_health": 80,
            "speed": 250,
            "defense": 0,
            "health_regen": 0,
            "exp_multiplier": 1.0,
            "pickup_range": 60,
            "attack_power": 0.9,
            "luck": 1.2
        },
        "starting_weapon": "bullet",
        "unlock_condition": "reach_level_10"  # 达到10级解锁
    },
    
    "pink_man": {
        "name": "粉红侠",
        "description": "高防御，高生命值的坦克型英雄",
        "animations": {
            "idle": {
                "sprite_sheet": "images/player/Pink_Man_Idle_32x32.png",
                "frame_count": 11,
                "frame_duration": 0.0333,
                "frame_width": 32,
                "frame_height": 32
            },
            "run": {
                "sprite_sheet": "images/player/Pink_Man_Run_32x32.png",
                "frame_count": 12,
                "frame_duration": 0.0333,
                "frame_width": 32,
                "frame_height": 32
            },
            "hurt": {
                "sprite_sheet": "images/player/Pink_Man_Hit_32x32.png",
                "frame_count": 7,
                "frame_duration": 0.0333,
                "frame_width": 32,
                "frame_height": 32
            }
        },
        "base_stats": {
            "max_health": 120,
            "speed": 180,
            "defense": 0.2,
            "health_regen": 0.5,
            "exp_multiplier": 0.9,
            "pickup_range": 40,
            "attack_power": 1.1,
            "luck": 0.8
        },
        "starting_weapon": "bullet",
        "unlock_condition": "collect_1000_coins"  # 收集1000金币解锁
    }
}

def get_hero_config(hero_type):
    """
    获取指定英雄的配置
    
    Args:
        hero_type: 英雄类型
        
    Returns:
        dict: 英雄配置字典
    """
    return HERO_CONFIGS.get(hero_type, DEFAULT_HERO_CONFIG)

def get_available_heroes():
    """
    获取所有可用英雄类型
    
    Returns:
        list: 英雄类型列表
    """
    return list(HERO_CONFIGS.keys()) 
import sys
import os
sys.path.append('src')

import pygame
from modules.hero_config import get_hero_config
from modules.resource_manager import resource_manager

# 初始化pygame
pygame.init()

# 测试两个不同角色的配置
configs = {
    'ninja_frog': get_hero_config('ninja_frog'),
    'role2': get_hero_config('role2')
}

print("测试不同角色的动画资源区分:")

for hero_type, config in configs.items():
    print(f"\n=== {hero_type} ({config['name']}) ===")
    print(f"描述: {config['description']}")
    print(f"动画: {list(config['animations'].keys())}")
    
    # 测试加载精灵表
    for anim_name, anim_info in config['animations'].items():
        print(f"\n  {anim_name} 动画:")
        print(f"    精灵表路径: {anim_info['sprite_sheet']}")
        print(f"    帧数: {anim_info['frame_count']}")
        print(f"    帧持续时间: {anim_info['frame_duration']}")
        print(f"    帧尺寸: {anim_info['frame_width']}x{anim_info['frame_height']}")
        
        # 尝试加载精灵表
        try:
            # 使用角色类型作为前缀
            sprite_name = f"{hero_type}_{anim_name}_sprite"
            anim_name_with_prefix = f"{hero_type}_{anim_name}_anim"
            
            spritesheet = resource_manager.load_spritesheet(sprite_name, anim_info['sprite_sheet'])
            print(f"    ✓ 精灵表加载成功 (名称: {sprite_name})")
            
            # 创建动画
            animation = resource_manager.create_animation(
                anim_name_with_prefix,
                spritesheet,
                frame_width=anim_info['frame_width'],
                frame_height=anim_info['frame_height'],
                frame_count=anim_info['frame_count'],
                frame_duration=anim_info['frame_duration']
            )
            print(f"    ✓ 动画创建成功 (名称: {anim_name_with_prefix})，帧数: {len(animation.frames)}")
            
        except Exception as e:
            print(f"    ✗ 加载失败: {e}")

print("\n测试完成!") 
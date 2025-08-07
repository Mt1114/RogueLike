#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试Soul敌人的精灵图加载
"""

import sys
import os

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from modules.enemies.types.soul import Soul
from modules.enemies.enemy_config import get_enemy_config

def test_soul_sprites():
    """测试Soul敌人的精灵图加载"""
    print("=== 测试Soul敌人的精灵图加载 ===")
    
    try:
        # 创建Soul敌人实例
        soul = Soul(100, 100, 'soul', 'normal', 1)
        
        print("✅ Soul敌人创建成功")
        print(f"敌人类型: {soul.type}")
        print(f"敌人生命值: {soul.health}/{soul.max_health}")
        print(f"敌人伤害: {soul.damage}")
        
        # 检查动画
        if hasattr(soul, 'animations'):
            print(f"✅ 动画加载成功，包含 {len(soul.animations)} 个动画")
            for anim_name, anim in soul.animations.items():
                print(f"  - {anim_name}: {anim}")
        else:
            print("❌ 动画加载失败")
            
        # 检查图像
        if hasattr(soul, 'image') and soul.image:
            print(f"✅ 图像加载成功，尺寸: {soul.image.get_size()}")
        else:
            print("❌ 图像加载失败")
            
        print("\n=== 测试完成 ===")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_soul_sprites()

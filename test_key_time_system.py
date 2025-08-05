#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试基于时间的钥匙生成系统
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

import pygame
from modules.items.key_manager import KeyManager

class MockGame:
    """模拟游戏类，用于测试"""
    def __init__(self):
        self.map_manager = MockMapManager()
        self.item_manager = MockItemManager()

class MockMapManager:
    """模拟地图管理器"""
    def get_map_size(self):
        return 1000, 1000
    
    def get_collision_tiles(self):
        return []  # 空碰撞图块列表

class MockItemManager:
    """模拟物品管理器"""
    def __init__(self):
        self.items = []

def test_key_spawn_times():
    """测试钥匙生成时间"""
    print("=== 测试基于时间的钥匙生成系统 ===")
    
    # 创建模拟游戏对象
    mock_game = MockGame()
    
    # 创建钥匙管理器
    key_manager = KeyManager(mock_game)
    
    # 测试不同时间点的钥匙生成
    test_times = [5.0, 10.0, 15.0, 20.0, 25.0, 30.0, 35.0]
    
    for game_time in test_times:
        print(f"\n游戏时间: {game_time:.1f}秒")
        key_manager.update(0.1, game_time)
        print(f"当前钥匙数量: {key_manager.get_key_count()}")
        print(f"已生成钥匙时间点: {key_manager.spawned_keys_set}")
        
        # 显示所有钥匙信息
        for key in key_manager.keys:
            print(f"  钥匙 {key.key_id} 在位置 ({key.world_x}, {key.world_y})")

if __name__ == "__main__":
    test_key_spawn_times() 
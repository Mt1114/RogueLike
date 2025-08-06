import pygame
import numpy as np
import random
import sys
import xml.etree.ElementTree as ET

# 迷宫生成算法 - 深度优先搜索
def generate_maze(width, height):
    # 初始化迷宫，881表示墙，0表示路径
    maze = np.full((height, width), 881, dtype=int)
    
    # 起点和终点
    start_x, start_y = 1, 1  # 简化起点位置
    end_x, end_y = width-2, height-2  # 简化终点位置
    
    # 设置起点和终点
    maze[start_y, start_x] = 0
    maze[end_y, end_x] = 0
    
    # 深度优先搜索生成迷宫
    stack = [(start_x, start_y)]
    visited = set()
    visited.add((start_x, start_y))
    
    while stack:
        x, y = stack[-1]
        
        # 获取未访问的邻居（1格间距）
        neighbors = []
        directions = [(0, 2), (2, 0), (0, -2), (-2, 0)]  # 2格间距
        random.shuffle(directions)
        
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if 0 < nx < width-1 and 0 < ny < height-1 and (nx, ny) not in visited:
                # 检查中间路径
                mid_x, mid_y = x + dx//2, y + dy//2
                neighbors.append((nx, ny, mid_x, mid_y))
        
        if neighbors:
            # 选择一个未访问的邻居
            nx, ny, mid_x, mid_y = random.choice(neighbors)
            
            # 打通墙壁，创建路径（1格宽度）
            maze[ny, nx] = 0
            maze[mid_y, mid_x] = 0
            
            # 将新位置加入栈和已访问集合
            stack.append((nx, ny))
            visited.add((nx, ny))
        else:
            # 回溯
            stack.pop()
    
    return maze

def update_tmx_collision_layer(maze, tmx_file_path):
    """更新TMX文件的collision层数据"""
    # 解析XML文件
    tree = ET.parse(tmx_file_path)
    root = tree.getroot()
    
    # 找到collision层
    collision_layer = None
    for layer in root.findall('.//layer'):
        if layer.get('name') == 'collision':
            collision_layer = layer
            break
    
    if collision_layer is None:
        print("未找到collision层")
        return False
    
    # 找到data元素
    data_element = collision_layer.find('data')
    if data_element is None:
        print("未找到data元素")
        return False
    
    # 将迷宫数据转换为CSV格式
    csv_data = []
    for row in maze:
        # 确保每行有80个元素，并且以逗号结尾
        row_data = ','.join(str(cell) for cell in row)
        csv_data.append(row_data + ',')
    
    # 更新data元素的内容
    data_element.text = '\n' + '\n'.join(csv_data) + '\n'
    
    # 保存文件
    tree.write(tmx_file_path, encoding='UTF-8', xml_declaration=True)
    return True

def main():
    # 迷宫尺寸
    width, height = 60, 60
    
    # 生成迷宫
    maze = generate_maze(width, height)
    
    # 统计路径数量
    path_count = np.sum(maze == 0)
    wall_count = np.sum(maze == 881)
    print(f"迷宫生成完成 - 路径数量: {path_count}, 墙壁数量: {wall_count}")
    
    # 保存到文本文件
    with open("maze.txt", 'w') as f:
        for row in maze:
            f.write(','.join(str(cell) for cell in row) + ',\n')
    print("迷宫已保存到 maze.txt")
    
    # 更新TMX文件
    tmx_file_path = "assets/maps/test6_map.tmx"
    if update_tmx_collision_layer(maze, tmx_file_path):
        print(f"迷宫数据已成功写入到 {tmx_file_path} 的collision层")
    else:
        print("更新TMX文件失败")
    
    # 初始化Pygame
    pygame.init()
    
    # 计算窗口大小（每个单元格8像素）
    cell_size = 8
    window_size = (width * cell_size, height * cell_size)
    screen = pygame.display.set_mode(window_size)
    pygame.display.set_caption("60x60迷宫生成 - 深度优先搜索算法")
    
    # 创建字体
    font = pygame.font.SysFont(None, 28)
    
    # 定义颜色
    wall_color = (30, 30, 60)    # 深蓝色墙壁
    path_color = (200, 220, 255) # 浅蓝色路径
    start_color = (255, 100, 100) # 红色起点
    end_color = (100, 255, 100)   # 绿色终点
    
    # 绘制迷宫函数
    def draw_maze(screen, maze, cell_size):
        height, width = maze.shape
        screen.fill((0, 0, 0))  # 黑色背景
        
        for y in range(height):
            for x in range(width):
                rect = pygame.Rect(x * cell_size, y * cell_size, cell_size, cell_size)
                if maze[y, x] == 881:  # 墙壁
                    pygame.draw.rect(screen, wall_color, rect)
                    pygame.draw.rect(screen, (50, 50, 90), rect, 1)  # 边框
                else:  # 路径
                    pygame.draw.rect(screen, path_color, rect)
                    pygame.draw.rect(screen, (180, 200, 230), rect, 1)  # 边框
                    
                    # 标记起点和终点
                    if (x, y) == (1, 1):
                        pygame.draw.rect(screen, start_color, rect.inflate(-cell_size//2, -cell_size//2))
                    elif (x, y) == (width-2, height-2):
                        pygame.draw.rect(screen, end_color, rect.inflate(-cell_size//2, -cell_size//2))
    
    # 主循环
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_r:  # 按R键重新生成迷宫
                    maze = generate_maze(width, height)
                    
                    # 保存到文本文件
                    with open("maze.txt", 'w') as f:
                        for row in maze:
                            f.write(','.join(str(cell) for cell in row) + ',\n')
                    print("迷宫已重新生成并保存到 maze.txt")
                    
                    # 更新TMX文件
                    if update_tmx_collision_layer(maze, tmx_file_path):
                        print(f"迷宫数据已重新写入到 {tmx_file_path} 的collision层")
                    else:
                        print("更新TMX文件失败")
        
        # 绘制迷宫
        draw_maze(screen, maze, cell_size)
        
        # 显示说明文字
        text = font.render("按R键重新生成迷宫 | 按ESC退出", True, (255, 255, 200))
        screen.blit(text, (10, 10))
        
        # 显示起点和终点说明
        start_text = font.render("起点", True, start_color)
        end_text = font.render("终点", True, end_color)
        screen.blit(start_text, (window_size[0] - 150, 10))
        screen.blit(end_text, (window_size[0] - 150, 40))
        
        # 绘制起点和终点示例
        pygame.draw.rect(screen, start_color, (window_size[0] - 200, 15, 15, 15))
        pygame.draw.rect(screen, end_color, (window_size[0] - 200, 45, 15, 15))
        
        pygame.display.flip()
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main() 
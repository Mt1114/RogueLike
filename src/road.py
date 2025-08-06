import pygame
import numpy as np
import random
import sys

# 迷宫生成算法 - 深度优先搜索
def generate_maze(width, height):
    # 初始化迷宫，1375表示墙，0表示路径
    maze = np.full((height, width), 1375, dtype=int)
    
    # 起点和终点
    start_x, start_y = 1, 1
    end_x, end_y = width-2, height-2
    
    # 设置起点和终点
    maze[start_y, start_x] = 0
    maze[end_y, end_x] = 0
    
    # 深度优先搜索生成迷宫
    stack = [(start_x, start_y)]
    
    while stack:
        x, y = stack[-1]
        
        # 获取未访问的邻居
        neighbors = []
        directions = [(0, 2), (2, 0), (0, -2), (-2, 0)]
        random.shuffle(directions)
        
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if 0 < nx < width-1 and 0 < ny < height-1 and maze[ny, nx] == 1375:
                neighbors.append((nx, ny, x + dx//2, y + dy//2))
        
        if neighbors:
            # 选择一个未访问的邻居
            nx, ny, mid_x, mid_y = random.choice(neighbors)
            
            # 打通墙壁
            maze[ny, nx] = 0
            maze[mid_y, mid_x] = 0
            
            # 将新位置加入栈
            stack.append((nx, ny))
        else:
            # 回溯
            stack.pop()
    
    return maze

# 保存迷宫到文本文件
def save_maze_to_txt(maze, filename):
    with open(filename, 'w') as f:
        for row in maze:
            f.write(','.join(str(cell) for cell in row) + '\n')

# 绘制迷宫
def draw_maze(screen, maze, cell_size):
    height, width = maze.shape
    screen.fill((0, 0, 0))  # 黑色背景
    
    # 定义颜色
    wall_color = (30, 30, 60)    # 深蓝色墙壁
    path_color = (200, 220, 255) # 浅蓝色路径
    start_color = (255, 100, 100) # 红色起点
    end_color = (100, 255, 100)   # 绿色终点
    
    for y in range(height):
        for x in range(width):
            rect = pygame.Rect(x * cell_size, y * cell_size, cell_size, cell_size)
            if maze[y, x] == 1375:  # 墙壁
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

# 主函数
def main():
    # 迷宫尺寸
    width, height = 80, 80
    
    # 生成迷宫
    maze = generate_maze(width, height)
    
    # 保存到文件
    save_maze_to_txt(maze, "maze.txt")
    print("迷宫已保存到 maze.txt")
    
    # 初始化Pygame
    pygame.init()
    
    # 计算窗口大小（每个单元格8像素）
    cell_size = 8
    window_size = (width * cell_size, height * cell_size)
    screen = pygame.display.set_mode(window_size)
    pygame.display.set_caption("80x80迷宫生成 - 深度优先搜索算法")
    
    # 创建字体
    font = pygame.font.SysFont(None, 28)
    
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
                    save_maze_to_txt(maze, "maze.txt")
                    print("迷宫已重新生成并保存到 maze.txt")
        
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
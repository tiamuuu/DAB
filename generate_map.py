import json
import numpy as np

def draw_line(grid, start, end):
    """使用Bresenham算法在网格上绘制线段"""
    x0, y0 = start
    x1, y1 = end
    
    dx = abs(x1 - x0)
    dy = abs(y1 - y0)
    
    x_step = 1 if x0 < x1 else -1
    y_step = 1 if y0 < y1 else -1
    
    error = dx - dy
    
    x, y = x0, y0
    
    while True:
        # 标记当前点
        if 0 <= y < grid.shape[0] and 0 <= x < grid.shape[1]:
            grid[y][x] = 1
        
        if x == x1 and y == y1:
            break
            
        error2 = 2 * error
        
        if error2 > -dy:
            error -= dy
            x += x_step
            
        if error2 < dx:
            error += dx
            y += y_step

def generate_map_from_json(json_file):
    """从JSON文件生成二维数组地图"""
    resolution = 5
    # 读取JSON文件
    with open(json_file, 'r') as f:
        data = json.load(f)
    
    segments = data['segments']
    start_point = data.get('start_point', [0, 0])  # 获取起始点
    
    # 找到所有坐标的边界，并放大10倍
    max_x = 0
    max_y = 0
    
    for segment in segments:
        start = segment['start']
        end = segment['end']
        
        # 坐标放大10倍
        start_scaled = [start[0] * resolution, start[1] * resolution]
        end_scaled = [end[0] * resolution, end[1] * resolution]
        
        max_x = max(max_x, start_scaled[0], end_scaled[0])
        max_y = max(max_y, start_scaled[1], end_scaled[1])
    
    # 创建二维数组（行数 = max_y + 1, 列数 = max_x + 1）
    grid = np.zeros((max_y + 1, max_x + 1), dtype=int)
    
    # 绘制所有线段
    for segment in segments:
        start = segment['start']
        end = segment['end']
        
        # 坐标放大10倍
        start_scaled = [start[0] * resolution, start[1] * resolution]
        end_scaled = [end[0] * resolution, end[1] * resolution]
        
        # 绘制线段（注意：坐标格式是[x, y]，但数组索引是[行, 列] = [y, x]）
        draw_line(grid, start_scaled, end_scaled)
    
    # 计算起始位置（放大10倍）
    start_pos = [start_point[1] * resolution, start_point[0] * resolution]  # [row, col] = [* resolution, * resolution]
    
    return grid, start_pos

def print_map(grid):
    """打印地图（可选：用于小地图的可视化）"""
    print(f"地图大小: {grid.shape[0]} 行 x {grid.shape[1]} 列")
    print("地图预览（前20x20区域）:")
    preview_rows = min(20, grid.shape[0])
    preview_cols = min(20, grid.shape[1])
    
    for i in range(preview_rows):
        row_str = ""
        for j in range(preview_cols):
            row_str += "█" if grid[i][j] == 1 else "·"
        print(row_str)
    
    if grid.shape[0] > 20 or grid.shape[1] > 20:
        print("（只显示前20x20区域）")

def save_map(grid, filename):
    """保存地图到文件"""
    np.savetxt(filename, grid, fmt='%d', delimiter='')
    print(f"地图已保存到 {filename}")

if __name__ == "__main__":
    # 生成地图
    map_grid = generate_map_from_json('map1.json')
    
    # 打印地图信息和预览
    print_map(map_grid)
    
    # 保存地图到文件
    save_map(map_grid, 'map_output.txt')
    
    # 也可以保存为numpy数组
    np.save('map_array.npy', map_grid)
    print("地图数组已保存到 map_array.npy")
    
    print(f"\n线段总数: {len(map_grid[map_grid == 1])}") 
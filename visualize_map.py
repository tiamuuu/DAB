import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as colors

def load_and_visualize_map(npy_file):
    """加载npy文件并可视化地图"""
    
    # 加载numpy数组
    map_array = np.load(npy_file)
    
    print(f"地图大小: {map_array.shape[0]} 行 x {map_array.shape[1]} 列")
    print(f"线段像素数: {np.sum(map_array == 1)}")
    
    # 创建自定义颜色映射：0 -> 白色, 1 -> 黑色
    cmap = colors.ListedColormap(['white', 'black'])
    
    # 创建图形
    plt.figure(figsize=(12, 10))
    
    # 显示地图
    plt.imshow(map_array, cmap=cmap, interpolation='nearest')
    
    # 移除坐标轴刻度和网格
    plt.axis('off')
    
    # 设置标题
    plt.title(f'地图可视化 ({map_array.shape[0]}x{map_array.shape[1]})', fontsize=14, pad=20)
    
    # 调整布局
    plt.tight_layout()
    
    # 显示图像
    plt.show()
    
    return map_array

def save_visualization(npy_file, output_file='map_visualization.png', dpi=300):
    """加载地图并保存可视化图像"""
    
    # 加载numpy数组
    map_array = np.load(npy_file)
    
    # 创建自定义颜色映射
    cmap = colors.ListedColormap(['white', 'black'])
    
    # 创建图形
    plt.figure(figsize=(12, 10))
    
    # 显示地图
    plt.imshow(map_array, cmap=cmap, interpolation='nearest')
    
    # 移除坐标轴和网格
    plt.axis('off')
    
    # 设置标题
    plt.title(f'地图可视化 ({map_array.shape[0]}x{map_array.shape[1]})', fontsize=14, pad=20)
    
    # 调整布局
    plt.tight_layout()
    
    # 保存图像
    plt.savefig(output_file, dpi=dpi, bbox_inches='tight', facecolor='white')
    print(f"可视化图像已保存到: {output_file}")
    
    # 显示图像
    plt.show()
    
    return map_array

def visualize_map_with_coordinates(npy_file):
    """带坐标信息的地图可视化"""
    
    # 加载numpy数组
    map_array = np.load(npy_file)
    
    # 创建自定义颜色映射
    cmap = colors.ListedColormap(['white', 'black'])
    
    # 创建图形
    fig, ax = plt.subplots(figsize=(12, 10))
    
    # 显示地图
    im = ax.imshow(map_array, cmap=cmap, interpolation='nearest')
    
    # 设置坐标轴标签
    ax.set_xlabel('列 (X坐标 * 10)', fontsize=12)
    ax.set_ylabel('行 (Y坐标 * 10)', fontsize=12)
    ax.set_title(f'地图可视化 ({map_array.shape[0]}x{map_array.shape[1]})', fontsize=14)
    
    # 设置坐标轴刻度
    x_ticks = np.arange(0, map_array.shape[1], 10)
    y_ticks = np.arange(0, map_array.shape[0], 10)
    ax.set_xticks(x_ticks)
    ax.set_yticks(y_ticks)
    
    # 移除网格（如果有的话）
    ax.grid(False)
    
    # 调整布局
    plt.tight_layout()
    
    # 显示图像
    plt.show()
    
    return map_array

if __name__ == "__main__":
    # 默认文件名
    npy_filename = 'map_array.npy'
    
    try:
        print("=== 地图可视化 ===")
        
        # 首先尝试加载和显示地图（无坐标）
        print("\n1. 加载并显示地图（无坐标轴）:")
        map_data = load_and_visualize_map(npy_filename)
        
        # 保存可视化图像
        print("\n2. 保存可视化图像:")
        save_visualization(npy_filename, 'map_visualization.png')
        
        # 可选：显示带坐标的版本
        print("\n3. 显示带坐标的版本:")
        visualize_map_with_coordinates(npy_filename)
        
    except FileNotFoundError:
        print(f"错误: 找不到文件 '{npy_filename}'")
        print("请先运行 generate_map.py 来生成地图数组")
    except Exception as e:
        print(f"发生错误: {e}") 
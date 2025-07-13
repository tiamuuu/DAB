import numpy as np
import matplotlib.pyplot as plt
import math

class Radar:
    def __init__(self, map_array, position, max_range=None):
        """
        初始化雷达
        
        Args:
            map_array: 二维numpy数组，0表示空白，1表示障碍物
            position: 雷达位置 [y, x] （行，列）
            max_range: 最大扫描距离，如果为None则使用地图对角线长度
        """
        self.map = map_array
        self.position = position  # [y, x]
        self.height, self.width = map_array.shape
        
        # 设置最大扫描距离
        if max_range is None:
            self.max_range = int(math.sqrt(self.height**2 + self.width**2))
        else:
            self.max_range = max_range
        
        # 存储扫描结果
        self.scan_results = {}
    
    def cast_ray(self, angle_degrees):
        """
        向指定角度发射射线
        
        Args:
            angle_degrees: 射线角度（度）
            
        Returns:
            distance: 射线到达障碍物的距离，如果没有遇到障碍物则返回max_range
            hit_point: 碰撞点坐标 [y, x]，如果没有碰撞则为None
        """
        # 将角度转换为弧度
        angle_rad = math.radians(angle_degrees)
        
        # 计算射线方向
        dy = math.sin(angle_rad)
        dx = math.cos(angle_rad)
        
        # 起始位置
        y, x = self.position
        
        # 逐步推进射线
        for step in range(self.max_range):
            # 计算当前位置
            current_y = y + dy * step
            current_x = x + dx * step
            
            # 转换为整数坐标
            grid_y = int(round(current_y))
            grid_x = int(round(current_x))
            
            # 检查是否超出地图边界
            if (grid_y < 0 or grid_y >= self.height or 
                grid_x < 0 or grid_x >= self.width):
                return step, [grid_y, grid_x]
            
            # 检查是否碰到障碍物
            if self.map[grid_y, grid_x] == 1:
                distance = math.sqrt((current_y - y)**2 + (current_x - x)**2)
                return distance, [grid_y, grid_x]
        
        # 如果没有碰撞，返回最大距离
        return self.max_range, None
    
    def scan_360(self, angle_step=1):
        """
        进行360度扫描
        
        Args:
            angle_step: 角度步长（度）
            
        Returns:
            scan_data: 字典，键为角度，值为 (距离, 碰撞点)
        """
        scan_data = {}
        
        for angle in range(0, 360, angle_step):
            distance, hit_point = self.cast_ray(angle)
            scan_data[angle] = (distance, hit_point)
        
        self.scan_results = scan_data
        return scan_data
    
    def get_scan_distances(self, angle_step=1):
        """
        获取360度扫描的距离数组
        
        Args:
            angle_step: 角度步长
            
        Returns:
            angles: 角度数组
            distances: 对应的距离数组
        """
        if not self.scan_results:
            self.scan_360(angle_step)
        
        angles = sorted(self.scan_results.keys())
        distances = [self.scan_results[angle][0] for angle in angles]
        
        return np.array(angles), np.array(distances)
    
    def visualize_scan(self, angle_step=5, show_rays=True, max_rays_to_show=72):
        """
        可视化雷达扫描结果
        
        Args:
            angle_step: 角度步长
            show_rays: 是否显示射线
            max_rays_to_show: 最大显示射线数量
        """
        # 进行扫描
        scan_data = self.scan_360(angle_step)
        
        # 创建图形
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
        
        # 左图：地图和射线
        ax1.imshow(self.map, cmap='gray_r', interpolation='nearest')
        ax1.plot(self.position[1], self.position[0], 'ro', markersize=8, label='雷达位置')
        
        if show_rays:
            ray_count = 0
            for angle, (distance, hit_point) in scan_data.items():
                if ray_count >= max_rays_to_show:
                    break
                    
                # 计算射线终点
                angle_rad = math.radians(angle)
                end_y = self.position[0] + distance * math.sin(angle_rad)
                end_x = self.position[1] + distance * math.cos(angle_rad)
                
                # 绘制射线
                ax1.plot([self.position[1], end_x], [self.position[0], end_y], 
                        'b-', alpha=0.3, linewidth=0.5)
                
                # 标记碰撞点
                if hit_point is not None:
                    ax1.plot(hit_point[1], hit_point[0], 'r.', markersize=2)
                
                ray_count += 1
        
        ax1.set_title('雷达扫描图')
        ax1.set_xlabel('X坐标')
        ax1.set_ylabel('Y坐标')
        ax1.legend()
        ax1.axis('equal')
        
        # 右图：极坐标图
        angles, distances = self.get_scan_distances(angle_step)
        angles_rad = np.radians(angles)
        
        ax2 = plt.subplot(122, projection='polar')
        ax2.plot(angles_rad, distances, 'b-', linewidth=1)
        ax2.fill(angles_rad, distances, alpha=0.3)
        ax2.set_title('雷达扫描 - 极坐标视图')
        ax2.set_ylim(0, self.max_range)
        
        plt.tight_layout()
        plt.show()
    
    def visualize_polar_only(self, angle_step=1):
        """
        只显示极坐标雷达图
        """
        angles, distances = self.get_scan_distances(angle_step)
        angles_rad = np.radians(angles)
        
        plt.figure(figsize=(8, 8))
        ax = plt.subplot(111, projection='polar')
        ax.plot(angles_rad, distances, 'b-', linewidth=1)
        ax.fill(angles_rad, distances, alpha=0.3, color='lightblue')
        ax.set_title('雷达扫描图', pad=20)
        ax.set_ylim(0, self.max_range)
        ax.grid(True)
        
        plt.show()
    
    def move_radar(self, new_position):
        """
        移动雷达到新位置
        
        Args:
            new_position: 新位置 [y, x]
        """
        self.position = new_position
        self.scan_results = {}  # 清空之前的扫描结果
    
    def get_scan_points(self, angle_step=1):
        """
        获取扫描到的所有点的坐标
        
        Returns:
            points: 扫描点坐标列表 [[y1, x1], [y2, x2], ...]
        """
        if not self.scan_results:
            self.scan_360(angle_step)
        
        points = []
        for angle, (distance, hit_point) in self.scan_results.items():
            if hit_point is not None:
                points.append(hit_point)
            else:
                # 如果没有碰撞，计算边界点
                angle_rad = math.radians(angle)
                end_y = self.position[0] + distance * math.sin(angle_rad)
                end_x = self.position[1] + distance * math.cos(angle_rad)
                points.append([int(end_y), int(end_x)])
        
        return points

# 示例使用函数
def demo_radar():
    """演示雷达功能"""
    # 创建一个简单的测试地图
    test_map = np.zeros((50, 50), dtype=int)
    
    # 添加一些障碍物
    test_map[10:15, 20:25] = 1  # 矩形障碍物
    test_map[30:35, 10:40] = 1  # 长条障碍物
    test_map[20:30, 35:38] = 1  # 竖条障碍物
    
    # 创建雷达
    radar_pos = [25, 25]  # 雷达位置
    radar = Radar(test_map, radar_pos, max_range=30)
    
    # 进行扫描和可视化
    radar.visualize_scan(angle_step=2)
    radar.visualize_polar_only(angle_step=1)
    
    return radar

if __name__ == "__main__":
    # 运行演示
    demo_radar() 
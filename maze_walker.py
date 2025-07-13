import tkinter as tk
import numpy as np
import math
from generate_map import generate_map_from_json
from radar import Radar

class MazeWalker:
    def __init__(self, target_pos=None):
        self.root = tk.Tk()
        self.root.title("迷宫行走游戏 - 使用WASD或方向键控制")
        
        # 创建迷宫（先生成迷宫以获取实际尺寸）
        self.maze, self.player_pos = self.generate_maze()
        self.start_pos = self.player_pos
        self.maze_height, self.maze_width = self.maze.shape
        
        # 动态计算格子大小和窗口尺寸
        self.calculate_display_parameters()
        
        # 设置窗口大小
        self.root.geometry(f"{self.window_width}x{self.window_height}")
        # self.root.resizable(False, False)  # 不允许调整大小
        
        
        # 初始化雷达
        self.radar_range = 30
        self.radar = Radar(self.maze, self.player_pos, self.radar_range)
        
        # 创建探索地图（记录哪些区域被雷达扫描过）
        self.explored_map = np.zeros_like(self.maze, dtype=bool)
        
        # 雷达设置
        self.scan_angle_step = 3
        self.show_rays = False
        
        # 游戏状态
        self.moves = 0
        self.game_won = False
        self.is_auto_exploring = False
        self.last_positions = []  # 记录最近的位置，防止来回移动
        self.player_trail = [tuple(self.player_pos)]  # 记录玩家轨迹
        self.exits = []  # 记录找到的出口位置
        self.planned_path = []  # A*算法规划的路径
        self.is_auto_moving = False  # 是否正在自动移动
        self.auto_move_path = []  # 自动移动的路径
        self.auto_move_index = 0  # 自动移动的当前索引
        
        self.setup_gui()
        self.bind_keys()
        
        # 初始雷达扫描
        self.update_radar_scan()
        
        self.update_display()
        
    def generate_maze(self):
        """生成迷宫"""
        maze, start_pos = generate_map_from_json('1.json')
        return maze, start_pos
    
    def calculate_display_parameters(self):
        """根据迷宫大小动态计算显示参数（考虑双地图显示）"""
        # 设置最大显示区域（留出空间给UI元素，考虑双地图）
        max_single_canvas_width = 600  # 单个地图的最大宽度
        max_canvas_height = 600
        
        # 计算理想的格子大小
        ideal_cell_width = max_single_canvas_width // self.maze_width
        ideal_cell_height = max_canvas_height // self.maze_height
        
        # 选择较小的尺寸以确保迷宫完全显示
        self.cell_size = min(ideal_cell_width, ideal_cell_height, 25)  # 最大25像素
        self.cell_size = max(self.cell_size, 2)  # 最小2像素
        
        # 计算实际画布大小
        self.canvas_width = self.maze_width * self.cell_size
        self.canvas_height = self.maze_height * self.cell_size
        
        # 计算窗口大小（为双画布和UI元素预留空间）
        canvas_spacing = 20  # 两个画布之间的间距
        ui_width_padding = 100  # 左右边距
        ui_height_padding = 400  # 上下边距（标题、按钮、说明等）
        
        self.window_width = (self.canvas_width * 2) + canvas_spacing + ui_width_padding
        self.window_height = self.canvas_height + ui_height_padding
        
        # 确保窗口不会太大
        screen_width = 1600  # 假设的屏幕宽度
        screen_height = 1000   # 假设的屏幕高度
        
        if self.window_width > screen_width:
            self.window_width = screen_width
        if self.window_height > screen_height:
            self.window_height = screen_height
            
        print(f"迷宫尺寸: {self.maze_height}x{self.maze_width}")
        print(f"格子大小: {self.cell_size}x{self.cell_size} 像素")
        print(f"单个画布大小: {self.canvas_width}x{self.canvas_height} 像素")
        print(f"窗口大小: {self.window_width}x{self.window_height} 像素")
    

    def setup_gui(self):
        """设置图形界面"""
        # 创建主框架
        main_frame = tk.Frame(self.root, bg='lightgray')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 标题
        title_label = tk.Label(
            main_frame, 
            text="雷达迷宫探索 - 双视图", 
            font=("Arial", 20, "bold"),
            bg='lightgray'
        )
        title_label.pack(pady=10)
        
        # 游戏信息
        info_frame = tk.Frame(main_frame, bg='lightgray')
        info_frame.pack(pady=5)
        
        self.moves_label = tk.Label(
            info_frame, 
            text="步数: 0", 
            font=("Arial", 12),
            bg='lightgray'
        )
        self.moves_label.pack(side=tk.LEFT, padx=15)
        
        self.status_label = tk.Label(
            info_frame, 
            text="使用WASD或方向键移动", 
            font=("Arial", 12),
            bg='lightgray'
        )
        self.status_label.pack(side=tk.LEFT, padx=15)
        
        self.radar_info_label = tk.Label(
            info_frame, 
            text="雷达范围: 50", 
            font=("Arial", 12),
            bg='lightgray'
        )
        self.radar_info_label.pack(side=tk.LEFT, padx=15)
        
        self.position_label = tk.Label(
            info_frame, 
            text="坐标: (0, 0)", 
            font=("Arial", 12),
            bg='lightgray',
            fg='darkblue'
        )
        self.position_label.pack(side=tk.LEFT, padx=15)
        
        # 双画布框架
        canvas_container = tk.Frame(main_frame, bg='lightgray')
        canvas_container.pack(pady=10)
        
        # 左侧画布 - 明图（显示完整地图和雷达射线）
        left_frame = tk.Frame(canvas_container)
        left_frame.pack(side=tk.LEFT, padx=10)
        
        tk.Label(left_frame, text="明图 - 完整地图视图", font=("Arial", 14, "bold")).pack(pady=5)
        
        bright_canvas_frame = tk.Frame(left_frame, relief=tk.SUNKEN, borderwidth=2)
        bright_canvas_frame.pack()
        
        self.bright_canvas = tk.Canvas(
            bright_canvas_frame,
            width=self.canvas_width,
            height=self.canvas_height,
            bg='white'
        )
        self.bright_canvas.pack()
        
        # 右侧画布 - 暗图（只显示探索过的区域）
        right_frame = tk.Frame(canvas_container)
        right_frame.pack(side=tk.LEFT, padx=10)
        
        tk.Label(right_frame, text="暗图 - 雷达探索视图", font=("Arial", 14, "bold")).pack(pady=5)
        
        dark_canvas_frame = tk.Frame(right_frame, relief=tk.SUNKEN, borderwidth=2)
        dark_canvas_frame.pack()
        
        self.dark_canvas = tk.Canvas(
            dark_canvas_frame,
            width=self.canvas_width,
            height=self.canvas_height,
            bg='black'
        )
        self.dark_canvas.pack()
        
        # 控制面板
        control_frame = tk.Frame(main_frame, bg='lightgray')
        control_frame.pack(pady=10)
        
        # 按钮行1
        button_frame1 = tk.Frame(control_frame, bg='lightgray')
        button_frame1.pack(pady=5)
        
        self.explore_button = tk.Button(
            button_frame1, 
            text="探索", 
            command=self.toggle_auto_explore,
            font=("Arial", 11),
            padx=15, pady=3,
            bg='lightgreen'
        )
        self.explore_button.pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            button_frame1, 
            text="回家", 
            command=self.go_home,
            font=("Arial", 11),
            padx=15, pady=3,
            bg='lightblue'
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            button_frame1, 
            text="寻路", 
            command=self.find_path,
            font=("Arial", 11),
            padx=15, pady=3,
            bg='lightcoral'
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            button_frame1, 
            text="停止&清空", 
            command=self.stop_auto_move,
            font=("Arial", 11),
            padx=15, pady=3,
            bg='red'
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            button_frame1, 
            text="退出", 
            command=self.root.quit,
            font=("Arial", 11),
            padx=15, pady=3
        ).pack(side=tk.LEFT, padx=5)
        
        
        # 雷达设置
        settings_frame = tk.Frame(control_frame, bg='lightgray')
        settings_frame.pack(pady=5)
        
        tk.Label(settings_frame, text="雷达范围:", bg='lightgray', font=("Arial", 10)).pack(side=tk.LEFT, padx=5)
        self.range_scale = tk.Scale(
            settings_frame, 
            from_=20, to=100, 
            orient=tk.HORIZONTAL, 
            command=self.on_range_change,
            length=150
        )
        self.range_scale.set(self.radar_range)
        self.range_scale.pack(side=tk.LEFT, padx=5)
        
        
        # 说明文字
        instruction_text = """
控制说明: W/A/S/D或方向键移动 | 蓝色圆点=角色 | 红色线条=移动轨迹 | 绿色圆圈=出口 | 黄色方块=起点 | 橙色路径=A*规划路径
明图显示完整地图+雷达射线 | 暗图显示探索区域+出口+规划路径 | 回家/寻路=A*寻路并自动移动 | 停止&清空=中断移动并清空轨迹
        """
        
        instruction_label = tk.Label(
            main_frame, 
            text=instruction_text.strip(),
            font=("Arial", 9),
            bg='lightgray',
            justify=tk.CENTER
        )
        instruction_label.pack(pady=5)
    
    def bind_keys(self):
        """绑定键盘事件"""
        self.root.bind('<KeyPress>', self.on_key_press)
        self.root.focus_set()  # 确保窗口获得焦点
    
    def on_key_press(self, event):
        """处理键盘按键"""
        if self.game_won or self.is_auto_moving:
            return
            
        key = event.keysym.lower()
        
        # 定义移动方向
        moves = {
            'w': (-1, 0),      # 上
            'up': (-1, 0),     # 上箭头
            's': (1, 0),       # 下
            'down': (1, 0),    # 下箭头
            'a': (0, -1),      # 左
            'left': (0, -1),   # 左箭头
            'd': (0, 1),       # 右
            'right': (0, 1)    # 右箭头
        }
        
        if key in moves:
            dy, dx = moves[key]
            self.move_player(dy, dx)
    

    def toggle_auto_explore(self):
        """切换自动探索状态"""
        if self.is_auto_exploring:
            # 停止探索
            self.is_auto_exploring = False
            self.explore_button.config(text="开始自动探索", bg='lightgreen')
            self.status_label.config(text="已停止自动探索")
        else:
            # 检查是否正在自动移动
            if self.is_auto_moving:
                self.status_label.config(text="正在自动移动中，请稍候...")
                return
            # 开始探索
            self.auto_explore()
    
    def auto_explore(self):
        """开始自动探索"""
        self.is_auto_exploring = True
        self.explore_button.config(text="停止探索", bg='orange')
        self.status_label.config(text="开始自动探索（使用A*算法）...")
        self.auto_explore_step()
    
    def auto_explore_step(self):
        """执行一步自动探索"""
        if not self.is_auto_exploring:
            return
            
        # 寻找所有frontier点
        frontiers = []
        for i in range(self.maze_height):
            for j in range(self.maze_width):
                if self.is_frontier(i, j):
                    frontiers.append((i, j))
        
        if len(frontiers) == 0:
            self.status_label.config(text="探索完成！正在寻找出口...")
            self.find_exits()
            exit_count = len(self.exits)
            self.status_label.config(text=f"探索完成！找到 {exit_count} 个可能的出口")
            self.is_auto_exploring = False
            self.explore_button.config(text="开始自动探索", bg='lightgreen')
            self.update_display()
            return
        
        # 按距离排序，选择最近的frontier
        frontiers.sort(key=lambda x: self.calc_dist(x[0], x[1], self.player_pos[0], self.player_pos[1]))
        
        # 尝试找到路径到最近的frontier
        for frontier in frontiers:
            print(f"尝试到达frontier: {frontier}, 当前位置: {self.player_pos}")
            # 使用A*算法寻路到frontier，避开最近访问的位置
            current_pos = tuple(self.player_pos)
            path = self.astar_pathfinding(current_pos, frontier, avoid_recent=True)
            
            if path and len(path) >= 2:
                # 向目标移动一步
                next_pos = path[1]  # path[0]是当前位置，path[1]是下一步
                dy = next_pos[0] - self.player_pos[0]  # 行的变化
                dx = next_pos[1] - self.player_pos[1]  # 列的变化
                
                print(f"下一步位置: {next_pos}, 移动方向: dy={dy}, dx={dx}")
                
                # 记录当前位置，防止来回移动
                current_pos = tuple(self.player_pos)
                if current_pos not in self.last_positions[-3:]:  # 避免最近3步的重复
                    self.last_positions.append(current_pos)
                    if len(self.last_positions) > 10:  # 只保留最近10个位置
                        self.last_positions.pop(0)
                
                self.move_player(dy, dx)
                
                # 快速继续下一步探索
                self.root.after(1, self.auto_explore_step)  # 1ms延迟，既快速又不卡顿
                return
        
        # 如果没有找到可达的frontier，结束探索
        self.status_label.config(text="探索完成！正在寻找出口...")
        self.find_exits()
        exit_count = len(self.exits)
        self.status_label.config(text=f"探索完成！找到 {exit_count} 个可能的出口")
        self.is_auto_exploring = False
        self.explore_button.config(text="开始自动探索", bg='lightgreen')
        self.update_display()
            
    def calc_dist(self, i1, j1, i2, j2):
        return abs(i1 - i2) + abs(j1 - j2)
    
    def astar_pathfinding(self, start, goal, avoid_recent=False):
        """A*算法寻路"""
        import heapq
        
        def heuristic(pos):
            return self.calc_dist(pos[0], pos[1], goal[0], goal[1])
        
        # 开放列表和关闭列表
        open_list = []
        closed_set = set()
        
        # 存储每个节点的父节点和成本
        came_from = {}
        g_score = {start: 0}
        f_score = {start: heuristic(start)}
        
        heapq.heappush(open_list, (f_score[start], start))
        
        while open_list:
            current_f, current = heapq.heappop(open_list)
            
            if current == goal:
                # 重构路径
                path = []
                while current in came_from:
                    path.append(current)
                    current = came_from[current]
                path.append(start)
                return path[::-1]
            
            closed_set.add(current)
            
            # 检查四个方向的邻居
            for dy, dx in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                neighbor = (current[0] + dy, current[1] + dx)
                
                # 检查边界
                if (neighbor[0] < 0 or neighbor[0] >= self.maze_height or 
                    neighbor[1] < 0 or neighbor[1] >= self.maze_width):
                    continue
                
                # 检查是否是墙壁
                if self.maze[neighbor[0], neighbor[1]] == 1:
                    continue
                
                # 检查是否已经在关闭列表中
                if neighbor in closed_set:
                    continue
                
                # 在探索模式下，给最近访问的位置增加额外成本
                extra_cost = 0
                if avoid_recent and neighbor in self.last_positions[-3:]:
                    extra_cost = 5  # 增加成本，但不完全禁止
                
                tentative_g_score = g_score[current] + 1 + extra_cost
                
                if neighbor not in g_score or tentative_g_score < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g_score
                    f_score[neighbor] = tentative_g_score + heuristic(neighbor)
                    
                    if neighbor not in [item[1] for item in open_list]:
                        heapq.heappush(open_list, (f_score[neighbor], neighbor))
        
        return None  # 没有找到路径
    
    def clear_trail(self):
        """清空轨迹"""
        self.player_trail = [tuple(self.player_pos)]
        self.planned_path = []
        self.update_display()
    
    def go_home(self):
        """回家功能 - 寻找回到起始位置的路径并自动移动"""
        if self.is_auto_moving:
            self.status_label.config(text="正在移动中，请稍候...")
            return
            
        self.clear_trail()
        current_pos = tuple(self.player_pos)
        start_pos = tuple(self.start_pos)
        
        path = self.astar_pathfinding(current_pos, start_pos)
        
        if path:
            self.planned_path = path
            self.status_label.config(text=f"找到回家路径，共{len(path)}步，开始自动移动...")
            print(f"回家路径: {path}")
            self.update_display()
            # 开始自动移动
            self.start_auto_move(path)
        else:
            self.status_label.config(text="无法找到回家路径")
            print("无法找到回家路径")
            self.update_display()
    
    def find_path(self):
        """寻路功能 - 寻找到最近出口的路径并自动移动"""
        if self.is_auto_moving:
            self.status_label.config(text="正在移动中，请稍候...")
            return
            
        self.clear_trail()
        
        if not self.exits:
            self.status_label.config(text="请先完成探索以找到出口")
            return
        
        current_pos = tuple(self.player_pos)
        best_path = None
        shortest_distance = float('inf')
        
        # 寻找到最近出口的路径
        for exit_pos in self.exits:
            path = self.astar_pathfinding(current_pos, exit_pos)
            if path and len(path) < shortest_distance:
                best_path = path
                shortest_distance = len(path)
        
        if best_path:
            self.planned_path = best_path
            self.status_label.config(text=f"找到出口路径，共{len(best_path)}步，开始自动移动...")
            print(f"出口路径: {best_path}")
            self.update_display()
            # 开始自动移动
            self.start_auto_move(best_path)
        else:
            self.status_label.config(text="无法找到出口路径")
            print("无法找到出口路径")
            self.update_display()
    
    def start_auto_move(self, path):
        """开始自动移动"""
        if not path or len(path) < 2:
            return
        
        self.is_auto_moving = True
        self.auto_move_path = path
        self.auto_move_index = 1  # 从第1个位置开始（第0个是当前位置）
        self.auto_move_step()
    
    def auto_move_step(self):
        """执行一步自动移动"""
        if not self.is_auto_moving or self.auto_move_index >= len(self.auto_move_path):
            # 移动完成
            self.is_auto_moving = False
            self.auto_move_path = []
            self.auto_move_index = 0
            self.status_label.config(text="移动完成！")
            return
        
        # 获取下一个位置
        next_pos = self.auto_move_path[self.auto_move_index]
        current_pos = tuple(self.player_pos)
        
        # 计算移动方向
        dy = next_pos[0] - current_pos[0]
        dx = next_pos[1] - current_pos[1]
        
        # 执行移动
        self.move_player(dy, dx)
        
        # 更新索引
        self.auto_move_index += 1
        
        # 更新状态显示
        remaining_steps = len(self.auto_move_path) - self.auto_move_index
        self.status_label.config(text=f"自动移动中... 还剩 {remaining_steps} 步")
        
                # 继续下一步移动
        self.root.after(200, self.auto_move_step)  # 200ms延迟，让用户看到移动过程
    
    def stop_auto_move(self):
        """停止自动移动并清空轨迹"""
        if self.is_auto_moving:
            self.is_auto_moving = False
            self.auto_move_path = []
            self.auto_move_index = 0
            self.status_label.config(text="自动移动已停止，轨迹已清空")
        else:
            self.status_label.config(text="当前没有自动移动")
        
        # 清空轨迹和规划路径
        self.clear_trail()
 
    def find_exits(self):
        """寻找迷宫的可能出口"""
        self.exits = []
        
        # 检查四个边界上的可通行点
        for i in range(self.maze_height):
            for j in range(self.maze_width):
                # 只检查边界位置
                is_boundary = (i == 0 or i == self.maze_height - 1 or 
                              j == 0 or j == self.maze_width - 1)
                
                if is_boundary and self.maze[i, j] == 0 and self.calc_dist(self.start_pos[0], self.start_pos[1], i, j) > 10:  # 可通行的边界点
                    # 检查是否被探索过（如果要求只标记探索过的出口）
                    # 或者直接标记所有边界出口
                    self.exits.append((i, j))
        
        print(f"找到 {len(self.exits)} 个可能的出口: {self.exits}")

    def is_frontier(self, i, j):
        if self.explored_map[i, j] == 0:
            for dy, dx in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                if not (0 <= i + dy < self.maze_height and 0 <= j + dx < self.maze_width):
                    continue
                if self.explored_map[i + dy, j + dx] == 1 and self.maze[i + dy, j + dx] == 0:
                    return True
        return False
    
    def on_range_change(self, value):
        """雷达范围改变"""
        self.radar_range = int(value)
        self.radar = Radar(self.maze, self.player_pos, self.radar_range)
        self.radar_info_label.config(text=f"雷达范围: {self.radar_range}")
        self.update_radar_scan()
        self.update_display()
    
    def update_radar_scan(self):
        """更新雷达扫描并记录探索区域"""
        if hasattr(self, 'radar'):
            self.radar.move_radar(self.player_pos)
            scan_data = self.radar.scan_360(self.scan_angle_step)
            
            # 标记雷达扫描过的区域
            for angle, (distance, hit_point) in scan_data.items():
                # 使用Bresenham算法标记射线路径上的所有点
                self.mark_ray_path(self.player_pos, angle, distance)
    
    def mark_ray_path(self, start_pos, angle, distance):
        """标记射线路径上的所有点为已探索"""
        start_y, start_x = start_pos
        angle_rad = math.radians(angle)
        
        # 沿射线路径标记点
        for step in range(int(distance) + 1):
            y = start_y + step * math.sin(angle_rad)
            x = start_x + step * math.cos(angle_rad)
            
            grid_y = int(round(y))
            grid_x = int(round(x))
            
            if (0 <= grid_y < self.maze_height and 0 <= grid_x < self.maze_width):
                self.explored_map[grid_y, grid_x] = True

    def move_player(self, dy, dx):
        """移动玩家"""
        current_row, current_col = self.player_pos
        new_row = current_row + dy
        new_col = current_col + dx
        
        # 检查边界
        if (0 <= new_row < self.maze_height and 0 <= new_col < self.maze_width):
            # 检查是否是通道（0表示可通行，1表示墙壁）
            if self.maze[new_row, new_col] == 0:
                self.player_pos = [new_row, new_col]
                self.moves += 1
                
                # 记录轨迹
                self.player_trail.append(tuple(self.player_pos))
                
                # 更新雷达扫描
                self.update_radar_scan()
                
                self.update_display()

            else:
                # 撞墙了
                if self.is_auto_moving:
                    # 如果在自动移动过程中撞墙，停止自动移动
                    self.stop_auto_move()
                    self.status_label.config(text="自动移动遇到障碍，已停止")
                else:
                    self.status_label.config(text="前方是墙壁，无法通过！")
                    self.root.after(1500, lambda: self.status_label.config(text="使用WASD或方向键移动"))
    
       
    def update_display(self):
        """更新双画布显示"""
        # 更新明图（完整地图视图）
        self.update_bright_map()
        
        # 更新暗图（探索区域视图）
        self.update_dark_map()
        
        # 更新步数显示
        self.moves_label.config(text=f"步数: {self.moves}")
        
        # 更新坐标显示
        player_row, player_col = self.player_pos
        self.position_label.config(text=f"坐标: ({player_row}, {player_col})")
    
    def update_bright_map(self):
        """更新明图 - 显示完整地图和雷达射线"""
        self.bright_canvas.delete("all")
        
        # 绘制完整迷宫
        for row in range(self.maze_height):
            for col in range(self.maze_width):
                x1 = col * self.cell_size
                y1 = row * self.cell_size
                x2 = x1 + self.cell_size
                y2 = y1 + self.cell_size
                
                if self.maze[row, col] == 1:
                    # 墙壁 - 黑色
                    self.bright_canvas.create_rectangle(
                        x1, y1, x2, y2,
                        fill='black', outline=''
                    )
                else:
                    # 通道 - 白色
                    self.bright_canvas.create_rectangle(
                        x1, y1, x2, y2,
                        fill='white', outline=''
                    )
        
        # 绘制雷达射线
        if self.show_rays and hasattr(self, 'radar'):
            scan_data = self.radar.scan_360(self.scan_angle_step)
            player_x = self.player_pos[1] * self.cell_size + self.cell_size // 2
            player_y = self.player_pos[0] * self.cell_size + self.cell_size // 2
            
            for angle, (distance, hit_point) in scan_data.items():
                if angle % (self.scan_angle_step * 2) == 0:  # 减少射线密度
                    angle_rad = math.radians(angle)
                    end_x = player_x + distance * self.cell_size * math.cos(angle_rad) / 10
                    end_y = player_y + distance * self.cell_size * math.sin(angle_rad) / 10
                    
                    self.bright_canvas.create_line(
                        player_x, player_y, end_x, end_y,
                        fill='cyan', width=1, stipple='gray25'
                    )
        
        # 绘制目标点
        self.draw_target_on_canvas(self.bright_canvas)
        
        # 绘制玩家轨迹
        self.draw_player_trail_on_canvas(self.bright_canvas)
        
        # 绘制玩家
        self.draw_player_on_canvas(self.bright_canvas)
    
    def update_dark_map(self):
        """更新暗图 - 只显示探索过的区域"""
        self.dark_canvas.delete("all")
        
        # 绘制探索过的区域
        for row in range(self.maze_height):
            for col in range(self.maze_width):
                x1 = col * self.cell_size
                y1 = row * self.cell_size
                x2 = x1 + self.cell_size
                y2 = y1 + self.cell_size
                
                if self.explored_map[row, col]:
                    # 已探索区域
                    if self.maze[row, col] == 1:
                        # 墙壁 - 深灰色
                        self.dark_canvas.create_rectangle(
                            x1, y1, x2, y2,
                            fill='#404040', outline='#606060'
                        )
                    else:
                        # 通道 - 浅灰色
                        self.dark_canvas.create_rectangle(
                            x1, y1, x2, y2,
                            fill='#c0c0c0', outline='#808080'
                        )
                else:
                    # 未探索区域 - 黑色
                    self.dark_canvas.create_rectangle(
                        x1, y1, x2, y2,
                        fill='black', outline='black'
                    )
        
        # 绘制目标点（如果在探索区域内）
        # target_row, target_col = self.target_pos
        # if self.explored_map[target_row, target_col]:
        #     self.draw_target_on_canvas(self.dark_canvas)
        
        # 绘制出口
        self.draw_exits_on_canvas(self.dark_canvas)
        
        # 绘制起始位置
        self.draw_start_position_on_canvas(self.dark_canvas)
        
        # 绘制规划路径
        self.draw_planned_path_on_canvas(self.dark_canvas)
        
        # 绘制玩家
        self.draw_player_on_canvas(self.dark_canvas)
    
    def draw_exits_on_canvas(self, canvas):
        """在指定画布上绘制出口"""
        for exit_row, exit_col in self.exits:
            exit_x = exit_col * self.cell_size + self.cell_size // 2
            exit_y = exit_row * self.cell_size + self.cell_size // 2
            radius = max(4, self.cell_size // 2)
            
            # 绘制绿色圆形标记出口
            canvas.create_oval(
                exit_x - radius, exit_y - radius,
                exit_x + radius, exit_y + radius,
                fill='green', outline='darkgreen', width=2
            )
            
            # 在出口上添加文字标记
            canvas.create_text(
                exit_x, exit_y,
                text="EXIT",
                fill='white',
                font=("Arial", max(6, self.cell_size // 4), "bold")
            )
    
    def draw_start_position_on_canvas(self, canvas):
        """在指定画布上绘制起始位置"""
        start_row, start_col = self.start_pos
        start_x = start_col * self.cell_size + self.cell_size // 2
        start_y = start_row * self.cell_size + self.cell_size // 2
        radius = max(4, self.cell_size // 2)
        
        # 绘制黄色方形标记起始位置
        canvas.create_rectangle(
            start_x - radius, start_y - radius,
            start_x + radius, start_y + radius,
            fill='yellow', outline='orange', width=2
        )
        
        # 在起始位置上添加文字标记
        canvas.create_text(
            start_x, start_y,
            text="HOME",
            fill='black',
            font=("Arial", max(6, self.cell_size // 4), "bold")
        )
    
    def draw_planned_path_on_canvas(self, canvas):
        """在指定画布上绘制规划路径"""
        if len(self.planned_path) < 2:
            return
            
        # 绘制路径线条
        for i in range(len(self.planned_path) - 1):
            start_row, start_col = self.planned_path[i]
            end_row, end_col = self.planned_path[i + 1]
            
            start_x = start_col * self.cell_size + self.cell_size // 2
            start_y = start_row * self.cell_size + self.cell_size // 2
            end_x = end_col * self.cell_size + self.cell_size // 2
            end_y = end_row * self.cell_size + self.cell_size // 2
            
            # 使用橙色线条绘制规划路径
            canvas.create_line(
                start_x, start_y, end_x, end_y,
                fill='orange', width=3
            )
        
        # 在路径点上绘制小圆点
        for i, (row, col) in enumerate(self.planned_path):
            x = col * self.cell_size + self.cell_size // 2
            y = row * self.cell_size + self.cell_size // 2
            radius = max(2, self.cell_size // 8)
            
            canvas.create_oval(
                x - radius, y - radius,
                x + radius, y + radius,
                fill='orange', outline='darkorange'
            )

    def draw_player_trail_on_canvas(self, canvas):
        """在指定画布上绘制玩家轨迹"""
        if len(self.player_trail) < 2:
            return
            
        # 绘制轨迹线条
        for i in range(len(self.player_trail) - 1):
            start_row, start_col = self.player_trail[i]
            end_row, end_col = self.player_trail[i + 1]
            
            start_x = start_col * self.cell_size + self.cell_size // 2
            start_y = start_row * self.cell_size + self.cell_size // 2
            end_x = end_col * self.cell_size + self.cell_size // 2
            end_y = end_row * self.cell_size + self.cell_size // 2
            
            canvas.create_line(
                start_x, start_y, end_x, end_y,
                fill='red', width=2
            )

    def draw_player_on_canvas(self, canvas):
        """在指定画布上绘制玩家"""
        player_row, player_col = self.player_pos
        player_x = player_col * self.cell_size + self.cell_size // 2
        player_y = player_row * self.cell_size + self.cell_size // 2
        radius = max(3, self.cell_size // 3)
        
        canvas.create_oval(
            player_x - radius, player_y - radius,
            player_x + radius, player_y + radius,
            fill='blue', outline='darkblue', width=2
        )
    
    def draw_target_on_canvas(self, canvas):
        """在指定画布上绘制目标点"""
        # target_row, target_col = self.target_pos
        # target_x1 = target_col * self.cell_size + 2
        # target_y1 = target_row * self.cell_size + 2
        # target_x2 = target_x1 + self.cell_size - 4
        # target_y2 = target_y1 + self.cell_size - 4
        
        # canvas.create_rectangle(
        #     target_x1, target_y1, target_x2, target_y2,
        #     fill='red', outline='darkred', width=2
        # )
    

    def run(self):
        """运行游戏"""
        self.root.mainloop()

def main():
    """主函数"""
    try:
        print("启动迷宫行走游戏...")
        print("使用WASD键或方向键控制蓝色圆点移动")
        print("目标：到达红色方块的位置")
        
        game = MazeWalker()
        game.run()
        
    except Exception as e:
        print(f"启动游戏时出错: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 
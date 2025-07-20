import math
import numpy as np

class Object2D:
    """Kelas dasar untuk semua objek 2D"""
    def __init__(self, obj_type, points, color=(1.0, 1.0, 1.0), line_width=1.0):
        self.type = obj_type
        self.points = points.copy() if points else []
        self.color = color
        self.line_width = line_width
        self.visible = True
        self.corners = None
        self.transformed = False
    
    def get_center(self):
        if not self.points:
            return (0, 0)
        
        x_sum = sum(p[0] for p in self.points)
        y_sum = sum(p[1] for p in self.points)
        return (x_sum / len(self.points), y_sum / len(self.points))


class Point2D(Object2D):
    def __init__(self, x, y, color=(1.0, 1.0, 1.0), size=1.0):
        super().__init__('point', [(x, y)], color, size)
    
    @property
    def x(self):
        return self.points[0][0]
    
    @property
    def y(self):
        return self.points[0][1]


class Line2D(Object2D):
    def __init__(self, x1, y1, x2, y2, color=(1.0, 1.0, 1.0), width=1.0):
        super().__init__('line', [(x1, y1), (x2, y2)], color, width)
    
    @property
    def start_point(self):
        return self.points[0]
    
    @property
    def end_point(self):
        return self.points[1]
    
    @property
    def length(self):
        """Menghitung panjang garis"""
        x1, y1 = self.points[0]
        x2, y2 = self.points[1]
        return math.sqrt((x2 - x1)**2 + (y2 - y1)**2)


class Rectangle2D(Object2D):
    def __init__(self, x1, y1, x2, y2, color=(1.0, 1.0, 1.0), width=1.0):
        min_x, min_y = min(x1, x2), min(y1, y2)
        max_x, max_y = max(x1, x2), max(y1, y2)
        super().__init__('rectangle', [(min_x, min_y), (max_x, max_y)], color, width)

        self.corners = [
            (min_x, min_y),  # Bottom-left
            (max_x, min_y),  # Bottom-right
            (max_x, max_y),  # Top-right
            (min_x, max_y)   # Top-left
        ]
    
    @property
    def width(self):
        """Mendapatkan lebar persegi panjang"""
        if len(self.points) == 2:
            return abs(self.points[1][0] - self.points[0][0])
        elif self.corners:
            x_values = [p[0] for p in self.corners]
            return max(x_values) - min(x_values)
        return 0
    
    @property
    def height(self):
        """Mendapatkan tinggi persegi panjang"""
        if len(self.points) == 2:
            return abs(self.points[1][1] - self.points[0][1])
        elif self.corners:
            y_values = [p[1] for p in self.corners]
            return max(y_values) - min(y_values)
        return 0


class Ellipse2D(Object2D):
    def __init__(self, x1, y1, x2, y2, color=(1.0, 1.0, 1.0), width=1.0):
        min_x, min_y = min(x1, x2), min(y1, y2)
        max_x, max_y = max(x1, x2), max(y1, y2)
        super().__init__('ellipse', [(min_x, min_y), (max_x, max_y)], color, width)

        cx = (min_x + max_x) / 2
        cy = (min_y + max_y) / 2
        rx = abs(max_x - min_x) / 2
        ry = abs(max_y - min_y) / 2
        
        self.center = (cx, cy)
        self.radii = (rx, ry)

        self.rotated_points = []
        steps = 36
        for i in range(steps):
            angle_rad = math.radians(i * (360 / steps))
            point_x = cx + rx * math.cos(angle_rad)
            point_y = cy + ry * math.sin(angle_rad)
            self.rotated_points.append((point_x, point_y))

        self.corners = None

        self.transformed = False
        self.rotation_angle = 0
    
    @property
    def cx(self):
        return self.center[0]
    
    @property
    def cy(self):
        return self.center[1]
    
    @property
    def rx(self):
        return self.radii[0]
    
    @property
    def ry(self):
        return self.radii[1]

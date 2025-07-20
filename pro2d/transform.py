import math
import numpy as np

class Transform2D:
    @staticmethod
    def translate(obj, dx, dy):
        new_points = []
        
        if obj.type == 'rectangle':
            new_corners = []
            for point in obj.corners:
                new_x = point[0] + dx
                new_y = point[1] + dy
                new_corners.append((new_x, new_y))
            obj.corners = new_corners
            
            for point in obj.points:
                new_x = point[0] + dx
                new_y = point[1] + dy
                new_points.append((new_x, new_y))
                
        elif obj.type == 'ellipse':
            if hasattr(obj, 'center'):
                cx, cy = obj.center
                obj.center = (cx + dx, cy + dy)
            
            if hasattr(obj, 'rotated_points') and obj.rotated_points:
                new_rotated_points = []
                for point in obj.rotated_points:
                    new_x = point[0] + dx
                    new_y = point[1] + dy
                    new_rotated_points.append((new_x, new_y))
                obj.rotated_points = new_rotated_points
            
            for point in obj.points:
                new_x = point[0] + dx
                new_y = point[1] + dy
                new_points.append((new_x, new_y))
                
        else:
            for point in obj.points:
                new_x = point[0] + dx
                new_y = point[1] + dy
                new_points.append((new_x, new_y))
        
        obj.points = new_points
    
    @staticmethod
    def rotate(obj, angle, pivot_x=0, pivot_y=0):
        if obj is None or not hasattr(obj, 'points') or not obj.points:
            print("Warning: Cannot rotate - invalid object or no points defined")
            return
        
        cos_a = math.cos(math.radians(angle))
        sin_a = math.sin(math.radians(angle))
        
        if obj.type == 'rectangle':
            if len(obj.points) == 2 and not obj.transformed:
                pass
            
            new_corners = []
            for point in obj.corners:
                x = point[0] - pivot_x
                y = point[1] - pivot_y
                
                new_x = x * cos_a - y * sin_a
                new_y = x * sin_a + y * cos_a
                
                new_x += pivot_x
                new_y += pivot_y
                
                new_corners.append((new_x, new_y))
            
            obj.corners = new_corners
            obj.points = new_corners
            obj.transformed = True
            
            return
        
        elif obj.type == 'ellipse':
            if hasattr(obj, 'center') and hasattr(obj, 'radii'):
                cx, cy = obj.center
                rx, ry = obj.radii
            else:
                x1, y1 = obj.points[0]
                x2, y2 = obj.points[1]
                cx = (x1 + x2) / 2
                cy = (y1 + y2) / 2
                rx = abs(x2 - x1) / 2
                ry = abs(y2 - y1) / 2
                obj.center = (cx, cy)
                obj.radii = (rx, ry)
            
            if not obj.transformed:
                obj.rotation_angle = 0
                obj.transformed = True
                
                if not hasattr(obj, 'rotated_points') or not obj.rotated_points:
                    obj.rotated_points = []
                    steps = 36
                    for i in range(steps):
                        angle_rad = math.radians(i * (360 / steps))
                        point_x = cx + rx * math.cos(angle_rad)
                        point_y = cy + ry * math.sin(angle_rad)
                        obj.rotated_points.append((point_x, point_y))
            
            obj.rotation_angle += angle
            
            x = cx - pivot_x
            y = cy - pivot_y
            
            new_cx = x * cos_a - y * sin_a
            new_cy = x * sin_a + y * cos_a
            
            new_cx += pivot_x
            new_cy += pivot_y
            
            obj.center = (new_cx, new_cy)
            
            new_points = []
            for point in obj.rotated_points:
                x = point[0] - pivot_x
                y = point[1] - pivot_y
                
                new_x = x * cos_a - y * sin_a
                new_y = x * sin_a + y * cos_a
                
                new_x += pivot_x
                new_y += pivot_y
                
                new_points.append((new_x, new_y))
            
            obj.rotated_points = new_points
            return
        
        new_points = []
        for point in obj.points:
            x = point[0] - pivot_x
            y = point[1] - pivot_y
            
            new_x = x * cos_a - y * sin_a
            new_y = x * sin_a + y * cos_a
            
            new_x += pivot_x
            new_y += pivot_y
            
            new_points.append((new_x, new_y))
        obj.points = new_points
    
    @staticmethod
    def scale(obj, sx, sy, pivot_x=0, pivot_y=0):
        if obj is None or not hasattr(obj, 'points') or not obj.points:
            print("Warning: Cannot scale - invalid object or no points defined")
            return
        
        if obj.type == 'rectangle':
            if len(obj.points) == 2 and not obj.transformed:
                if pivot_x == 0 and pivot_y == 0:
                    x1, y1 = obj.points[0]
                    x2, y2 = obj.points[1]
                    pivot_x = (x1 + x2) / 2
                    pivot_y = (y1 + y2) / 2
            
            elif len(obj.points) == 4:
                if pivot_x == 0 and pivot_y == 0:
                    x_sum = sum(p[0] for p in obj.points)
                    y_sum = sum(p[1] for p in obj.points)
                    pivot_x = x_sum / 4
                    pivot_y = y_sum / 4
            
            new_corners = []
            for point in obj.corners:
                x = point[0] - pivot_x
                y = point[1] - pivot_y
                
                new_x = x * sx
                new_y = y * sy
                
                new_x += pivot_x
                new_y += pivot_y
                
                new_corners.append((new_x, new_y))
            
            obj.corners = new_corners
            obj.points = new_corners
            obj.transformed = True
            
            return
        
        elif obj.type == 'ellipse':
            if hasattr(obj, 'center') and hasattr(obj, 'radii'):
                cx, cy = obj.center
                rx, ry = obj.radii
            else:
                x1, y1 = obj.points[0]
                x2, y2 = obj.points[1]
                cx = (x1 + x2) / 2
                cy = (y1 + y2) / 2
                rx = abs(x2 - x1) / 2
                ry = abs(y2 - y1) / 2
                obj.center = (cx, cy)
                obj.radii = (rx, ry)
            
            if pivot_x == 0 and pivot_y == 0:
                pivot_x = cx
                pivot_y = cy
            
            obj.transformed = True
            
            x = cx - pivot_x
            y = cy - pivot_y
            
            new_cx = x * sx
            new_cy = y * sy
            
            new_cx += pivot_x
            new_cy += pivot_y
            
            new_rx = rx * sx
            new_ry = ry * sy
            
            obj.center = (new_cx, new_cy)
            obj.radii = (new_rx, new_ry)
            
            rotation_angle = obj.rotation_angle if hasattr(obj, 'rotation_angle') else 0
            
            new_rotated_points = []
            steps = 36
            
            for i in range(steps):
                angle = i * (360 / steps)
                angle_rad = math.radians(angle)
                
                x = new_rx * math.cos(angle_rad)
                y = new_ry * math.sin(angle_rad)
                
                if rotation_angle != 0:
                    rotation_rad = math.radians(rotation_angle)
                    cos_rot = math.cos(rotation_rad)
                    sin_rot = math.sin(rotation_rad)
                    rotated_x = x * cos_rot - y * sin_rot
                    rotated_y = x * sin_rot + y * cos_rot
                    x, y = rotated_x, rotated_y
                
                point_x = new_cx + x
                point_y = new_cy + y
                
                new_rotated_points.append((point_x, point_y))
            
            obj.rotated_points = new_rotated_points
            
            min_x = new_cx - new_rx
            max_x = new_cx + new_rx
            min_y = new_cy - new_ry
            max_y = new_cy + new_ry
            obj.points = [(min_x, min_y), (max_x, max_y)]
            
            return
        
        new_points = []
        for point in obj.points:
            x = point[0] - pivot_x
            y = point[1] - pivot_y
            
            new_x = x * sx
            new_y = y * sy
            
            new_x += pivot_x
            new_y += pivot_y
            
            new_points.append((new_x, new_y))
        obj.points = new_points
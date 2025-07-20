# Algoritma clipping dan windowing untuk grafik 2D.

class Clipper:
    @staticmethod
    def is_point_inside_window(x, y, window_bounds):
        return (window_bounds[0] <= x <= window_bounds[1] and 
                window_bounds[2] <= y <= window_bounds[3])
    
    @staticmethod
    def liang_barsky_clip(x1, y1, x2, y2, window_bounds):
        # Batas-batas window
        xmin, xmax, ymin, ymax = window_bounds

        dx = x2 - x1
        dy = y2 - y1
        
        p = [-dx, dx, -dy, dy]
        q = [x1 - xmin, xmax - x1, y1 - ymin, ymax - y1]
        
        u1 = 0.0
        u2 = 1.0
        
        for i in range(4):
            if p[i] == 0:
                if q[i] < 0:
                    return (False, x1, y1, x2, y2)
            else:
                r = q[i] / p[i]
                if p[i] < 0:
                    u1 = max(u1, r)
                else:
                    u2 = min(u2, r)
        
        if u1 > u2:
            return (False, x1, y1, x2, y2)
        
        # Menghitung titik akhir hasil clipping
        cx1 = x1 + u1 * dx
        cy1 = y1 + u1 * dy
        cx2 = x1 + u2 * dx
        cy2 = y1 + u2 * dy
        
        return (True, cx1, cy1, cx2, cy2)
    
    @staticmethod
    def cohen_sutherland_clip(x1, y1, x2, y2, window_bounds):
        # Batas-batas window
        xmin, xmax, ymin, ymax = window_bounds
        
        # Kode region
        INSIDE = 0  # 0000
        LEFT = 1    # 0001
        RIGHT = 2   # 0010
        BOTTOM = 4  # 0100
        TOP = 8     # 1000
        
        def compute_code(x, y):
            code = INSIDE
            if x < xmin:
                code |= LEFT
            elif x > xmax:
                code |= RIGHT
            if y < ymin:
                code |= BOTTOM
            elif y > ymax:
                code |= TOP
            return code
        code1 = compute_code(x1, y1)
        code2 = compute_code(x2, y2)

        clipped = False
        
        while True:
            if code1 == 0 and code2 == 0:
                clipped = True
                break
            
            if (code1 & code2) != 0:
                clipped = False
                break
            
            clipped = True

            code_out = code1 if code1 != 0 else code2

            x, y = 0, 0
            
            if code_out & TOP:
                if y2 - y1 != 0:
                    x = x1 + (x2 - x1) * (ymax - y1) / (y2 - y1)
                else:
                    x = x1
                y = ymax
            elif code_out & BOTTOM:
                if y2 - y1 != 0:
                    x = x1 + (x2 - x1) * (ymin - y1) / (y2 - y1)
                else:
                    x = x1
                y = ymin
            elif code_out & RIGHT:
                if x2 - x1 != 0:
                    y = y1 + (y2 - y1) * (xmax - x1) / (x2 - x1)
                else:
                    y = y1
                x = xmax
            elif code_out & LEFT:
                if x2 - x1 != 0:
                    y = y1 + (y2 - y1) * (xmin - x1) / (x2 - x1)
                else:
                    y = y1
                x = xmin

            if code_out == code1:
                x1, y1 = x, y
                code1 = compute_code(x1, y1)
            else:
                x2, y2 = x, y
                code2 = compute_code(x2, y2)
        
        return (clipped, x1, y1, x2, y2)
    
    @staticmethod
    def clip_rectangle(rect_points, window_bounds):
        xmin, xmax, ymin, ymax = window_bounds

        points_inside = 0
        for point in rect_points:
            if Clipper.is_point_inside_window(point[0], point[1], window_bounds):
                points_inside += 1

        if points_inside == len(rect_points):
            return False, True, False, rect_points

        if points_inside == 0:

            window_corners = [
                (xmin, ymin), (xmax, ymin), (xmax, ymax), (xmin, ymax)
            ]

            rect_xmin = min(p[0] for p in rect_points)
            rect_xmax = max(p[0] for p in rect_points)
            rect_ymin = min(p[1] for p in rect_points)
            rect_ymax = max(p[1] for p in rect_points)

            if rect_xmin <= xmin and rect_xmax >= xmax and rect_ymin <= ymin and rect_ymax >= ymax:
                return True, False, False, window_corners
            
            for i in range(len(rect_points)):
                x1, y1 = rect_points[i]
                x2, y2 = rect_points[(i + 1) % len(rect_points)]

                clipped, _, _, _, _ = Clipper.cohen_sutherland_clip(x1, y1, x2, y2, window_bounds)
                if clipped:
                    return True, False, False, None
            
            return False, False, True, None

        return True, False, False, None
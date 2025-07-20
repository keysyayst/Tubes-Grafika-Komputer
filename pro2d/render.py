import math
from OpenGL.GL import *
from pro2d.clipping import Clipper

# Kelas yang berisi metode-metode untuk merender objek grafik 2D.
class Renderer:
    @staticmethod
    def draw_point(x, y, color, size=5):
        glColor3f(*color)
        glPointSize(size)
        glBegin(GL_POINTS)
        glVertex2f(x, y)
        glEnd()
    
    @staticmethod
    def draw_line(x1, y1, x2, y2, color, width=1):
        glColor3f(*color)
        glLineWidth(width)
        glBegin(GL_LINES)
        glVertex2f(x1, y1)
        glVertex2f(x2, y2)
        glEnd()
    
    @staticmethod
    def draw_rectangle(points, color, width=1):
        glColor3f(*color)
        glLineWidth(width)
        glBegin(GL_LINE_LOOP)
        
        if len(points) == 2:
            x1, y1 = points[0]  # min_x, min_y
            x2, y2 = points[1]  # max_x, max_y

            glVertex2f(x1, y1)  # Bottom-left
            glVertex2f(x2, y1)  # Bottom-right
            glVertex2f(x2, y2)  # Top-right
            glVertex2f(x1, y2)  # Top-left
        elif len(points) == 4:
            for point in points:
                glVertex2f(point[0], point[1])
        else:
            print(f"Error: Rectangle requires 2 or 4 points, but {len(points)} were provided.")
        
        glEnd()
    
    @staticmethod
    def draw_ellipse(cx, cy, rx, ry, color, width=1):
        glColor3f(*color)
        glLineWidth(width)
        glBegin(GL_LINE_LOOP)
        
        for i in range(360):
            angle = math.radians(i)
            x = cx + rx * math.cos(angle)
            y = cy + ry * math.sin(angle)
            glVertex2f(x, y)
        
        glEnd()
    
    @staticmethod
    def draw_transformed_ellipse(obj, color, width=1):
        glColor3f(*color)
        glLineWidth(width)

        if hasattr(obj, 'rotated_points') and obj.rotated_points:
            glBegin(GL_LINE_LOOP)
            for point in obj.rotated_points:
                glVertex2f(point[0], point[1])
            glEnd()
        else:
            cx, cy = obj.center if hasattr(obj, 'center') else (0, 0)
            rx, ry = obj.radii if hasattr(obj, 'radii') else (1, 1)
            
            glBegin(GL_LINE_LOOP)
            for i in range(36):
                angle = math.radians(i * 10)
                x = cx + rx * math.cos(angle)
                y = cy + ry * math.sin(angle)
                glVertex2f(x, y)
            glEnd()
    
    @staticmethod
    def draw_axes(x_min=-400, x_max=400, y_min=-300, y_max=300, grid_spacing=50):
        # Draw X axis (horizontal) in red
        glColor3f(1.0, 0.0, 0.0)  # red
        glLineWidth(1.5)
        glBegin(GL_LINES)
        glVertex2f(x_min, 0)
        glVertex2f(x_max, 0)
        glEnd()
        
        # Draw Y axis (vertical) in blue
        glColor3f(0.0, 0.0, 1.0)  # blue
        glLineWidth(1.5)
        glBegin(GL_LINES)
        glVertex2f(0, y_min)
        glVertex2f(0, y_max)
        glEnd()
        
        # Draw grid lines
        glColor3f(0.2, 0.2, 0.2)  # dark gray
        glLineWidth(0.5)
        glBegin(GL_LINES)
        
        # Horizontal grid lines
        for y in range(0, y_max + 1, grid_spacing):
            if y != 0:
                glVertex2f(x_min, y)
                glVertex2f(x_max, y)
                glVertex2f(x_min, -y)
                glVertex2f(x_max, -y)
        
        # Vertical grid lines
        for x in range(0, x_max + 1, grid_spacing):
            if x != 0:
                glVertex2f(x, y_min)
                glVertex2f(x, y_max)
                glVertex2f(-x, y_min)
                glVertex2f(-x, y_max)
        
        glEnd()

        glColor3f(1.0, 1.0, 1.0)  # white
        glPointSize(3)
        glBegin(GL_POINTS)

        for x in range(0, x_max + 1, 100):
            if x != 0:
                glVertex2f(x, 0)
                glVertex2f(-x, 0)

        for y in range(0, y_max + 1, 100):
            if y != 0:
                glVertex2f(0, y)
                glVertex2f(0, -y)
        
        glEnd()

        glColor3f(1.0, 1.0, 0.0)  # yellow
        glPointSize(5)
        glBegin(GL_POINTS)
        glVertex2f(0, 0)
        glEnd()
    
    @staticmethod
    def draw_clipping_window(window_bounds, window_active=True, window_temp_points=None, window_definition_mode=False):
        if window_active:
            left, right, bottom, top = window_bounds
            
            glColor3f(1.0, 0.0, 0.0)  # red
            glLineWidth(2.0)
            glBegin(GL_LINE_LOOP)
            glVertex2f(left, bottom)   # Bottom-left
            glVertex2f(right, bottom)  # Bottom-right
            glVertex2f(right, top)     # Top-right
            glVertex2f(left, top)      # Top-left
            glEnd()
            
            glLineWidth(1.0)
            glBegin(GL_LINES)
            glVertex2f(left, bottom)
            glVertex2f(right, top)
            glVertex2f(left, top)
            glVertex2f(right, bottom)
            glEnd()

        if window_definition_mode and window_temp_points:
            glColor3f(1.0, 1.0, 0.0)  # yellow
            glPointSize(7.0)
            glBegin(GL_POINTS)
            for point in window_temp_points:
                glVertex2f(point[0], point[1])
            glEnd()
            
            if len(window_temp_points) == 1 and window_temp_points[0] is not None:
                x, y = window_temp_points[0]
                size = 50
                glColor3f(1.0, 1.0, 0.0)  # yellow
                glLineWidth(1.0)
                glBegin(GL_LINE_LOOP)
                glVertex2f(x, y)
                glVertex2f(x + size, y)
                glVertex2f(x + size, y + size)
                glVertex2f(x, y + size)
                glEnd()
    
    @staticmethod
    def draw_pivot_point(pivot_x, pivot_y, size=10):
        glColor3f(0.0, 1.0, 0.0)  # Green
        glLineWidth(2.0)
        glBegin(GL_LINE_LOOP)
        for i in range(36):
            angle = math.radians(i * 10)
            x = pivot_x + size * math.cos(angle)
            y = pivot_y + size * math.sin(angle)
            glVertex2f(x, y)
        glEnd()
        
        glBegin(GL_LINES)
        glVertex2f(pivot_x - size*1.5, pivot_y)
        glVertex2f(pivot_x + size*1.5, pivot_y)
        glVertex2f(pivot_x, pivot_y - size*1.5)
        glVertex2f(pivot_x, pivot_y + size*1.5)
        glEnd()
        
        glPointSize(5.0)
        glBegin(GL_POINTS)
        glVertex2f(pivot_x, pivot_y)
        glEnd()
    
    @staticmethod
    def render_object(obj, window_bounds=None, clipping_enabled=False, is_selected=False):
        if not obj.visible:
            return
        
        render_color = obj.color
        
        if window_bounds and clipping_enabled:
            inside_window = False
            
            if obj.type == 'point':
                if Clipper.is_point_inside_window(obj.points[0][0], obj.points[0][1], window_bounds):
                    inside_window = True
            
            elif obj.type == 'line' and len(obj.points) >= 2:
    
                pass
            
            elif obj.type == 'ellipse' and len(obj.points) >= 2:
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
                
                points_to_check = []
                points_to_check.append((cx, cy))  # Center
                
                points_to_check.append((cx + rx, cy))  # Right
                points_to_check.append((cx - rx, cy))  # Left
                points_to_check.append((cx, cy + ry))  # Top
                points_to_check.append((cx, cy - ry))  # Bottom

                for point in points_to_check:
                    if Clipper.is_point_inside_window(point[0], point[1], window_bounds):
                        inside_window = True
                        break
            
            if inside_window:
                render_color = (0.0, 1.0, 0.0)  # green untuk dalam window
        
        if is_selected:
            render_color = (1.0, 0.8, 0.2)
        if obj.type == 'point':
            Renderer.draw_point(obj.points[0][0], obj.points[0][1], render_color, obj.line_width)
            
            if is_selected:
                glColor3f(1.0, 1.0, 1.0)
                glLineWidth(1.0)
                glBegin(GL_LINE_LOOP)
                for i in range(36):
                    angle = math.radians(i * 10)
                    x = obj.points[0][0] + (obj.line_width + 5) * math.cos(angle)
                    y = obj.points[0][1] + (obj.line_width + 5) * math.sin(angle)
                    glVertex2f(x, y)
                glEnd()
        
        elif obj.type == 'line':
            if len(obj.points) >= 2:
                x1, y1 = obj.points[0]
                x2, y2 = obj.points[1]
                
                if window_bounds and clipping_enabled:
                    clipped, cx1, cy1, cx2, cy2 = Clipper.cohen_sutherland_clip(x1, y1, x2, y2, window_bounds)
                    if not clipped:
                        faded_color = tuple(c * 0.2 for c in obj.color)
                        Renderer.draw_line(x1, y1, x2, y2, faded_color, obj.line_width)
                    else:
                        if not (Clipper.is_point_inside_window(x1, y1, window_bounds) and 
                                Clipper.is_point_inside_window(x2, y2, window_bounds)):
                            faded_color = tuple(c * 0.4 for c in obj.color)
                            Renderer.draw_line(x1, y1, x2, y2, faded_color, obj.line_width)

                        green_color = (0.0, 1.0, 0.0)
                        Renderer.draw_line(cx1, cy1, cx2, cy2, green_color, obj.line_width)
                else:
                    Renderer.draw_line(x1, y1, x2, y2, render_color, obj.line_width)

                if is_selected:
                    glColor3f(1.0, 1.0, 1.0)  # white
                    glPointSize(8.0)
                    glBegin(GL_POINTS)
                    glVertex2f(x1, y1)
                    glVertex2f(x2, y2)
                    glEnd()
        
        elif obj.type == 'rectangle':
            if len(obj.points) >= 2:
                if len(obj.points) == 4 or obj.corners:
                    rect_points = obj.corners if obj.corners else obj.points
                else:
                    x1, y1 = obj.points[0]
                    x2, y2 = obj.points[1]
                    rect_points = [
                        (x1, y1),  # Bottom-left
                        (x2, y1),  # Bottom-right
                        (x2, y2),  # Top-right
                        (x1, y2),  # Top-left
                    ]
                
                if window_bounds and clipping_enabled:
                    # Potong (clip) persegi panjang terhadap window
                    is_clipped, is_inside, is_outside, clipped_points = Clipper.clip_rectangle(rect_points, window_bounds)
                    
                    if is_inside:
                        Renderer.draw_rectangle(rect_points, (0.0, 1.0, 0.0), obj.line_width)
                    elif is_outside:
                        faded_color = tuple(c * 0.2 for c in obj.color)
                        Renderer.draw_rectangle(rect_points, faded_color, obj.line_width)
                    else:
                        faded_color = tuple(c * 0.4 for c in obj.color)
                        Renderer.draw_rectangle(rect_points, faded_color, obj.line_width)
                        
                        left, right, bottom, top = window_bounds
                        window_corners = [
                            (left, bottom),   # Bottom-left
                            (right, bottom),  # Bottom-right
                            (right, top),     # Top-right
                            (left, top),      # Top-left
                        ]
                        glColor3f(0.0, 1.0, 0.0)  # Green
                        glLineWidth(obj.line_width)
                        glBegin(GL_LINES)
                        for i in range(len(rect_points)):
                            x1, y1 = rect_points[i]
                            x2, y2 = rect_points[(i + 1) % len(rect_points)]
                            
                            clipped, cx1, cy1, cx2, cy2 = Clipper.cohen_sutherland_clip(x1, y1, x2, y2, window_bounds)
                            if clipped:
                                glVertex2f(cx1, cy1)
                                glVertex2f(cx2, cy2)
                        glEnd()
                else:
                    Renderer.draw_rectangle(rect_points, render_color, obj.line_width)
                
                if is_selected:
                    # Draw dots at the corners
                    glColor3f(1.0, 1.0, 1.0)  # white
                    glPointSize(8.0)
                    glBegin(GL_POINTS)
                    
                    if len(obj.points) == 4:
                        for point in obj.points:
                            glVertex2f(point[0], point[1])
                    elif obj.corners:
                        for point in obj.corners:
                            glVertex2f(point[0], point[1])
                    else:
                        x1, y1 = obj.points[0]  # Min x, Min y
                        x2, y2 = obj.points[1]  # Max x, Max y
                        glVertex2f(x1, y1)  # Bottom-left
                        glVertex2f(x2, y1)  # Bottom-right
                        glVertex2f(x2, y2)  # Top-right
                        glVertex2f(x1, y2)  # Top-left
                    glEnd()
        
        elif obj.type == 'ellipse':
            if len(obj.points) >= 2:
                x1, y1 = obj.points[0]
                x2, y2 = obj.points[1]
                
                if window_bounds and clipping_enabled:
                    if hasattr(obj, 'center') and hasattr(obj, 'radii'):
                        cx, cy = obj.center
                        rx, ry = obj.radii
                    else:
                        cx = (x1 + x2) / 2
                        cy = (y1 + y2) / 2
                        rx = abs(x2 - x1) / 2
                        ry = abs(y2 - y1) / 2
                    xmin, xmax, ymin, ymax = window_bounds
                    ellipse_inside = (cx - rx >= xmin and cx + rx <= xmax and 
                                     cy - ry >= ymin and cy + ry <= ymax)
                    ellipse_outside = (cx + rx < xmin or cx - rx > xmax or 
                                      cy + ry < ymin or cy - ry > ymax)
                    
                    if ellipse_inside:
                        green_color = (0.0, 1.0, 0.0)
                        
                        if hasattr(obj, 'transformed') and obj.transformed:
                            Renderer.draw_transformed_ellipse(obj, green_color, obj.line_width)
                        else:
                            Renderer.draw_ellipse(cx, cy, rx, ry, green_color, obj.line_width)
                    
                    elif ellipse_outside:
                        faded_color = tuple(c * 0.2 for c in obj.color)
                        
                        if hasattr(obj, 'transformed') and obj.transformed:
                            Renderer.draw_transformed_ellipse(obj, faded_color, obj.line_width)
                        else:
                            Renderer.draw_ellipse(cx, cy, rx, ry, faded_color, obj.line_width)
                    
                    else:
                        faded_color = tuple(c * 0.4 for c in obj.color)
                        
                        if hasattr(obj, 'transformed') and obj.transformed:
                            Renderer.draw_transformed_ellipse(obj, faded_color, obj.line_width)
                        else:
                            Renderer.draw_ellipse(cx, cy, rx, ry, faded_color, obj.line_width)
                        
                        glColor3f(0.0, 1.0, 0.0)  # Green
                        glLineWidth(obj.line_width)
                        
                        if hasattr(obj, 'transformed') and obj.transformed and hasattr(obj, 'rotated_points'):
                            points = obj.rotated_points
                            glBegin(GL_LINES)
                            for i in range(len(points)):
                                x1, y1 = points[i]
                                x2, y2 = points[(i + 1) % len(points)]

                                clipped, cx1, cy1, cx2, cy2 = Clipper.cohen_sutherland_clip(x1, y1, x2, y2, window_bounds)
                                if clipped:
                                    glVertex2f(cx1, cy1)
                                    glVertex2f(cx2, cy2)
                            glEnd()
                        else:
                            glBegin(GL_LINES)
                            for i in range(36):
                                angle1 = math.radians(i * 10)
                                angle2 = math.radians(((i + 1) % 36) * 10)
                                
                                x1 = cx + rx * math.cos(angle1)
                                y1 = cy + ry * math.sin(angle1)
                                x2 = cx + rx * math.cos(angle2)
                                y2 = cy + ry * math.sin(angle2)
                                
                                clipped, cx1, cy1, cx2, cy2 = Clipper.cohen_sutherland_clip(x1, y1, x2, y2, window_bounds)
                                if clipped:
                                    glVertex2f(cx1, cy1)
                                    glVertex2f(cx2, cy2)
                            glEnd()
                else:
                    if hasattr(obj, 'transformed') and obj.transformed:
                        Renderer.draw_transformed_ellipse(obj, render_color, obj.line_width)
                    else:
                        cx = (x1 + x2) / 2
                        cy = (y1 + y2) / 2
                        rx = abs(x2 - x1) / 2
                        ry = abs(y2 - y1) / 2
                        Renderer.draw_ellipse(cx, cy, rx, ry, render_color, obj.line_width)
                
                if is_selected:
                    if hasattr(obj, 'center'):
                        cx, cy = obj.center
                    else:
                        cx = (x1 + x2) / 2
                        cy = (y1 + y2) / 2
                    
                    glColor3f(1.0, 1.0, 1.0)  # white
                    glPointSize(8.0)
                    glBegin(GL_POINTS)
                    glVertex2f(cx, cy)
                    glEnd()
    
    @staticmethod
    def draw_ui_info(text_lines, x, y, line_height=20):
        if not text_lines:
            return

        glColor4f(0.0, 0.0, 0.0, 0.5)  # Semi-transparent black

        padding = 5
        square_size = line_height * 0.5
        bg_width = square_size + padding * 2
        bg_height = len(text_lines) * line_height + padding * 2

        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glBegin(GL_QUADS)
        glVertex2f(x - padding, y - padding)
        glVertex2f(x + bg_width, y - padding)
        glVertex2f(x + bg_width, y + bg_height)
        glVertex2f(x - padding, y + bg_height)
        glEnd()
        glDisable(GL_BLEND)

        for i, line in enumerate(text_lines):
            y_pos = y + i * line_height + line_height/2

            if "Tool:" in line:
                color = (0.2, 0.8, 0.2)  # Green for tool
            elif "Color:" in line:
                if "RED" in line:
                    color = (1.0, 0.0, 0.0)
                elif "GREEN" in line:
                    color = (0.0, 1.0, 0.0)
                elif "BLUE" in line:
                    color = (0.0, 0.0, 1.0)
                elif "YELLOW" in line:
                    color = (1.0, 1.0, 0.0)
                elif "WHITE" in line:
                    color = (1.0, 1.0, 1.0)
                elif "MAGENTA" in line:
                    color = (1.0, 0.0, 1.0)
                elif "CYAN" in line:
                    color = (0.0, 1.0, 1.0)
                else:
                    color = (0.8, 0.8, 0.8)  # Default gray
            elif "Transform:" in line:
                color = (0.8, 0.6, 0.2)  # Orange for transform
            elif "Selected:" in line:
                color = (1.0, 0.8, 0.2)  # Yellow for selection
            elif "WINDOW" in line or "Window" in line or "Clipping" in line:
                color = (1.0, 0.4, 0.4)  # Red-ish for window/clipping
            else:
                color = (0.8, 0.8, 0.8)  # Default gray

            glColor3f(*color)
            square_size = line_height * 0.5
            glBegin(GL_QUADS)
            glVertex2f(x, y_pos - square_size/2)
            glVertex2f(x + square_size, y_pos - square_size/2)
            glVertex2f(x + square_size, y_pos + square_size/2)
            glVertex2f(x, y_pos + square_size/2)
            glEnd()
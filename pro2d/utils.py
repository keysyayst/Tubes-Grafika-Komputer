import math
import numpy as np

def screen_to_world(x, y, width, height, ortho_bounds):
    normalized_x = 2.0 * x / width - 1.0
    normalized_y = 1.0 - 2.0 * y / height
    
    left, right, bottom, top = ortho_bounds
    world_x = left + (right - left) * (normalized_x + 1.0) / 2.0
    world_y = bottom + (top - bottom) * (normalized_y + 1.0) / 2.0
    
    return (world_x, world_y)

def world_to_screen(world_x, world_y, width, height, ortho_bounds):
    left, right, bottom, top = ortho_bounds
    
    normalized_x = 2.0 * (world_x - left) / (right - left) - 1.0
    normalized_y = 2.0 * (world_y - bottom) / (top - bottom) - 1.0
    
    screen_x = (normalized_x + 1.0) * width / 2.0
    screen_y = (1.0 - normalized_y) * height / 2.0
    
    return (int(screen_x), int(screen_y))

def normalize_rectangle_points(p1, p2):
    x1, y1 = p1
    x2, y2 = p2
    
    min_x = min(x1, x2)
    max_x = max(x1, x2)
    min_y = min(y1, y2)
    max_y = max(y1, y2)
    
    return [(min_x, min_y), (max_x, max_y)]

def is_point_near_line(px, py, x1, y1, x2, y2, threshold=5.0):
    l2 = (x2 - x1)**2 + (y2 - y1)**2
    
    # Handle degenerate case
    if l2 == 0:
        return math.sqrt((px - x1)**2 + (py - y1)**2) <= threshold
    
    t = max(0, min(1, ((px - x1) * (x2 - x1) + (py - y1) * (y2 - y1)) / l2))
    
    proj_x = x1 + t * (x2 - x1)
    proj_y = y1 + t * (y2 - y1)
    
    distance = math.sqrt((px - proj_x)**2 + (py - proj_y)**2)
    
    return distance <= threshold

def is_point_near_rectangle(px, py, corners, threshold=5.0):
    for i in range(4):
        x1, y1 = corners[i]
        x2, y2 = corners[(i+1) % 4]
        if is_point_near_line(px, py, x1, y1, x2, y2, threshold):
            return True
    
    return False

def is_point_near_ellipse(px, py, cx, cy, rx, ry, threshold=5.0):
    # Normalize to unit circle space
    nx = (px - cx) / rx
    ny = (py - cy) / ry
    
    dist_to_unit_circle = abs(math.sqrt(nx*nx + ny*ny) - 1.0)
    
    actual_distance = dist_to_unit_circle * (rx + ry) / 2
    
    return actual_distance <= threshold

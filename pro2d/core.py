#Kelas aplikasi utama untuk grafik 2D.

import sys
import math
import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *

from pro2d.objects import Object2D, Point2D, Line2D, Rectangle2D, Ellipse2D
from pro2d.transform import Transform2D
from pro2d.render import Renderer
from pro2d.clipping import Clipper
from pro2d.utils import screen_to_world, is_point_near_line, is_point_near_rectangle, is_point_near_ellipse

class Graphics2DApp:
    def __init__(self):
        # Initialize Pygame and OpenGL
        pygame.init()
        self.width, self.height = 800, 600
        self.screen = pygame.display.set_mode(
            (self.width, self.height),
            DOUBLEBUF | OPENGL
        )
        pygame.display.set_caption("2D Graphics Application")
        
        # Setup OpenGL
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        self.ortho_bounds = (-400, 400, -300, 300)
        glOrtho(*self.ortho_bounds, -1, 1)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

        self.objects = []
        self.selected_object = None
        self.temp_points = []

        self.current_tool = 'point'  # 'point', 'line', 'rectangle', 'ellipse'
        self.current_color = (1.0, 1.0, 1.0)  # white
        self.current_line_width = 2.0

        self.transform_mode = None  # 'translate', 'rotate', 'scale'
        self.custom_pivot_mode = False
        self.custom_pivot_point = None

        self.window_bounds = [-200, 200, -150, 150]  # left, right, bottom, top
        self.window_active = False
        self.window_definition_mode = False
        self.window_temp_points = []
        self.clipping_enabled = False
    
    def screen_to_world(self, x, y):
        return screen_to_world(x, y, self.width, self.height, self.ortho_bounds)
    
    def handle_mouse_click(self, x, y):
        world_x, world_y = self.screen_to_world(x, y)
        
        if self.custom_pivot_mode:
            self.custom_pivot_point = (world_x, world_y)
            print(f"Custom pivot point set at ({world_x:.1f}, {world_y:.1f})")
            return
            
        if self.window_definition_mode:
            self.window_temp_points.append((world_x, world_y))
            
            if len(self.window_temp_points) == 2:
                x1, y1 = self.window_temp_points[0]
                x2, y2 = self.window_temp_points[1]
                
                self.window_bounds[0] = min(x1, x2)  # left
                self.window_bounds[1] = max(x1, x2)  # right
                self.window_bounds[2] = min(y1, y2)  # bottom
                self.window_bounds[3] = max(y1, y2)  # top
                
                self.window_active = True
                self.clipping_enabled = True
                self.window_definition_mode = False
                self.window_temp_points.clear()
                print(f"Window defined: ({self.window_bounds[0]:.1f}, {self.window_bounds[2]:.1f}) to ({self.window_bounds[1]:.1f}, {self.window_bounds[3]:.1f})")
                print("Clipping automatically enabled. Objects inside window will turn GREEN.")
            return

        if len(self.temp_points) == 0:
            for i in range(len(self.objects) - 1, -1, -1):
                obj = self.objects[i]
                if self.is_point_on_object(world_x, world_y, obj):
                    self.selected_object = obj
                    print(f"Selected {obj.type} object")
                    return

            if self.selected_object is not None:
                self.selected_object = None
                print("Deselected object")

        if self.current_tool == 'point':
            obj = Point2D(world_x, world_y, self.current_color, self.current_line_width)
            self.objects.append(obj)
            self.selected_object = obj
        
        elif self.current_tool in ['line', 'ellipse']:
            self.temp_points.append((world_x, world_y))
            
            if len(self.temp_points) == 2:
                if self.current_tool == 'line':
                    x1, y1 = self.temp_points[0]
                    x2, y2 = self.temp_points[1]
                    obj = Line2D(x1, y1, x2, y2, self.current_color, self.current_line_width)
                
                elif self.current_tool == 'ellipse':
                    x1, y1 = self.temp_points[0]
                    x2, y2 = self.temp_points[1]
                    obj = Ellipse2D(x1, y1, x2, y2, self.current_color, self.current_line_width)
                
                self.objects.append(obj)
                self.selected_object = obj
                self.temp_points.clear()
                
        elif self.current_tool == 'rectangle':
            self.temp_points.append((world_x, world_y))

            if len(self.temp_points) == 1:
                print("Rectangle: Titik pertama ditentukan. Klik untuk titik kedua (sudut berlawanan).")

            if len(self.temp_points) == 2:
                x1, y1 = self.temp_points[0]
                x2, y2 = self.temp_points[1]
                obj = Rectangle2D(x1, y1, x2, y2, self.current_color, self.current_line_width)
                
                self.objects.append(obj)
                self.selected_object = obj
                self.temp_points.clear()
                print("Rectangle: Selesai dibuat dengan 2 titik (sudut berlawanan).")
    
    def is_point_on_object(self, px, py, obj, threshold=5.0):
        if obj.type == 'point' and len(obj.points) > 0:
            x, y = obj.points[0]
            return math.sqrt((px - x)**2 + (py - y)**2) <= max(threshold, obj.line_width)
    
        elif obj.type == 'line' and len(obj.points) >= 2:
            x1, y1 = obj.points[0]
            x2, y2 = obj.points[1]
            return is_point_near_line(px, py, x1, y1, x2, y2, max(threshold, obj.line_width))
    
        elif obj.type == 'rectangle' and len(obj.points) >= 2:
            if obj.corners:
                return is_point_near_rectangle(px, py, obj.corners, max(threshold, obj.line_width))
            else:
                return is_point_near_rectangle(
                    px, py, 
                    [obj.points[0], (obj.points[1][0], obj.points[0][1]), 
                     obj.points[1], (obj.points[0][0], obj.points[1][1])],
                    max(threshold, obj.line_width)
                )
    
        elif obj.type == 'ellipse' and len(obj.points) >= 2:
            if hasattr(obj, 'transformed') and obj.transformed:
                cx, cy = obj.center
                rx, ry = obj.radii
            else:
                x1, y1 = obj.points[0]
                x2, y2 = obj.points[1]
                cx = (x1 + x2) / 2
                cy = (y1 + y2) / 2
                rx = abs(x2 - x1) / 2
                ry = abs(y2 - y1) / 2
            
            return is_point_near_ellipse(px, py, cx, cy, rx, ry, max(threshold, obj.line_width))
    
        return False
    
    def handle_keyboard(self, key):
        if key == pygame.K_1:
            self.current_tool = 'point'
            self.temp_points.clear()
        elif key == pygame.K_2:
            self.current_tool = 'line'
            self.temp_points.clear()
        elif key == pygame.K_3:
            self.current_tool = 'rectangle'
            self.temp_points.clear()
        elif key == pygame.K_4:
            self.current_tool = 'ellipse'
            self.temp_points.clear()
        
        # Color controls
        elif key == pygame.K_r:
            self.current_color = (1.0, 0.0, 0.0)  # red
        elif key == pygame.K_g:
            self.current_color = (0.0, 1.0, 0.0)  # green
        elif key == pygame.K_b:
            self.current_color = (0.0, 0.0, 1.0)  # blue
        elif key == pygame.K_w:
            self.current_color = (1.0, 1.0, 1.0)  # white
        elif key == pygame.K_y:
            self.current_color = (1.0, 1.0, 0.0)  # yellow
        elif key == pygame.K_m:
            self.current_color = (1.0, 0.0, 1.0)  # magenta
        elif key == pygame.K_c and not (pygame.key.get_pressed()[pygame.K_LCTRL] or pygame.key.get_pressed()[pygame.K_RCTRL]):
            self.current_color = (0.0, 1.0, 1.0)  # cyan
        
        # Line width controls
        elif key == pygame.K_PLUS or key == pygame.K_EQUALS:
            self.current_line_width = min(10.0, self.current_line_width + 1.0)
        elif key == pygame.K_MINUS:
            self.current_line_width = max(1.0, self.current_line_width - 1.0)

        elif key == pygame.K_t:
            self.transform_mode = 'translate'
            print("Transform mode: TRANSLATE")
        elif key == pygame.K_o:  # rotate
            self.transform_mode = 'rotate'
            print("Transform mode: ROTATE")
        elif key == pygame.K_s and not (pygame.key.get_pressed()[pygame.K_LCTRL] or pygame.key.get_pressed()[pygame.K_RCTRL]):
            self.transform_mode = 'scale'
            print("Transform mode: SCALE")
        elif key == pygame.K_p:  # Custom pivot mode
            self.custom_pivot_mode = not self.custom_pivot_mode
            
            if self.custom_pivot_mode:
                print("Custom pivot mode: ON - Click anywhere on canvas to set pivot point for rotation and scaling")
                self.custom_pivot_point = None
                self._pivot_message_shown = False
            else:
                print("Custom pivot mode: OFF - Using object centers for rotation and scaling")
                self.custom_pivot_point = None

        elif key == pygame.K_q:
            self.window_definition_mode = True
            self.window_temp_points.clear()
            print("Window definition mode - Click 2 points to define window")
        elif key == pygame.K_w and (pygame.key.get_pressed()[pygame.K_LCTRL] or pygame.key.get_pressed()[pygame.K_RCTRL]):
            self.window_definition_mode = True
            self.window_temp_points.clear()
            print("Window definition mode - Click 2 points to define window")
        elif key == pygame.K_v:
            self.clipping_enabled = not self.clipping_enabled
            status = "ON" if self.clipping_enabled else "OFF"
            print(f"Clipping: {status}")
        elif key == pygame.K_n:
            self.window_active = False
            self.clipping_enabled = False
            self.window_definition_mode = False
            self.window_temp_points.clear()
            print("Window disabled")
        
        # Clear all
        elif key == pygame.K_DELETE or key == pygame.K_BACKSPACE:
            self.objects.clear()
            self.temp_points.clear()
            print("All objects cleared")
        elif key == pygame.K_F1 and self.window_active:
            height = self.window_bounds[3] - self.window_bounds[2]
            self.window_bounds[2] += 20
            self.window_bounds[3] += 20
        elif key == pygame.K_F2 and self.window_active:
            height = self.window_bounds[3] - self.window_bounds[2]
            self.window_bounds[2] -= 20
            self.window_bounds[3] -= 20
        elif key == pygame.K_F3 and self.window_active:
            width = self.window_bounds[1] - self.window_bounds[0]
            self.window_bounds[0] -= 20
            self.window_bounds[1] -= 20
        elif key == pygame.K_F4 and self.window_active:
            width = self.window_bounds[1] - self.window_bounds[0]
            self.window_bounds[0] += 20
            self.window_bounds[1] += 20
        elif key == pygame.K_F5 and self.window_active:
            cx = (self.window_bounds[0] + self.window_bounds[1]) / 2
            cy = (self.window_bounds[2] + self.window_bounds[3]) / 2
            w = (self.window_bounds[1] - self.window_bounds[0]) * 0.9
            h = (self.window_bounds[3] - self.window_bounds[2]) * 0.9
            self.window_bounds[0] = cx - w/2
            self.window_bounds[1] = cx + w/2
            self.window_bounds[2] = cy - h/2
            self.window_bounds[3] = cy + h/2
        elif key == pygame.K_F6 and self.window_active:
            cx = (self.window_bounds[0] + self.window_bounds[1]) / 2
            cy = (self.window_bounds[2] + self.window_bounds[3]) / 2
            w = (self.window_bounds[1] - self.window_bounds[0]) * 1.1
            h = (self.window_bounds[3] - self.window_bounds[2]) * 1.1
            self.window_bounds[0] = cx - w/2
            self.window_bounds[1] = cx + w/2
            self.window_bounds[2] = cy - h/2
            self.window_bounds[3] = cy + h/2

        if self.transform_mode and self.selected_object:
            if key == pygame.K_UP:
                if self.transform_mode == 'translate':
                    Transform2D.translate(self.selected_object, 0, 10)
                elif self.transform_mode == 'scale':
                    if self.custom_pivot_mode and self.custom_pivot_point:
                        pivot_x, pivot_y = self.custom_pivot_point
                        Transform2D.scale(self.selected_object, 1.1, 1.1, pivot_x, pivot_y)
                    else:
                        Transform2D.scale(self.selected_object, 1.1, 1.1)
            elif key == pygame.K_DOWN:
                if self.transform_mode == 'translate':
                    Transform2D.translate(self.selected_object, 0, -10)
                elif self.transform_mode == 'scale':
                    if self.custom_pivot_mode and self.custom_pivot_point:
                        pivot_x, pivot_y = self.custom_pivot_point
                        Transform2D.scale(self.selected_object, 0.9, 0.9, pivot_x, pivot_y)
                    else:
                        Transform2D.scale(self.selected_object, 0.9, 0.9)
            elif key == pygame.K_LEFT:
                if self.transform_mode == 'translate':
                    Transform2D.translate(self.selected_object, -10, 0)
                elif self.transform_mode == 'rotate':
                    if self.custom_pivot_mode and self.custom_pivot_point:
                        pivot_x, pivot_y = self.custom_pivot_point
                        Transform2D.rotate(self.selected_object, -10, pivot_x, pivot_y)
                    else:
                        Transform2D.rotate(self.selected_object, -10)
                elif self.transform_mode == 'scale':
                    if self.custom_pivot_mode and self.custom_pivot_point:
                        pivot_x, pivot_y = self.custom_pivot_point
                        Transform2D.scale(self.selected_object, 0.9, 1.0, pivot_x, pivot_y)
                    else:
                        Transform2D.scale(self.selected_object, 0.9, 1.0)
            elif key == pygame.K_RIGHT:
                if self.transform_mode == 'translate':
                    Transform2D.translate(self.selected_object, 10, 0)
                elif self.transform_mode == 'rotate':
                    if self.custom_pivot_mode and self.custom_pivot_point:
                        pivot_x, pivot_y = self.custom_pivot_point
                        Transform2D.rotate(self.selected_object, 10, pivot_x, pivot_y)
                    else:
                        Transform2D.rotate(self.selected_object, 10)
                elif self.transform_mode == 'scale':
                    if self.custom_pivot_mode and self.custom_pivot_point:
                        pivot_x, pivot_y = self.custom_pivot_point
                        Transform2D.scale(self.selected_object, 1.1, 1.0, pivot_x, pivot_y)
                    else:
                        Transform2D.scale(self.selected_object, 1.1, 1.0)
        elif self.transform_mode and not self.selected_object:
            print("No object selected. Click on an object to select it first.")
    
    def render(self):
        glClear(GL_COLOR_BUFFER_BIT)

        Renderer.draw_axes()

        Renderer.draw_clipping_window(
            self.window_bounds, 
            self.window_active,
            self.window_temp_points, 
            self.window_definition_mode
        )

        for obj in self.objects:
            Renderer.render_object(
                obj, 
                self.window_bounds if self.window_active else None,
                self.clipping_enabled,
                obj == self.selected_object
            )

        if self.custom_pivot_mode and self.custom_pivot_point:
            Renderer.draw_pivot_point(*self.custom_pivot_point)

        if self.temp_points:
            glColor3f(0.5, 0.5, 0.5)  # gray
            for point in self.temp_points:
                Renderer.draw_point(point[0], point[1], (0.5, 0.5, 0.5), 3)

            if len(self.temp_points) > 1:
                if self.current_tool == 'line' and len(self.temp_points) == 2:
                    p1, p2 = self.temp_points
                    Renderer.draw_line(p1[0], p1[1], p2[0], p2[1], (0.5, 0.5, 0.5), 1)
                elif self.current_tool == 'rectangle' and len(self.temp_points) > 1:
                    glColor3f(0.5, 0.5, 0.5)  # gray
                    glLineWidth(1)
                    p1, p2 = self.temp_points

                    Renderer.draw_rectangle([p1, p2], (0.5, 0.5, 0.5), 1)
                    
                    glPointSize(5)
                    glBegin(GL_POINTS)
                    x1, y1 = min(p1[0], p2[0]), min(p1[1], p2[1])
                    x2, y2 = max(p1[0], p2[0]), max(p1[1], p2[1])
                    glVertex2f(x1, y1)
                    glVertex2f(x2, y1)
                    glVertex2f(x2, y2)
                    glVertex2f(x1, y2)
                    glEnd()
                elif self.current_tool == 'ellipse' and len(self.temp_points) == 2:
                    p1, p2 = self.temp_points
                    cx = (p1[0] + p2[0]) / 2
                    cy = (p1[1] + p2[1]) / 2
                    rx = abs(p2[0] - p1[0]) / 2
                    ry = abs(p2[1] - p1[1]) / 2
                    Renderer.draw_ellipse(cx, cy, rx, ry, (0.5, 0.5, 0.5), 1)
        pygame.display.flip()
    
    def get_color_name(self):
        color_map = {
            (1.0, 0.0, 0.0): "RED",
            (0.0, 1.0, 0.0): "GREEN", 
            (0.0, 0.0, 1.0): "BLUE",
            (1.0, 1.0, 1.0): "WHITE",
            (1.0, 1.0, 0.0): "YELLOW",
            (1.0, 0.0, 1.0): "MAGENTA",
            (0.0, 1.0, 1.0): "CYAN"
        }
        return color_map.get(self.current_color, "CUSTOM")
    
    def print_controls(self):
        print("=" * 60)
        print("TUGAS UAS GRAFIKA KOMPUTER - OBJEK 2D INTERAKTIF")
        print("=" * 60)
        print("ALAT GAMBAR:")
        print("  1 - Titik (Point) - 1 klik")
        print("  2 - Garis (Line) - 2 klik (awal dan akhir)")
        print("  3 - Persegi (Rectangle) - 2 klik (sudut kiri atas dan kanan bawah)")
        print("  4 - Ellipse - 2 klik (sudut kiri atas dan kanan bawah)")
        print()
        print("WARNA:")
        print("  R - Merah (Red)")
        print("  G - Hijau (Green)") 
        print("  B - Biru (Blue)")
        print("  W - Putih (White)")
        print("  Y - Kuning (Yellow)")
        print("  M - Magenta")
        print("  C - Cyan")
        print()
        print("KETEBALAN GARIS:")
        print("  + - Tambah ketebalan")
        print("  - - Kurangi ketebalan")
        print()
        print("TRANSFORMASI GEOMETRI:")
        print("  T - Mode translasi")
        print("  O - Mode rotasi")
        print("  S - Mode scaling")
        print("  P - Toggle mode pivot kustom (untuk rotasi dan scaling)")
        print("  KLIK pada objek untuk memilih objek yang akan ditransformasi")
        print("  Saat mode pivot kustom aktif, KLIK di mana saja pada canvas untuk menetapkan titik pivot")
        print("  Arrow Keys untuk mode translasi: Atas/Bawah/Kiri/Kanan")
        print("  Arrow Keys untuk mode rotasi: Kiri  / Kanan ")
        print("  Arrow Keys untuk mode scaling: Atas (membesar), Bawah (mengecil),")
        print("                             Kiri (mengecil horizontal), Kanan (membesar horizontal)")
        print()
        print(" WINDOWING & CLIPPING (FITUR UTAMA)")
        print("  Q - Definisikan window (klik 2 titik) ")
        print("  Ctrl+W - Definisikan window (alternatif)")
        print("  V - Toggle clipping ON/OFF")
        print("  N - Nonaktifkan window")
        print("  F1/F2/F3/F4 - Geser window (atas/bawah/kiri/kanan)")
        print("  F5/F6 - Ubah ukuran window (kecil/besar)")
        print()
        print(" CARA TESTING WINDOWING & CLIPPING ")
        print("1. Tekan Q untuk masuk mode definisi window")
        print("2. Klik 2 titik di canvas untuk menentukan window")
        print("3. Window merah akan muncul dan clipping otomatis aktif")
        print("4. Gambar objek di dalam dan luar window")
        print("5. Objek di DALAM window akan berubah warna HIJAU")
        print("6. Garis yang dipotong window akan menunjukkan efek clipping")
        print()
        print("LAINNYA:")
        print("  Delete/Backspace - Hapus semua objek")
        print("  ESC - Keluar aplikasi")
        print("  Mouse Click - Gambar objek sesuai mode aktif")
        print()
        print("SISTEM KOORDINAT:")
        print("  Sumbu X - Garis horizontal (merah)")
        print("  Sumbu Y - Garis vertikal (biru)")
        print("  Grid - Garis bantuan setiap 50 unit")
        print("  Titik Pusat (0,0) - Titik kuning di tengah canvas")
        print("=" * 60)
    
    def run(self):
        self.print_controls()
        clock = pygame.time.Clock()
        running = True
        
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    elif event.key == pygame.K_w and (event.mod & pygame.KMOD_CTRL):
                        print("Ctrl+W detected!")
                        self.window_definition_mode = True
                        self.window_temp_points.clear()
                        print("Window definition mode - Click 2 points to define window")
                    else:
                        self.handle_keyboard(event.key)
                
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        self.handle_mouse_click(event.pos[0], event.pos[1])
            
            self.render()
            clock.tick(60)
        
        pygame.quit()
        sys.exit()
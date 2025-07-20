import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np
import sys
import math
import os

class Object3D:
    def __init__(self, obj_type, vertices=None, faces=None, position=(0, 0, 0), rotation=(0, 0, 0), scale=(1, 1, 1), color=(1, 1, 1)):
        self.obj_type = obj_type  # 'cube', 'pyramid', 'loaded'
        self.vertices = vertices if vertices else []
        self.faces = faces if faces else []
        self.position = position
        self.rotation = rotation
        self.scale = scale
        self.color = color
        self.display_mode = GL_FILL
        self.visible = True
        self.normals = []
        
    def calculate_normals(self):
        self.normals = []
        for face in self.faces:
            if len(face) >= 3:
                v1 = np.array(self.vertices[face[0]])
                v2 = np.array(self.vertices[face[1]])
                v3 = np.array(self.vertices[face[2]])
                
                # Hitung dua vektor dari tiga titik
                vector1 = v2 - v1
                vector2 = v3 - v1
                
                # Hitung perkalian silang untuk mendapatkan normal
                normal = np.cross(vector1, vector2)
                
                # Normalisasi vektor normal
                norm = np.linalg.norm(normal)
                if norm != 0:
                    normal = normal / norm
                
                self.normals.append(normal)
            else:
                self.normals.append((0, 0, 1))
                
    def load_obj_file(self, file_path):
        # Muat objek dari file .obj
        vertices = []
        faces = []
        
        try:
            with open(file_path, 'r') as f:
                for line in f:
                    if line.startswith('#'):
                        continue
                        
                    values = line.split()
                    if not values:
                        continue
                        
                    if values[0] == 'v':
                        # Posisi vertex
                        vertex = [float(values[1]), float(values[2]), float(values[3])]
                        vertices.append(vertex)
                    elif values[0] == 'f':
                        face = []
                        for v in values[1:]:
                            w = v.split('/')
                            face.append(int(w[0]) - 1)
                        faces.append(face)
            self.vertices = vertices
            self.faces = faces
            self.calculate_normals()
            print(f"Loaded OBJ file: {file_path}")
            print(f"Vertices: {len(self.vertices)}, Faces: {len(self.faces)}")
            return True
        except Exception as e:
            print(f"Error loading OBJ file: {e}")
            return False

class Graphics3DApp:
    def toggle_camera_mode(self):
        # Toggle antara mode manipulasi objek dan kamera
        self.camera_mode = not getattr(self, 'camera_mode', False)
        mode = "KAMERA" if self.camera_mode else "OBJEK"
        self.set_status_message(f"Mode manipulasi: {mode}")
    def scale_current_object(self, factor):
        # Skala objek aktif saat ini dengan faktor (>1: besar, <1: kecil)
        for obj in self.objects:
            if obj.obj_type == self.current_object_type:
                obj.scale = tuple(max(0.05, s * factor) for s in obj.scale)
                self.set_status_message(f"Skala objek: {obj.scale}")
                break
    def draw_pygame_text(self, surface, x, y):
        # Render surface pygame (teks) sebagai tekstur OpenGL di (x, y).
        surface = pygame.transform.flip(surface, False, True)
        text_data = pygame.image.tostring(surface, "RGBA", True)
        width, height = surface.get_size()
        texid = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, texid)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, width, height, 0, GL_RGBA, GL_UNSIGNED_BYTE, text_data)
        glEnable(GL_TEXTURE_2D)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glColor4f(1, 1, 1, 1)
        glBegin(GL_QUADS)
        glTexCoord2f(0, 0); glVertex2f(x, y)
        glTexCoord2f(1, 0); glVertex2f(x + width, y)
        glTexCoord2f(1, 1); glVertex2f(x + width, y + height)
        glTexCoord2f(0, 1); glVertex2f(x, y + height)
        glEnd()
        glDisable(GL_TEXTURE_2D)
        glDisable(GL_BLEND)
        glDeleteTextures([texid])
    def __init__(self):
        self.width = 800
        self.height = 600
        self.objects = []
        self.current_object_type = 'cube'
        self.camera_position = [0, 0, 5]  # x, y, z
        self.camera_rotation = [0, 0, 0]  # pitch, yaw, roll dalam derajat
        self.camera_mode = False  # False: manipulasi objek, True: manipulasi kamera
        self.light_position = (0.0, 10.0, 10.0)  # Posisi sumber cahaya (matahari)
        
        # Variabel pesan status
        self.status_message = "Selamat datang di Aplikasi Grafika 3D"
        self.status_message_time = 0
        self.status_message_duration = 3.0  # untuk durasi pesan status (dalam detik)
        self.show_status = True
        
        # Pengaturan pencahayaan
        self.ambient_enabled = True
        self.ambient_intensity = 0.3
        self.diffuse_enabled = True
        self.diffuse_intensity = 0.7
        self.specular_enabled = True
        self.specular_intensity = 0.5
        self.material_shininess = 50
        self.shading_model = 'phong'
        
        # Interaksi mouse
        self.mouse_dragging = False
        self.last_mouse_pos = (0, 0)
        self.drag_mode = 'rotate'  # 'rotate', 'translate', 'zoom'
        
        # Komponen UI
        self.ui_buttons = []
        self.ui_labels = []
        self.ui_active = False
        
        # Kondisi dialog file
        self.file_dialog_open = False
        self.obj_file_path = None
        
        # Inisialisasi Pygame dan OpenGL
        pygame.init()
        self.screen = pygame.display.set_mode((self.width, self.height), DOUBLEBUF | OPENGL)
        pygame.display.set_caption("Tugas UAS Grafika Komputer - Objek 3D Interactive")
        
        self.setup_opengl()
        self.setup_ui()
        self.create_default_objects()
        
    def setup_opengl(self):
        glViewport(0, 0, self.width, self.height)
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_COLOR_MATERIAL)
        
        # Inisialisasi font pygame untuk rendering teks
        pygame.font.init()
        self.ui_font = pygame.font.SysFont('Arial', 14, bold=True)
        self.status_font = pygame.font.SysFont('Arial', 20, bold=True)
        # Aktifkan pencahayaan
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)

        self.update_lighting()
        self.update_projection()
    
    def update_projection(self):
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(45, (self.width/self.height), 0.1, 50.0)
        
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
    
    # Update posisi dan rotasi kamera
    def update_camera(self):
        glLoadIdentity()
        pitch = math.radians(self.camera_rotation[0])
        yaw = math.radians(self.camera_rotation[1])
        dir_x = math.sin(yaw) * math.cos(pitch)
        dir_y = -math.sin(pitch)
        dir_z = -math.cos(yaw) * math.cos(pitch)
        eye = self.camera_position
        center = [
            eye[0] + dir_x,
            eye[1] + dir_y,
            eye[2] + dir_z
        ]
        up = [0, 1, 0]
        gluLookAt(
            eye[0], eye[1], eye[2],
            center[0], center[1], center[2],
            up[0], up[1], up[2]
        )

    # Update konfigurasi pencahayaan
    def update_lighting(self):
        # Cahaya ambient global
        if self.ambient_enabled:
            ambient = (self.ambient_intensity, self.ambient_intensity, self.ambient_intensity, 1.0)
        else:
            ambient = (0.1, 0.1, 0.1, 1.0)
        glLightModelfv(GL_LIGHT_MODEL_AMBIENT, ambient)
        
        # Posisi cahaya diatur sebelum diffuse dan specular
        light_pos = (*self.light_position, 1.0)
        glLightfv(GL_LIGHT0, GL_POSITION, light_pos)
        
        # Cahaya diffuse
        if self.diffuse_enabled:
            diffuse = (self.diffuse_intensity, self.diffuse_intensity, self.diffuse_intensity, 1.0)
        else:
            diffuse = (0.0, 0.0, 0.0, 1.0)
        glLightfv(GL_LIGHT0, GL_DIFFUSE, diffuse)
        
        # Cahaya specular
        if self.specular_enabled:
            specular = (self.specular_intensity, self.specular_intensity, self.specular_intensity, 1.0)
        else:
            specular = (0.0, 0.0, 0.0, 1.0)
        glLightfv(GL_LIGHT0, GL_SPECULAR, specular)
        
        # Properti material untuk semua objek
        glMaterialfv(GL_FRONT_AND_BACK, GL_AMBIENT, (0.2, 0.2, 0.2, 1.0))
        glMaterialfv(GL_FRONT_AND_BACK, GL_DIFFUSE, (0.8, 0.8, 0.8, 1.0))
        glMaterialfv(GL_FRONT_AND_BACK, GL_SPECULAR, (1.0, 1.0, 1.0, 1.0))
        glMaterialf(GL_FRONT_AND_BACK, GL_SHININESS, self.material_shininess)
        
        # Model shading
        if self.shading_model == 'phong':
            glShadeModel(GL_SMOOTH)
        else:
            glShadeModel(GL_FLAT)
            
        # Aktifkan/nonaktifkan pencahayaan berdasarkan pengaturan
        if self.ambient_enabled or self.diffuse_enabled or self.specular_enabled:
            glEnable(GL_LIGHTING)
            glEnable(GL_LIGHT0)
        else:
            glDisable(GL_LIGHTING)
            glDisable(GL_LIGHT0)

    # Set up user interface
    def setup_ui(self):
        button_width = 120
        button_height = 22
        margin = 7
        status_height = 60
        y_start = status_height + 10
        
        # Tombol objek
        self.ui_buttons.append({
            'label': '1. Kubus', 'x': 10, 'y': y_start, 
            'width': button_width, 'height': button_height,
            'action': lambda: self.set_object_type('cube'),
            'color': (0.2, 0.2, 0.5), 'hover_color': (0.3, 0.3, 0.7)
        })
        
        self.ui_buttons.append({
            'label': '2. Piramida', 'x': 10, 'y': y_start + button_height + margin, 
            'width': button_width, 'height': button_height,
            'action': lambda: self.set_object_type('pyramid'),
            'color': (0.2, 0.2, 0.5), 'hover_color': (0.3, 0.3, 0.7)
        })
        
        self.ui_buttons.append({
            'label': '3. Muat File OBJ', 'x': 10, 'y': y_start + (button_height + margin) * 2, 
            'width': button_width, 'height': button_height,
            'action': self.load_obj_dialog,
            'color': (0.2, 0.2, 0.5), 'hover_color': (0.3, 0.3, 0.7)
        })
        
        # Tombol pencahayaan
        y_light_start = y_start + (button_height + margin) * 3 + margin
        
        self.ui_buttons.append({
            'label': 'A. Ambient Light', 'x': 10, 'y': y_light_start, 
            'width': button_width, 'height': button_height,
            'action': self.toggle_ambient,
            'color': (0.5, 0.2, 0.2), 'hover_color': (0.7, 0.3, 0.3)
        })
        
        self.ui_buttons.append({
            'label': 'D. Diffuse Light', 'x': 10, 'y': y_light_start + button_height + margin, 
            'width': button_width, 'height': button_height,
            'action': self.toggle_diffuse,
            'color': (0.5, 0.2, 0.2), 'hover_color': (0.7, 0.3, 0.3)
        })
        
        self.ui_buttons.append({
            'label': 'S. Specular Light', 'x': 10, 'y': y_light_start + (button_height + margin) * 2, 
            'width': button_width, 'height': button_height,
            'action': self.toggle_specular,
            'color': (0.5, 0.2, 0.2), 'hover_color': (0.7, 0.3, 0.3)
        })
        
        self.ui_buttons.append({
            'label': 'P. Ganti Shading', 'x': 10, 'y': y_light_start + (button_height + margin) * 3, 
            'width': button_width, 'height': button_height,
            'action': self.toggle_shading,
            'color': (0.5, 0.2, 0.2), 'hover_color': (0.7, 0.3, 0.3)
        })
        
        # Tombol mode tampilan
        y_mode_start = y_light_start + (button_height + margin) * 4 + margin
        
        self.ui_buttons.append({
            'label': 'W. Mode Wireframe', 'x': 10, 'y': y_mode_start, 
            'width': button_width, 'height': button_height,
            'action': lambda: self.set_display_mode('wireframe'),
            'color': (0.2, 0.5, 0.2), 'hover_color': (0.3, 0.7, 0.3)
        })
        
        self.ui_buttons.append({
            'label': 'W. Mode Solid', 'x': 10, 'y': y_mode_start + button_height + margin, 
            'width': button_width, 'height': button_height,
            'action': lambda: self.set_display_mode('solid'),
            'color': (0.2, 0.5, 0.2), 'hover_color': (0.3, 0.7, 0.3)
        })
        
        # Tombol kamera
        y_camera_start = y_mode_start + (button_height + margin) * 2 + margin
        
        self.ui_buttons.append({
            'label': 'R. Reset Kamera', 'x': 10, 'y': y_camera_start, 
            'width': button_width, 'height': button_height,
            'action': self.reset_camera,
            'color': (0.5, 0.5, 0.2), 'hover_color': (0.7, 0.7, 0.3)
        })

        # Tombol bantuan
        self.ui_buttons.append({
            'label': 'H. Bantuan', 'x': self.width - button_width - 10, 'y': self.height - button_height - 10, 
            'width': button_width, 'height': button_height,
            'action': self.toggle_help,
            'color': (0.2, 0.5, 0.5), 'hover_color': (0.3, 0.7, 0.7)
        })
        
        # Tombol toggle UI
        self.ui_buttons.append({
            'label': 'U. Tampilkan Menu', 'x': 10, 'y': self.height - button_height - 10, 
            'width': button_width, 'height': button_height,
            'action': self.toggle_ui,
            'color': (0.5, 0.5, 0.5), 'hover_color': (0.7, 0.7, 0.7),
            'always_visible': True
        })

    def create_default_objects(self):
        self.create_cube()
        self.create_pyramid()
    
    def create_cube(self):
        # Definisikan vertex dari unit cube
        vertices = [
            # Face depan
            (-0.5, -0.5, 0.5),  # 0 - depan bawah kiri
            (0.5, -0.5, 0.5),   # 1 - depan bawah kanan
            (0.5, 0.5, 0.5),    # 2 - depan atas kanan
            (-0.5, 0.5, 0.5),   # 3 - depan atas kiri
            
            # Face belakang
            (-0.5, -0.5, -0.5), # 4 - belakang bawah kiri
            (0.5, -0.5, -0.5),  # 5 - belakang bawah kanan 
            (0.5, 0.5, -0.5),   # 6 - belakang atas kanan
            (-0.5, 0.5, -0.5)   # 7 - belakang atas kiri
        ]
        
        # Definisikan face sebagai grup dari 4 vertex
        faces = [
            [0, 1, 2, 3],  # Face depan
            [4, 5, 1, 0],  # Face bawah
            [7, 6, 5, 4],  # Face belakang
            [3, 2, 6, 7],  # Face atas
            [0, 3, 7, 4],  # Face kiri
            [1, 5, 6, 2]   # Face kanan
        ]
        
        cube = Object3D('cube', vertices, faces, (0, 0, 0), (0, 0, 0), (1, 1, 1), (0, 0.5, 1))
        cube.calculate_normals()
        self.objects.append(cube)
    
    def create_pyramid(self):
        # Definisikan vertex dari piramida
        vertices = [
            # Alas
            (-0.5, -0.5, -0.5),  # 0 - bawah kiri
            (0.5, -0.5, -0.5),   # 1 - bawah kanan
            (0.5, -0.5, 0.5),    # 2 - atas kanan
            (-0.5, -0.5, 0.5),   # 3 - atas kiri
            (0, 0.5, 0)          # 4 - puncak
        ]
        
        # Definisikan face - segitiga untuk sisi, quad untuk alas
        faces = [
            [0, 3, 4],      # Face kiri
            [3, 2, 4],      # Face depan
            [2, 1, 4],      # Face kanan
            [1, 0, 4],      # Face belakang
            [0, 1, 2, 3]    # Alas
        ]
        
        pyramid = Object3D('pyramid', vertices, faces, (0, 0.15, 0), (0, 0, 0), (1, 1, 1), (1, 0.5, 0))
        pyramid.calculate_normals()
        self.objects.append(pyramid)
    
    def render_ui(self):
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluOrtho2D(0, self.width, self.height, 0)
        
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        glDisable(GL_DEPTH_TEST)
        glDisable(GL_LIGHTING)

        mouse_pos = pygame.mouse.get_pos()
        for button in self.ui_buttons:
            if button.get('always_visible', False) or self.ui_active:
                hover = (button['x'] <= mouse_pos[0] <= button['x'] + button['width'] and 
                        button['y'] <= mouse_pos[1] <= button['y'] + button['height'])
                color = button['hover_color'] if hover else button['color']
                glBegin(GL_QUADS)
                glColor3f(*color)
                glVertex2f(button['x'], button['y'])
                glVertex2f(button['x'] + button['width'], button['y'])
                glVertex2f(button['x'] + button['width'], button['y'] + button['height'])
                glVertex2f(button['x'], button['y'] + button['height'])
                glEnd()
                glColor4f(1, 1, 1, 1)
                text_surface = self.ui_font.render(button['label'], True, (255, 255, 0))
                text_rect = text_surface.get_rect(center=(button['x'] + button['width']//2, button['y'] + button['height']//2))
                shadow_offset = 1
                shadow_surface = self.ui_font.render(button['label'], True, (0, 0, 0))
                shadow_rect = shadow_surface.get_rect(center=(text_rect.centerx + shadow_offset, text_rect.centery + shadow_offset))
                self.draw_pygame_text(shadow_surface, shadow_rect.left, shadow_rect.top)
                self.draw_pygame_text(text_surface, text_rect.left, text_rect.top)
        glEnable(GL_DEPTH_TEST)
        if self.ambient_enabled or self.diffuse_enabled or self.specular_enabled:
            glEnable(GL_LIGHTING)
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)
        glPopMatrix()
    
    def render_text(self):
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluOrtho2D(0, self.width, self.height, 0)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        
        # Gambar label UI
        glColor3f(1.0, 1.0, 1.0)
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)
        glPopMatrix()
    
    def render_object(self, obj):
        if not obj.visible:
            return
        
        # Terapkan transformasi objek
        glPushMatrix()
        
        # Posisi, rotasi, penskalaan
        glTranslatef(*obj.position)
        glRotatef(obj.rotation[0], 1, 0, 0)
        glRotatef(obj.rotation[1], 0, 1, 0)
        glRotatef(obj.rotation[2], 0, 0, 1)
        glScalef(*obj.scale)
        
        # Atur material color untuk lighting
        if glIsEnabled(GL_LIGHTING):
            ambient_color = tuple(c * 0.3 for c in obj.color) + (1.0,)
            diffuse_color = obj.color + (1.0,)
            specular_color = (1.0, 1.0, 1.0, 1.0)
            
            glMaterialfv(GL_FRONT_AND_BACK, GL_AMBIENT, ambient_color)
            glMaterialfv(GL_FRONT_AND_BACK, GL_DIFFUSE, diffuse_color)
            glMaterialfv(GL_FRONT_AND_BACK, GL_SPECULAR, specular_color)
            glColor3f(*obj.color)
        else:
            glColor3f(*obj.color)
        
        # Gambar setiap face dari objek
        for i, face in enumerate(obj.faces):
            if i < len(obj.normals) and glIsEnabled(GL_LIGHTING):
                glNormal3f(*obj.normals[i])

            if obj.display_mode == GL_LINE_LOOP:
                glDisable(GL_LIGHTING)
                glColor3f(*obj.color)
                glBegin(GL_LINE_LOOP)
                for vertex_idx in face:
                    glVertex3f(*obj.vertices[vertex_idx])
                glEnd()
                if self.ambient_enabled or self.diffuse_enabled or self.specular_enabled:
                    glEnable(GL_LIGHTING)
            else:
                if len(face) == 3:
                    # Segitiga
                    glBegin(GL_TRIANGLES)
                    for vertex_idx in face:
                        if i < len(obj.normals):
                            glNormal3f(*obj.normals[i])
                        glVertex3f(*obj.vertices[vertex_idx])
                    glEnd()
                elif len(face) == 4:
                    glBegin(GL_TRIANGLES)
                    # Segitiga 1: vertex 0,1,2
                    if i < len(obj.normals):
                        glNormal3f(*obj.normals[i])
                    glVertex3f(*obj.vertices[face[0]])
                    glVertex3f(*obj.vertices[face[1]])
                    glVertex3f(*obj.vertices[face[2]])
                    # Segitiga 2: vertex 0,2,3
                    glVertex3f(*obj.vertices[face[0]])
                    glVertex3f(*obj.vertices[face[2]])
                    glVertex3f(*obj.vertices[face[3]])
                    glEnd()
                else:
                    glBegin(GL_POLYGON)
                    for vertex_idx in face:
                        if i < len(obj.normals):
                            glNormal3f(*obj.normals[i])
                        glVertex3f(*obj.vertices[vertex_idx])
                    glEnd()
        
        glPopMatrix()
    
    def render_scene(self):
        # Atur latar belakang abu-abu terang
        glClearColor(0.92, 0.92, 0.92, 1.0)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        # Gambar grid pada bidang XZ
        glDisable(GL_LIGHTING)
        glColor3f(0.8, 0.8, 0.8)
        grid_size = 10
        grid_step = 1
        glLineWidth(1)
        glBegin(GL_LINES)
        for i in range(-grid_size, grid_size + 1):
            # Garis sejajar sumbu X
            glVertex3f(-grid_size, 0, i)
            glVertex3f(grid_size, 0, i)
            # Garis sejajar sumbu Z
            glVertex3f(i, 0, -grid_size)
            glVertex3f(i, 0, grid_size)
        glEnd()

        # Gambar sumbu XYZ
        glLineWidth(2)
        glBegin(GL_LINES)
        # Sumbu X - Merah
        glColor3f(1, 0, 0)
        glVertex3f(0, 0, 0)
        glVertex3f(2, 0, 0)
        # Sumbu Y - Hijau
        glColor3f(0, 1, 0)
        glVertex3f(0, 0, 0)
        glVertex3f(0, 2, 0)
        # Sumbu Z - Biru
        glColor3f(0, 0, 1)
        glVertex3f(0, 0, 0)
        glVertex3f(0, 0, 2)
        glEnd()
        glLineWidth(1)

        # Gambar matahari sebagai bola kuning
        from OpenGL.GLU import gluNewQuadric, gluSphere, gluDeleteQuadric
        glPushMatrix()
        glTranslatef(*self.light_position)
        glColor3f(1.0, 1.0, 0.0)  # Kuning terang
        quad = gluNewQuadric()
        gluSphere(quad, 0.3, 16, 16)
        gluDeleteQuadric(quad)
        glPopMatrix()

        if self.ambient_enabled or self.diffuse_enabled or self.specular_enabled:
            glEnable(GL_LIGHTING)

        # Perbarui view kamera
        self.update_camera()

        # Render semua objek
        for obj in self.objects:
            if obj.obj_type == self.current_object_type or self.current_object_type == 'all':
                self.render_object(obj)

        self.render_ui()
        self.render_text()
        self.render_status_message()

        # Perbarui tampilan
        pygame.display.flip()
    
    # Metode interaksi UI
    def toggle_ui(self):
        self.ui_active = not self.ui_active
        self.set_status_message(f"Menu {'ditampilkan' if self.ui_active else 'disembunyikan'}")
    
    def toggle_help(self):
        controls = [
            "Kontrol Objek 3D:",
            "Mouse Drag: Rotasi objek",
            "Shift+Mouse: Translasi objek",
            "Ctrl+Mouse: Zoom in/out",
            "R: Reset view",
            "1-2: Ganti jenis objek",
            "W: Toggle wireframe/solid",
            "A/D/S: Toggle ambient/diffuse/specular lighting",
            "P: Toggle Phong/Flat shading",
            "ESC: Keluar"
        ]
        help_text = "\n".join(controls)
        print(help_text)
        self.set_status_message("Bantuan: Gunakan Mouse + tombol 1,2,W,A,D,S,P,R,U,H")
    
    def toggle_ambient(self):
        self.ambient_enabled = not self.ambient_enabled
        self.update_lighting()
        self.set_status_message(f"Ambient lighting: {'AKTIF' if self.ambient_enabled else 'NONAKTIF'}")
    
    def toggle_diffuse(self):
        self.diffuse_enabled = not self.diffuse_enabled
        self.update_lighting()
        self.set_status_message(f"Diffuse lighting: {'AKTIF' if self.diffuse_enabled else 'NONAKTIF'}")
    
    def toggle_specular(self):
        self.specular_enabled = not self.specular_enabled
        self.update_lighting()
        self.set_status_message(f"Specular lighting: {'AKTIF' if self.specular_enabled else 'NONAKTIF'}")
    
    def toggle_shading(self):
        self.shading_model = 'flat' if self.shading_model == 'phong' else 'phong'
        self.update_lighting()
        self.set_status_message(f"Model shading: {self.shading_model.upper()}")
    
    def set_object_type(self, obj_type):
        self.current_object_type = obj_type
        self.set_status_message(f"Objek yang dipilih: {obj_type.upper()}")
    
    def set_display_mode(self, mode):
        for obj in self.objects:
            if mode == 'wireframe':
                obj.display_mode = GL_LINE_LOOP
            else:
                obj.display_mode = GL_FILL
        self.set_status_message(f"Mode tampilan: {mode.upper()}")
    
    def reset_camera(self):
        self.camera_position = [0, 0, 5]
        self.camera_rotation = [0, 0, 0]
        self.set_status_message("Kamera dikembalikan ke posisi default")
    
    def load_obj_dialog(self):
        default_obj = 'FinalBaseMesh.obj'
        if os.path.exists(default_obj):
            loaded = self.load_obj_file(default_obj)
            if loaded:
                return
        sample_obj = 'sample.obj'
        if os.path.exists(sample_obj):
            loaded = self.load_obj_file(sample_obj)
            if loaded:
                return
            
        self.set_status_message("File OBJ default tidak ditemukan. Silakan masukkan path ke file OBJ di konsol.")
        print("Please enter the path to an OBJ file (contoh: FinalBaseMesh.obj):")
        self.file_dialog_open = True
    
    def load_obj_file(self, file_path):
        try:
            new_obj = Object3D('loaded')
            success = new_obj.load_obj_file(file_path)
            if success:
                self.objects.append(new_obj)
                self.current_object_type = 'loaded'
                self.set_status_message(f"File OBJ berhasil dimuat: {file_path}")
                return True
        except Exception as e:
            error_msg = f"Error memuat file OBJ: {e}"
            print(error_msg)
            self.set_status_message(error_msg)
        return False
    
    # Penanganan input
    def handle_key_event(self, event):
        if event.key == pygame.K_ESCAPE:
            return False

        elif event.key == pygame.K_r:
            self.reset_camera()

        elif event.key == pygame.K_1:
            self.set_object_type('cube')

        elif event.key == pygame.K_2:
            self.set_object_type('pyramid')

        elif event.key == pygame.K_3:
            if any(obj.obj_type == 'loaded' for obj in self.objects):
                self.set_object_type('loaded')
            else:
                self.load_obj_dialog()

        elif event.key == pygame.K_w:
            for obj in self.objects:
                obj.display_mode = GL_FILL if obj.display_mode == GL_LINE_LOOP else GL_LINE_LOOP
            mode = "SOLID" if self.objects[0].display_mode == GL_FILL else "WIREFRAME"
            self.set_status_message(f"Mode tampilan: {mode}")

        elif event.key == pygame.K_a:
            self.toggle_ambient()

        elif event.key == pygame.K_d:
            self.toggle_diffuse()

        elif event.key == pygame.K_s:
            self.toggle_specular()

        elif event.key == pygame.K_p:
            self.toggle_shading()

        elif event.key == pygame.K_h:
            self.toggle_help()

        elif event.key == pygame.K_u:
            self.toggle_ui()

        elif event.key == pygame.K_TAB:
            self.toggle_camera_mode()

        elif event.key in (pygame.K_PLUS, pygame.K_EQUALS):  # + untuk membesar
            self.scale_current_object(1.1)
        elif event.key == pygame.K_MINUS:  # - untuk mengecil
            self.scale_current_object(0.9)

        elif event.key in (pygame.K_LEFT, pygame.K_RIGHT, pygame.K_UP, pygame.K_DOWN):
            obj = None
            for o in self.objects:
                if o.obj_type == self.current_object_type:
                    obj = o
                    break
            if obj is not None:
                px, py, pz = obj.position
                move_step = 0.2
                if event.key == pygame.K_LEFT:
                    px -= move_step
                elif event.key == pygame.K_RIGHT:
                    px += move_step
                elif event.key == pygame.K_UP:
                    py += move_step
                elif event.key == pygame.K_DOWN:
                    py -= move_step
                obj.position = (px, py, pz)
                self.set_status_message(f"Posisi objek: {obj.position}")

        return True 
    
    def handle_mouse_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # Klik kiri
            # Cek klik tombol UI ketika UI aktif
            if self.ui_active or any(button.get('always_visible', False) for button in self.ui_buttons):
                mouse_pos = pygame.mouse.get_pos()
                for button in self.ui_buttons:
                    if (button.get('always_visible', False) or self.ui_active) and \
                       button['x'] <= mouse_pos[0] <= button['x'] + button['width'] and \
                       button['y'] <= mouse_pos[1] <= button['y'] + button['height']:
                        button['action']()
                        return
            self.mouse_dragging = True
            self.last_mouse_pos = pygame.mouse.get_pos()
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]:
                self.drag_mode = 'translate'  # Geser kamera (pan) X/Y
            elif keys[pygame.K_LCTRL] or keys[pygame.K_RCTRL]:
                self.drag_mode = 'zoom'       # Zoom kamera (Z)
            else:
                self.drag_mode = 'rotate'     # Orbit kamera (yaw/pitch)
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.mouse_dragging = False
        elif event.type == pygame.MOUSEMOTION and self.mouse_dragging:
            current_pos = pygame.mouse.get_pos()
            dx = current_pos[0] - self.last_mouse_pos[0]
            dy = current_pos[1] - self.last_mouse_pos[1]
            self.last_mouse_pos = current_pos
            if getattr(self, 'camera_mode', False):
                if self.drag_mode == 'rotate':
                    # Orbit kamera (yaw/pitch)
                    self.camera_rotation[1] += dx * 0.5
                    self.camera_rotation[0] += dy * 0.5
                elif self.drag_mode == 'translate':
                    # Geser kamera (pan) X/Y (drag ke atas: kamera naik)
                    self.camera_position[0] -= dx * 0.01
                    self.camera_position[1] += dy * 0.01
                elif self.drag_mode == 'zoom':
                    # Zoom kamera (Z)
                    self.camera_position[2] += dy * 0.05
            else:
                # Mode manipulasi objek
                obj = None
                for o in self.objects:
                    if o.obj_type == self.current_object_type:
                        obj = o
                        break
                if obj is not None:
                    if self.drag_mode == 'rotate':
                        rx, ry, rz = obj.rotation
                        ry += dx * 0.5
                        rx += dy * 0.5
                        obj.rotation = (rx, ry, rz)
                    elif self.drag_mode == 'translate':
                        px, py, pz = obj.position
                        px += dx * 0.01
                        py -= dy * 0.01
                        obj.position = (px, py, pz)
                    elif self.drag_mode == 'zoom':
                        px, py, pz = obj.position
                        pz += dy * 0.05
                        obj.position = (px, py, pz)
    
    def print_controls(self):
        print("=" * 60)
        print("TUGAS UAS GRAFIKA KOMPUTER - OBJEK 3D INTERAKTIF")
        print("=" * 60)
        print("KONTROL MOUSE:")
        print("  Left Drag: Rotasi objek/kamera")
        print("  Shift+Left Drag: Translasi objek/kamera")
        print("  Ctrl+Left Drag: Zoom in/out")
        print()
        print("KONTROL KEYBOARD:")
        print("  1: Tampilkan Kubus")
        print("  2: Tampilkan Piramida")
        print("  3: Muat file OBJ")
        print("  W: Toggle wireframe/solid")
        print("  A: Toggle ambient lighting")
        print("  D: Toggle diffuse lighting")
        print("  S: Toggle specular lighting")
        print("  P: Toggle Phong/Flat shading")
        print("  R: Reset posisi kamera")
        print("  U: Toggle UI")
        print("  H: Tampilkan bantuan")
        print("  ESC: Keluar")
        print()
        print("ANTARMUKA:")
        print("  Gunakan tombol di layar untuk kontrol tambahan")
        print("=" * 60)
    
    def set_status_message(self, message):
        self.status_message = message
        self.status_message_time = pygame.time.get_ticks() / 1000.0
        self.status_message_duration = 7.0
        self.show_status = True
        print(message)
    
    def render_status_message(self):
        """Render pesan status di bagian atas layar"""
        if not self.show_status:
            return

        current_time = pygame.time.get_ticks() / 1000.0
        if current_time - self.status_message_time > self.status_message_duration:
            return
        
        # Simpan matriks
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluOrtho2D(0, self.width, self.height, 0)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

        glDisable(GL_DEPTH_TEST)
        glDisable(GL_LIGHTING)

        glColor4f(0.0, 0.0, 0.0, 0.95)
        status_height = 60
        glBegin(GL_QUADS)
        glVertex2f(0, 0)
        glVertex2f(self.width, 0)
        glVertex2f(self.width, status_height)
        glVertex2f(0, status_height)
        glEnd()

        glColor4f(1.0, 1.0, 0.0, 0.9)
        glLineWidth(2.0)
        glBegin(GL_LINES)
        glVertex2f(0, status_height)
        glVertex2f(self.width, status_height)
        glEnd()
        glLineWidth(1.0)

        shadow_offset = 2
        shadow_surface = self.status_font.render(self.status_message, True, (0, 0, 0))
        text_surface = self.status_font.render(self.status_message, True, (255, 255, 0))
        text_rect = text_surface.get_rect(center=(self.width//2, status_height//2))
        shadow_rect = shadow_surface.get_rect(center=(text_rect.centerx + shadow_offset, text_rect.centery + shadow_offset))

        self.draw_pygame_text(shadow_surface, shadow_rect.left, shadow_rect.top)
        self.draw_pygame_text(text_surface, text_rect.left, text_rect.top)

        glEnable(GL_DEPTH_TEST)
        if self.ambient_enabled or self.diffuse_enabled or self.specular_enabled:
            glEnable(GL_LIGHTING)

        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)
        glPopMatrix()
    
    def run(self):
        self.print_controls()
        clock = pygame.time.Clock()
        running = True
        
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                
                elif event.type == pygame.KEYDOWN:
                    running = self.handle_key_event(event)
                
                elif event.type in (pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP, pygame.MOUSEMOTION):
                    self.handle_mouse_event(event)

            self.render_scene()

            clock.tick(60)
        
        pygame.quit()
        sys.exit()

def main():
    app = Graphics3DApp()
    app.run()

if __name__ == "__main__":
    main()
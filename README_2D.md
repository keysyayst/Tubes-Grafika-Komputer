# Tugas Besar UAS Grafika Komputer

## Pengembangan Aplikasi Grafika 2D dan 3D Interaktif Menggunakan PyOpenGL

### Modul A: Objek 2D

##  Implementasi Lengkap Sesuai Kriteria Tugas

### A. Fungsi Penggambaran Objek

1. **Gambar Objek Dasar:**

   - **Titik (Point)** - Tombol `1`
   - **Garis (Line)** - Tombol `2`
   - **Persegi (Rectangle)** - Tombol `3`
   - **Ellipse** - Tombol `4`

2. **Koordinat Input:**
   - **Input dilakukan dengan klik mouse pada canvas OpenGL**
   - Konversi otomatis dari screen coordinates ke world coordinates
   - **Titik**: klik 1 titik
   - **Garis**: klik 2 titik (awal dan akhir)
   - **Persegi**: klik 4 titik (keempat sudut)
   - **Ellipse**: klik 2 titik untuk menentukan area

### B. Fungsi Warna & Ketebalan

3. **Pengguna dapat memilih:**
   - **Warna objek** melalui tombol keyboard:
     - `R` = Merah, `G` = Hijau, `B` = Biru, `W` = Putih, `Y` = Kuning, `M` = Magenta, `C` = Cyan
   - **Ketebalan garis** menggunakan `+/-` (implementasi GL_LINES dan GL_LINE_LOOP)

### C. Transformasi Geometri

4. **Objek yang telah digambar dapat ditransformasi:**

   - **Translasi** - Mode `T` + Arrow Keys
   - **Rotasi** - Mode `O` + Left/Right Arrow
   - **Scaling** - Mode `S` + Up/Down Arrow
   - **Pemilihan Objek** - Klik pada objek untuk memilih objek yang akan ditransformasi
   - **Custom Pivot** - Mode `P` untuk mengaktifkan/menonaktifkan mode pivot kustom, lalu klik pada canvas untuk menetapkan titik pivot untuk rotasi dan scaling

5. **Transformasi dilakukan melalui:**
   - **Keyboard** dengan shortcut keys
   - **Mouse** untuk pemilihan objek
   - **Tombol menu** dan **shortcut** tersedia

### D. Windowing dan Clipping

6. **Pengguna dapat menentukan window aktif:**

   - **Klik 2 titik sebagai batas window** (`Q atau Ctrl+W` lalu klik 2 titik)
   - Window ditampilkan sebagai kotak merah

7. **Objek yang:**

   - **Masuk ke window: BERUBAH WARNA MENJADI HIJAU**
   - **Di luar window: dikenai clipping** menggunakan algoritma:
     - **Cohen-Sutherland** untuk line clipping
     - **Liang-Barsky** untuk line clipping (alternatif)

8. **Window dapat digeser atau diubah ukurannya:**
   - **F1/F2/F3/F4** - Geser window (atas/bawah/kiri/kanan)
   - **F5/F6** - Ubah ukuran window (kecil/besar)

## Kontrol Aplikasi Lengkap

### 🎨 Alat Gambar:

- **1** - Mode Titik (Point)
- **2** - Mode Garis (Line)
- **3** - Mode Persegi (Rectangle)
- **4** - Mode Ellipse

### 🌈 Warna:

- **R** - Merah (Red)
- **G** - Hijau (Green)
- **B** - Biru (Blue)
- **W** - Putih (White)
- **Y** - Kuning (Yellow)
- **M** - Magenta
- **C** - Cyan

### 📏 Ketebalan Garis:

- **+** - Tambah ketebalan
- **-** - Kurangi ketebalan

### 🔄 Transformasi Geometri:

- **T** - Mode translasi
- **O** - Mode rotasi
- **S** - Mode scaling
- **Klik pada objek** - Pilih objek untuk ditransformasi
- **Arrow Keys** - Aplikasikan transformasi pada objek yang dipilih

### 🖼️ Windowing & Clipping:

- **Ctrl+W** - Definisikan window (klik 2 titik)
- **V** - Toggle clipping ON/OFF
- **N** - Nonaktifkan window
- **F1/F2/F3/F4** - Geser window (atas/bawah/kiri/kanan)
- **F5/F6** - Ubah ukuran window (kecil/besar)

### 🛠️ Lainnya:

- **Delete/Backspace** - Hapus semua objek
- **ESC** - Keluar aplikasi
- **Mouse Click** - Gambar objek sesuai mode aktif

## Fitur Khusus yang Memenuhi Kriteria

1. **🎯 Objek di dalam window berubah warna HIJAU**
2. **✂️ Clipping menggunakan algoritma Cohen-Sutherland & Liang-Barsky**
3. **📐 Window dapat digeser dan diubah ukuran secara real-time**
4. **🖱️ Definisi window melalui 2 klik mouse**
5. **⌨️ Kontrol lengkap melalui keyboard dan mouse**

## Cara Menjalankan

1. **Install dependencies:**
2. **Jalankan aplikasi:**
3. **Ikuti instruksi di terminal untuk kontrol lengkap**

## Teknologi yang Digunakan

- **Python 3.13+**
- **PyOpenGL** - untuk rendering grafik OpenGL
- **Pygame** - untuk window management dan event handling
- **OpenGL 2.1** - untuk primitive drawing dan transformasi

## Algoritma yang Diimplementasikan

1. **Cohen-Sutherland Line Clipping** - untuk clipping garis pada window
2. **Liang-Barsky Line Clipping** - algoritma alternatif untuk clipping
3. **Transformasi Matrix 2D** - untuk translasi, rotasi, dan scaling
4. **Point-in-Rectangle Test** - untuk deteksi objek di dalam window

## Struktur Kode

- `Object2D` class - representasi objek 2D dengan properties
- `Graphics2DApp` class - main application dengan semua fitur
- Event handling untuk mouse dan keyboard yang responsif
- Real-time rendering dengan OpenGL
- Coordinate system conversion yang akurat

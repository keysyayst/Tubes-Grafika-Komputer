# README 3D - Aplikasi Visualisasi dan Manipulasi Objek 3D

## Tugas UAS Grafika Komputer - Modul 3D Interaktif

Aplikasi ini dibuat untuk memenuhi seluruh kriteria tugas UAS Modul B (3D) dengan fitur visualisasi, transformasi, pencahayaan, serta kontrol kamera dan objek secara interaktif menggunakan PyOpenGL dan pygame.

---

## Fitur Utama

- Visualisasi objek 3D: Kubus, Piramida, dan file OBJ eksternal
- Transformasi objek: Translasi, rotasi, scaling
- Pencahayaan: Ambient, diffuse, specular, shading Phong/Flat
- Visualisasi sumber cahaya ("matahari")
- Kontrol kamera: Orbit, pan, zoom, reset
- Kontrol objek: Rotasi, translasi, scaling
- UI interaktif (tombol di layar)

---

## Kontrol Kamera (Mode Kamera)

> Tekan `TAB` untuk masuk/keluar mode kamera

| Kontrol           | Aksi Kamera        | Penjelasan                       |
| ----------------- | ------------------ | -------------------------------- |
| Left Drag         | Rotasi (Yaw/Pitch) | Orbit kamera mengelilingi objek  |
| Shift + Left Drag | Translasi (X, Y)   | Geser tampilan (pan) X/Y         |
| Ctrl + Left Drag  | Zoom (Z)           | Zoom in/out (maju/mundur)        |
| R                 | Reset Kamera       | Kembalikan kamera ke posisi awal |

- Drag ke atas: kamera naik (Y+), drag ke bawah: kamera turun (Y-)
- Drag ke kanan/kiri: kamera geser kanan/kiri (X)
- Zoom: drag ke atas = mendekat, ke bawah = menjauh

---

## Kontrol Objek (Mode Objek)

> Tekan `TAB` untuk kembali ke mode objek

| Kontrol           | Aksi Objek             | Penjelasan                  |
| ----------------- | ---------------------- | --------------------------- |
| Left Drag         | Rotasi objek           | Putar objek pada sumbu X/Y  |
| Shift + Left Drag | Translasi objek (X, Y) | Geser objek pada bidang X/Y |
| Ctrl + Left Drag  | Zoom objek (Z)         | Geser objek pada sumbu Z    |
| Panah (←↑↓→)      | Translasi objek        | Geser objek pada X/Y        |
| + / -             | Scaling objek          | Perbesar/perkecil objek     |

---

## Kontrol Umum & UI

| Tombol | Fungsi                                   |
| ------ | ---------------------------------------- |
| 1      | Tampilkan kubus                          |
| 2      | Tampilkan piramida                       |
| 3      | Muat file OBJ eksternal                  |
| W      | Toggle wireframe/solid                   |
| A/D/S  | Toggle ambient/diffuse/specular lighting |
| P      | Toggle shading Phong/Flat                |
| U      | Tampilkan/sembunyikan menu UI            |
| H      | Tampilkan bantuan di status bar          |
| ESC    | Keluar aplikasi                          |

---

## Petunjuk Penggunaan

1. Jalankan aplikasi: `python Objek3d.py`
2. Gunakan mouse dan keyboard sesuai tabel di atas.
3. Tekan `TAB` untuk berpindah antara mode kamera dan objek.
4. Gunakan tombol UI di layar untuk akses cepat fitur.
5. Untuk memuat file OBJ, tekan `3` atau tombol "Muat File OBJ" di UI.

---

## Catatan Teknis

- Semua kontrol kamera dan objek sudah mengikuti standar aplikasi 3D modern.
- Mouse wheel tidak digunakan.
- Sumber cahaya divisualisasikan sebagai bola kuning ("matahari").
- Status dan instruksi akan muncul di status bar bagian atas aplikasi.

# I Don't Think It's Reliable — Noisy Mask Cleaning

## Overview
Program ini membersihkan noise pada video mask biner secara dinamis untuk setiap frame. Piksel putih dianggap foreground/objek, sedangkan piksel hitam dianggap background.

## Metode
1. Membaca frame video menggunakan OpenCV.
2. Mengubah frame ke grayscale.
3. Melakukan threshold untuk memisahkan foreground putih dan background hitam.
4. Menggunakan Connected Component Analysis untuk menemukan komponen foreground yang saling terhubung.
5. Mempertahankan komponen foreground terbesar sebagai objek dan menghapus komponen lainnya sebagai noise.
6. Menggunakan operasi morfologi kecil (closing dan opening) untuk merapikan tepi mask.
7. Menyimpan mask bersih sebagai video dan statistik per frame sebagai CSV.

Metode bekerja berdasarkan isi piksel setiap frame. Tidak ada koordinat objek, nomor frame, atau waktu kemunculan yang di-hardcode.

## Requirements
- Python 3
- OpenCV
- NumPy

Install:
```bash
pip install opencv-python numpy
```

## Cara menjalankan
Letakkan `noisy_mask.mp4` dan `i_dont_think_its_reliable.py` di folder yang sama, lalu jalankan:

```bash
python3 i_dont_think_its_reliable.py
```

Output default:
- `cleaned_mask.mp4` — video mask setelah noise dibersihkan.
- `mask_statistics.csv` — statistik setiap frame.

Untuk menampilkan hasil selama pemrosesan:
```bash
python3 i_dont_think_its_reliable.py --show
```
Tekan `q` untuk menutup jendela tampilan.

Parameter dapat diubah:
```bash
python3 i_dont_think_its_reliable.py --input noisy_mask.mp4 --output cleaned_mask.mp4 --threshold 127
```

## Statistik
CSV berisi:
- `frame`: indeks frame.
- `object_pixels`: jumlah piksel komponen objek terbesar sebelum operasi morfologi.
- `removed_noise_pixels`: jumlah piksel foreground di luar komponen terbesar.
- `foreground_components`: jumlah komponen foreground yang terdeteksi.
- `object_percentage`: persentase area frame yang ditempati komponen objek terbesar.

## Catatan
Metode ini sesuai untuk video mask yang memiliki satu objek utama dan noise berupa komponen foreground kecil/terpisah. Jika terdapat beberapa objek utama yang saling terpisah, asumsi satu komponen terbesar perlu disesuaikan. Threshold default 127 cocok untuk video mask hitam-putih ini dan dapat diubah melalui argumen `--threshold`.

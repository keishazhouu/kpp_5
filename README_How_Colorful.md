# How Colorful?

Program Python untuk mendeteksi kelompok warna pada setiap frame video dan
melakukan segmentasi terhadap kelompok warna dengan jumlah piksel terbanyak.

## Metode
1. Membaca video frame demi frame menggunakan OpenCV.
2. Mengelompokkan warna dengan kuantisasi kanal BGR (`step=16`) agar variasi kecil
   akibat kompresi dan anti-aliasing tidak dianggap sebagai warna yang sepenuhnya berbeda.
3. Menghitung histogram warna menggunakan `numpy.bincount`. Perhitungan dilakukan
   berdasarkan jumlah piksel, bukan jumlah region.
4. Memilih bin warna dengan jumlah piksel terbanyak pada frame saat itu.
5. Membuat mask untuk seluruh piksel yang termasuk bin dominan dan menyorotnya
   pada frame output.
6. Menyimpan statistik semua bin warna per frame ke file CSV.

## Instalasi
```bash
python3 -m venv venv
source venv/bin/activate
pip install opencv-python numpy
```

## Menjalankan
Letakkan file video di folder yang sama dengan script, lalu jalankan:
```bash
python3 how_colorful.py --input "Lucky Charms Diamond Dancers.mp4"
```

File output:
- `how_colorful_segmented.mp4`
- `color_statistics.csv`

Untuk menampilkan proses pada jendela video:
```bash
python3 how_colorful.py --input "Lucky Charms Diamond Dancers.mp4" --show
```

Nilai kuantisasi dapat diubah, misalnya `--step 8` untuk pengelompokan warna yang
lebih detail atau `--step 24` untuk pengelompokan yang lebih kasar.

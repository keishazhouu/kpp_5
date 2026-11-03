# Where Are The Shapes? — ROS Noetic

Deteksi real-time lima bentuk geometri menggunakan Python, OpenCV, dan ROS Noetic.
Metode utama: segmentasi foreground berbasis HSV, contour detection, polygon
approximation, circularity, dan aspect ratio. Tidak menggunakan posisi, urutan,
nomor frame, atau timing objek sebagai acuan klasifikasi.

## Struktur
- `scripts/video_publisher.py`: membaca video dengan `cv2.VideoCapture()` lalu
  mengirim frame sebagai `sensor_msgs/Image`.
- `scripts/shape_detector.py`: menerima frame, memprosesnya, mengklasifikasikan
  bentuk, dan menampilkan hasil.
- `launch/shape_detection.launch`: menjalankan kedua node.

## Dependensi
- ROS Noetic
- Python 3
- `rospy`, `sensor_msgs`, `cv_bridge`
- OpenCV (`cv2`) dan NumPy pada environment Python yang digunakan ROS.

## Instalasi
Salin folder `where_are_the_shapes` ke `~/catkin_ws/src/`, lalu:

```bash
cd ~/catkin_ws
catkin_make
source devel/setup.bash
chmod +x src/where_are_the_shapes/scripts/*.py
```

Pastikan OpenCV dan NumPy dapat di-import dari Python yang dipakai oleh ROS Noetic.

## Menjalankan
Terminal 1:
```bash
roscore
```

Terminal 2 (ganti path sesuai lokasi video):
```bash
source ~/catkin_ws/devel/setup.bash
roslaunch where_are_the_shapes shape_detection.launch video:=/path/ke/shape_detection_static.mp4
```

Untuk video transisi:
```bash
roslaunch where_are_the_shapes shape_detection.launch video:=/path/ke/shape_detection_transition.mp4
```

Untuk mengulang video:
```bash
roslaunch where_are_the_shapes shape_detection.launch video:=/path/ke/video.mp4 loop:=true
```

## Parameter yang dapat disesuaikan
- `min_area`: mengabaikan contour kecil/noise.
- `max_saturation`: batas saturasi HSV foreground abu-abu.
- `min_value`: batas kecerahan foreground.
- `approx_factor`: tingkat penyederhanaan contour.
- `output_width`: lebar frame yang dipublikasikan.
- `loop`: mengulang video setelah selesai.

## Catatan metode
Background video sintetis memiliki saturasi tinggi, sedangkan objek berbentuk abu-abu
memiliki saturasi rendah. Mask HSV memisahkan keduanya tanpa mengunci warna background
tertentu. Jumlah vertex hasil `approxPolyDP` dipakai untuk polygon; lingkaran dikenali
dengan circularity. Square juga diperiksa rasio bounding box-nya.

Parameter merupakan titik awal dan perlu diuji kembali pada seluruh video serta
kondisi runtime ROS. Video demonstrasi dan hasil pengujian perlu direkam sendiri.

## Integritas akademik
Implementasi proyek ini disusun khusus untuk tugas ini dengan memanfaatkan API
library OpenCV dan ROS. Jika kemudian mengambil kode, dataset, atau referensi
eksternal lain, tambahkan kredit/sitasi pada bagian ini.

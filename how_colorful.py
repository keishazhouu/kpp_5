import cv2
import numpy as np
import csv
import argparse
import time

def process_video(input_path, output_path, csv_path, step=16, show=False):
    if step < 1 or step > 256:
        raise ValueError("step harus berada di antara 1 dan 256.")

    cap = cv2.VideoCapture(input_path)
    if not cap.isOpened():
        raise RuntimeError(f"Tidak bisa membuka video: {input_path}")

    fps = cap.get(cv2.CAP_PROP_FPS) or 24.0
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    writer = cv2.VideoWriter(
        output_path, cv2.VideoWriter_fourcc(*"mp4v"), fps, (width, height)
    )
    if not writer.isOpened():
        raise RuntimeError(f"Tidak bisa membuat video output: {output_path}")

    # Jumlah bin per kanal; indeks warna dihitung dari B, G, dan R.
    levels = (256 + step - 1) // step
    frame_index = 0
    start_time = time.time()

    with open(csv_path, "w", newline="", encoding="utf-8") as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow([
            "frame", "time_seconds", "color_bin_bgr",
            "representative_hex", "pixel_count", "percentage",
            "is_most_frequent"
        ])

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            # Kuantisasi warna dinamis pada setiap frame.
            b = frame[:, :, 0].astype(np.int32) // step
            g = frame[:, :, 1].astype(np.int32) // step
            r = frame[:, :, 2].astype(np.int32) // step
            color_ids = (b * levels + g) * levels + r

            # Histogram menghitung jumlah piksel setiap warna/bin.
            counts = np.bincount(color_ids.ravel(), minlength=levels**3)
            present_ids = np.flatnonzero(counts)
            dominant_id = int(present_ids[np.argmax(counts[present_ids])])
            dominant_count = int(counts[dominant_id])

            # Segmentasi hanya pada piksel yang termasuk bin warna dominan.
            mask = color_ids == dominant_id

            output = frame.copy()
            overlay = np.zeros_like(frame)
            overlay[:] = (0, 255, 255)  # highlight kuning (BGR)
            blended = cv2.addWeighted(output, 0.40, overlay, 0.60, 0)
            output[mask] = blended[mask]

            total_pixels = frame.shape[0] * frame.shape[1]
            percentage = 100.0 * dominant_count / total_pixels

            # Ambil titik tengah bin sebagai representasi warna.
            rb = dominant_id % levels
            gb = (dominant_id // levels) % levels
            bb = dominant_id // (levels * levels)
            cb = min(bb * step + step // 2, 255)
            cg = min(gb * step + step // 2, 255)
            cr = min(rb * step + step // 2, 255)
            dominant_hex = f"#{cr:02X}{cg:02X}{cb:02X}"

            cv2.putText(output,
                f"Dominant: {dominant_hex} | {percentage:.1f}% pixels",
                (20, 35), cv2.FONT_HERSHEY_SIMPLEX, 0.8,
                (255, 255, 255), 2, cv2.LINE_AA)
            cv2.putText(output,
                f"Unique color bins: {len(present_ids)} | Frame: {frame_index + 1}/{total_frames}",
                (20, 68), cv2.FONT_HERSHEY_SIMPLEX, 0.65,
                (255, 255, 255), 2, cv2.LINE_AA)

            # Catat semua bin warna yang muncul dan jumlah pikselnya.
            for color_id in present_ids:
                color_id = int(color_id)
                rb = color_id % levels
                gb = (color_id // levels) % levels
                bb = color_id // (levels * levels)
                cb = min(bb * step + step // 2, 255)
                cg = min(gb * step + step // 2, 255)
                cr = min(rb * step + step // 2, 255)
                count = int(counts[color_id])
                csvwriter.writerow([
                    frame_index, f"{frame_index / fps:.4f}",
                    f"({cb},{cg},{cr})", f"#{cr:02X}{cg:02X}{cb:02X}",
                    count, f"{100.0 * count / total_pixels:.6f}",
                    int(color_id == dominant_id)
                ])

            writer.write(output)
            if show:
                cv2.imshow("How Colorful? - Dominant Color Segmentation", output)
                if cv2.waitKey(1) & 0xFF == ord("q"):
                    break
            frame_index += 1

    cap.release()
    writer.release()
    if show:
        cv2.destroyAllWindows()

    elapsed = time.time() - start_time
    print(f"Selesai: {frame_index} frame diproses.")
    print(f"Video hasil: {output_path}")
    print(f"Statistik warna: {csv_path}")
    print(f"Waktu pemrosesan: {elapsed:.2f} detik")
    if elapsed:
        print(f"Kecepatan rata-rata: {frame_index / elapsed:.2f} FPS")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Deteksi warna dan segmentasi warna dominan.")
    parser.add_argument("--input", default="Lucky Charms Diamond Dancers.mp4")
    parser.add_argument("--output", default="how_colorful_segmented.mp4")
    parser.add_argument("--csv", default="color_statistics.csv")
    parser.add_argument("--step", type=int, default=16)
    parser.add_argument("--show", action="store_true")
    args = parser.parse_args()
    process_video(args.input, args.output, args.csv, args.step, args.show)

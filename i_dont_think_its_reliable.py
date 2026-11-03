#!/usr/bin/env python3
"""
I Don't Think It's Reliable
Clean a noisy binary object mask frame-by-frame using image processing.

Method:
1. Convert each frame to grayscale.
2. Threshold it into a binary foreground/background mask.
3. Find connected components.
4. Keep the largest foreground component (the object) and remove the rest as noise.

No frame number, timestamp, or fixed object coordinates are used.
"""
import argparse
import csv
import time
import cv2
import numpy as np


def clean_mask(frame, threshold=127):
    """Return a cleaned binary mask and basic component statistics."""
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # The supplied clip is a bright-object / dark-background mask.
    # Convert the mask to foreground (white) and background (black).
    _, binary = cv2.threshold(gray, threshold, 255, cv2.THRESH_BINARY)

    count, labels, stats, _ = cv2.connectedComponentsWithStats(
        binary, connectivity=8
    )

    if count <= 1:
        return np.zeros_like(binary), 0, 0, 0

    # Background is label 0; select the foreground component with the most pixels.
    component_areas = stats[1:, cv2.CC_STAT_AREA]
    largest_label = 1 + int(np.argmax(component_areas))
    object_pixels = int(stats[largest_label, cv2.CC_STAT_AREA])
    foreground_pixels = int(np.count_nonzero(binary))
    removed_pixels = foreground_pixels - object_pixels

    cleaned = np.zeros_like(binary)
    cleaned[labels == largest_label] = 255

    # A small closing/opening pass smooths tiny boundary irregularities.
    kernel = np.ones((3, 3), np.uint8)
    cleaned = cv2.morphologyEx(cleaned, cv2.MORPH_CLOSE, kernel)
    cleaned = cv2.morphologyEx(cleaned, cv2.MORPH_OPEN, kernel)

    return cleaned, object_pixels, removed_pixels, count - 1


def main():
    parser = argparse.ArgumentParser(
        description="Remove noise from a binary object-mask video."
    )
    parser.add_argument("--input", default="noisy_mask.mp4",
                        help="Input video filename (default: noisy_mask.mp4)")
    parser.add_argument("--output", default="cleaned_mask.mp4",
                        help="Output video filename (default: cleaned_mask.mp4)")
    parser.add_argument("--csv", default="mask_statistics.csv",
                        help="Per-frame statistics CSV filename")
    parser.add_argument("--threshold", type=int, default=127,
                        help="Grayscale threshold from 0 to 255 (default: 127)")
    parser.add_argument("--show", action="store_true",
                        help="Display cleaned frames while processing; press q to stop")
    args = parser.parse_args()

    cap = cv2.VideoCapture(args.input)
    if not cap.isOpened():
        raise SystemExit(
            f"Cannot open '{args.input}'. Put the video in this folder "
            "or pass its path with --input."
        )

    fps = cap.get(cv2.CAP_PROP_FPS)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    if not fps or fps <= 0:
        fps = 24.0

    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    writer = cv2.VideoWriter(args.output, fourcc, fps, (width, height), isColor=False)
    if not writer.isOpened():
        cap.release()
        raise SystemExit("Cannot create output video.")

    frame_index = 0
    start = time.time()
    csv_file = open(args.csv, "w", newline="", encoding="utf-8")
    csv_writer = csv.writer(csv_file)
    csv_writer.writerow([
        "frame", "object_pixels", "removed_noise_pixels",
        "foreground_components", "object_percentage"
    ])

    try:
        while True:
            ok, frame = cap.read()
            if not ok:
                break

            cleaned, object_pixels, removed_pixels, components = clean_mask(
                frame, args.threshold
            )
            writer.write(cleaned)

            total_pixels = width * height
            object_percentage = 100.0 * object_pixels / total_pixels
            csv_writer.writerow([
                frame_index, object_pixels, removed_pixels,
                components, f"{object_percentage:.4f}"
            ])

            if args.show:
                display = cv2.cvtColor(cleaned, cv2.COLOR_GRAY2BGR)
                cv2.putText(
                    display, f"Cleaned mask | Frame: {frame_index}",
                    (15, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7,
                    (0, 255, 0), 2, cv2.LINE_AA
                )
                cv2.imshow("I Don't Think It's Reliable", display)
                if cv2.waitKey(1) & 0xFF == ord("q"):
                    break

            frame_index += 1
    finally:
        cap.release()
        writer.release()
        csv_file.close()
        if args.show:
            cv2.destroyAllWindows()

    elapsed = time.time() - start
    print(f"Selesai: {frame_index} frame diproses.")
    print(f"Video hasil: {args.output}")
    print(f"Statistik: {args.csv}")
    print(f"Waktu pemrosesan: {elapsed:.2f} detik")
    if elapsed > 0:
        print(f"Kecepatan rata-rata: {frame_index / elapsed:.2f} FPS")
    print(f"FPS video sumber: {fps:.2f}")


if __name__ == "__main__":
    main()

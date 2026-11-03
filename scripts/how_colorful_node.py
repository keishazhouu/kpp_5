#!/usr/bin/env python3

import os
import csv
import cv2
import numpy as np
import rospy

from sensor_msgs.msg import Image
from cv_bridge import CvBridge, CvBridgeError


class HowColorfulNode:
    def __init__(self):
        self.bridge = CvBridge()

        self.step = int(rospy.get_param("~step", 16))
        self.image_topic = rospy.get_param(
            "~image_topic", "/camera/image_raw"
        )
        self.output_topic = rospy.get_param(
            "~output_topic", "/how_colorful/segmented_image"
        )
        self.csv_path = rospy.get_param(
            "~csv_path", os.path.expanduser("~/color_statistics.csv")
        )

        if not 1 <= self.step <= 256:
            raise ValueError("step harus berada di antara 1 dan 256.")

        self.levels = (256 + self.step - 1) // self.step
        self.frame_index = 0

        csv_dir = os.path.dirname(os.path.abspath(self.csv_path))
        os.makedirs(csv_dir, exist_ok=True)

        self.csv_file = open(
            self.csv_path, "w", newline="", encoding="utf-8"
        )
        self.csv_writer = csv.writer(self.csv_file)

        self.csv_writer.writerow([
            "frame", "time_seconds", "color_bin_bgr",
            "representative_hex", "pixel_count", "percentage",
            "is_most_frequent"
        ])

        self.publisher = rospy.Publisher(
            self.output_topic, Image, queue_size=1
        )

        self.subscriber = rospy.Subscriber(
            self.image_topic,
            Image,
            self.image_callback,
            queue_size=1,
            buff_size=2**24
        )

        rospy.loginfo("How Colorful Node started.")
        rospy.loginfo("Listening on: %s", self.image_topic)

    def image_callback(self, msg):
        try:
            frame = self.bridge.imgmsg_to_cv2(
                msg, desired_encoding="bgr8"
            )
        except CvBridgeError as error:
            rospy.logerr("cv_bridge error: %s", error)
            return

        step = self.step
        levels = self.levels

        b = frame[:, :, 0].astype(np.int32) // step
        g = frame[:, :, 1].astype(np.int32) // step
        r = frame[:, :, 2].astype(np.int32) // step

        color_ids = (b * levels + g) * levels + r

        counts = np.bincount(
            color_ids.ravel(), minlength=levels**3
        )

        present_ids = np.flatnonzero(counts)

        dominant_id = int(
            present_ids[np.argmax(counts[present_ids])]
        )
        dominant_count = int(counts[dominant_id])

        mask = color_ids == dominant_id

        output = frame.copy()
        overlay = np.zeros_like(frame)
        overlay[:] = (0, 255, 255)

        blended = cv2.addWeighted(
            output, 0.40, overlay, 0.60, 0
        )

        output[mask] = blended[mask]

        total_pixels = frame.shape[0] * frame.shape[1]
        percentage = 100.0 * dominant_count / total_pixels

        rb = dominant_id % levels
        gb = (dominant_id // levels) % levels
        bb = dominant_id // (levels * levels)

        cb = min(bb * step + step // 2, 255)
        cg = min(gb * step + step // 2, 255)
        cr = min(rb * step + step // 2, 255)

        dominant_hex = f"#{cr:02X}{cg:02X}{cb:02X}"

        cv2.putText(
            output,
            f"Dominant: {dominant_hex} | {percentage:.1f}%",
            (20, 35),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (255, 255, 255),
            2
        )

        cv2.putText(
            output,
            f"Unique color bins: {len(present_ids)}",
            (20, 68),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.65,
            (255, 255, 255),
            2
        )

        for color_id in present_ids:
            color_id = int(color_id)

            rb = color_id % levels
            gb = (color_id // levels) % levels
            bb = color_id // (levels * levels)

            cb = min(bb * step + step // 2, 255)
            cg = min(gb * step + step // 2, 255)
            cr = min(rb * step + step // 2, 255)

            count = int(counts[color_id])

            self.csv_writer.writerow([
                self.frame_index,
                f"{self.frame_index / 24.0:.4f}",
                f"({cb},{cg},{cr})",
                f"#{cr:02X}{cg:02X}{cb:02X}",
                count,
                f"{100.0 * count / total_pixels:.6f}",
                int(color_id == dominant_id)
            ])

        self.csv_file.flush()

        output_msg = self.bridge.cv2_to_imgmsg(
            output, encoding="bgr8"
        )
        output_msg.header = msg.header
        self.publisher.publish(output_msg)

        self.frame_index += 1

        rospy.loginfo_throttle(
            3.0,
            "Dominant color: %s (%.1f%%)",
            dominant_hex,
            percentage
        )

    def shutdown(self):
        self.csv_file.close()


if __name__ == "__main__":
    rospy.init_node("how_colorful_node")

    node = HowColorfulNode()
    rospy.on_shutdown(node.shutdown)

    rospy.spin()

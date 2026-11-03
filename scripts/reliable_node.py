#!/usr/bin/env python3

import os
import csv
import cv2
import numpy as np
import rospy

from sensor_msgs.msg import Image
from cv_bridge import CvBridge, CvBridgeError


def clean_mask(frame, threshold=127):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    _, binary = cv2.threshold(
        gray, threshold, 255, cv2.THRESH_BINARY
    )

    count, labels, stats, _ = cv2.connectedComponentsWithStats(
        binary, connectivity=8
    )

    if count <= 1:
        return np.zeros_like(binary), 0, 0, 0

    component_areas = stats[1:, cv2.CC_STAT_AREA]
    largest_label = 1 + int(np.argmax(component_areas))

    object_pixels = int(stats[largest_label, cv2.CC_STAT_AREA])
    foreground_pixels = int(np.count_nonzero(binary))
    removed_pixels = foreground_pixels - object_pixels

    cleaned = np.zeros_like(binary)
    cleaned[labels == largest_label] = 255

    kernel = np.ones((3, 3), np.uint8)
    cleaned = cv2.morphologyEx(
        cleaned, cv2.MORPH_CLOSE, kernel
    )
    cleaned = cv2.morphologyEx(
        cleaned, cv2.MORPH_OPEN, kernel
    )

    return cleaned, object_pixels, removed_pixels, count - 1


class ReliableNode:
    def __init__(self):
        self.bridge = CvBridge()
        self.frame_count = 0

        self.threshold = rospy.get_param("~threshold", 127)
        input_topic = rospy.get_param(
            "~image_topic", "/reliable/image_raw"
        )
        output_topic = rospy.get_param(
            "~output_topic", "/reliable/cleaned_mask"
        )
        csv_path = os.path.expanduser(
            rospy.get_param("~csv_path", "~/mask_statistics.csv")
        )

        self.csv_file = open(csv_path, "w", newline="")
        self.csv_writer = csv.writer(self.csv_file)
        self.csv_writer.writerow([
            "frame",
            "object_pixels",
            "removed_noise_pixels",
            "foreground_components",
            "object_percentage"
        ])

        self.publisher = rospy.Publisher(
            output_topic, Image, queue_size=1
        )
        self.subscriber = rospy.Subscriber(
            input_topic, Image, self.callback, queue_size=1
        )

        rospy.on_shutdown(self.close_csv)
        rospy.loginfo("Reliable node started.")

    def callback(self, msg):
        try:
            frame = self.bridge.imgmsg_to_cv2(
                msg, desired_encoding="bgr8"
            )

            cleaned, object_pixels, removed_pixels, components = (
                clean_mask(frame, self.threshold)
            )

            output_msg = self.bridge.cv2_to_imgmsg(
                cleaned, encoding="mono8"
            )
            output_msg.header = msg.header
            self.publisher.publish(output_msg)

            self.frame_count += 1
            total_pixels = cleaned.size
            percentage = (
                object_pixels / total_pixels * 100
                if total_pixels > 0 else 0
            )

            self.csv_writer.writerow([
                self.frame_count,
                object_pixels,
                removed_pixels,
                components,
                percentage
            ])
            self.csv_file.flush()

        except CvBridgeError as error:
            rospy.logerr("CvBridge error: %s", error)

    def close_csv(self):
        self.csv_file.close()


if __name__ == "__main__":
    rospy.init_node("reliable_node")
    node = ReliableNode()
    rospy.spin()

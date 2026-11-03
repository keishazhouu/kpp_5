#!/usr/bin/env python3

import rospy
import cv2
import numpy as np

from sensor_msgs.msg import Image
from cv_bridge import CvBridge


class LocateItNode:

    def __init__(self):
        rospy.init_node('locate_it_node')

        self.bridge = CvBridge()

        self.threshold = 22
        self.min_area = 12
        self.kernel_size = 7

        self.kernel = cv2.getStructuringElement(
            cv2.MORPH_ELLIPSE,
            (self.kernel_size, self.kernel_size)
        )

        self.publisher = rospy.Publisher(
            '/locate_it/detected_image',
            Image,
            queue_size=10
        )

        self.subscriber = rospy.Subscriber(
            '/camera/image_raw',
            Image,
            self.image_callback
        )

        rospy.loginfo("Locate It Node started.")

    def image_callback(self, msg):

        frame = self.bridge.imgmsg_to_cv2(
            msg,
            desired_encoding='bgr8'
        )

        gray = cv2.cvtColor(
            frame,
            cv2.COLOR_BGR2GRAY
        )

        _, mask = cv2.threshold(
            gray,
            self.threshold,
            255,
            cv2.THRESH_BINARY
        )

        mask = cv2.morphologyEx(
            mask,
            cv2.MORPH_CLOSE,
            self.kernel,
            iterations=2
        )

        contours, _ = cv2.findContours(
            mask,
            cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE
        )

        detected = 0

        for contour in contours:

            if cv2.contourArea(contour) < self.min_area:
                continue

            x, y, w, h = cv2.boundingRect(contour)

            cv2.rectangle(
                frame,
                (x, y),
                (x + w, y + h),
                (0, 255, 0),
                2
            )

            detected += 1

        cv2.putText(
            frame,
            f"Detected objects: {detected}",
            (20, 35),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.9,
            (0, 255, 0),
            2
        )

        output_msg = self.bridge.cv2_to_imgmsg(
            frame,
            encoding='bgr8'
        )

        self.publisher.publish(output_msg)


if __name__ == '__main__':
    node = LocateItNode()
    rospy.spin()

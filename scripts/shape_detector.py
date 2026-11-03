#!/usr/bin/env python3
import cv2
import numpy as np
import rospy
from sensor_msgs.msg import Image
from cv_bridge import CvBridge, CvBridgeError


class ShapeDetector:
    def __init__(self):
        self.bridge = CvBridge()
        self.topic = rospy.get_param("~image_topic", "/shapes/image_raw")
        self.min_area = float(rospy.get_param("~min_area", 700.0))
        self.max_saturation = int(rospy.get_param("~max_saturation", 75))
        self.min_value = int(rospy.get_param("~min_value", 70))
        self.approx_factor = float(rospy.get_param("~approx_factor", 0.02))
        self.show_window = bool(rospy.get_param("~show_window", True))
        self.sub = rospy.Subscriber(self.topic, Image, self.image_callback,
                                    queue_size=1, buff_size=2**24)
        rospy.loginfo("Shape detector listening on %s", self.topic)

    def classify(self, contour):
        perimeter = cv2.arcLength(contour, True)
        if perimeter <= 0:
            return "Unknown"

        area = cv2.contourArea(contour)
        circularity = 4.0 * np.pi * area / (perimeter * perimeter)

        # Circle is classified by circularity, not by a fixed vertex count.
        if circularity > 0.82:
            return "Circle"

        approx = cv2.approxPolyDP(
            contour, self.approx_factor * perimeter, True
        )
        vertices = len(approx)

        if vertices == 3:
            return "Triangle"
        if vertices == 4:
            # A square has four vertices and an approximately 1:1 bounding box.
            x, y, w, h = cv2.boundingRect(approx)
            ratio = w / float(h) if h else 0
            if 0.85 <= ratio <= 1.15:
                return "Square"
            return "Quadrilateral"
        if vertices == 5:
            return "Pentagon"
        if vertices == 6:
            return "Hexagon"
        return "Unknown"

    def process_frame(self, frame):
        # The shapes are gray while the synthetic backgrounds are saturated.
        # HSV saturation therefore separates foreground from background even
        # when the background hue/color changes between frames.
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(
            hsv,
            np.array([0, 0, self.min_value], dtype=np.uint8),
            np.array([180, self.max_saturation, 255], dtype=np.uint8)
        )

        kernel = np.ones((3, 3), np.uint8)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)

        contours, _ = cv2.findContours(
            mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )

        result = frame.copy()
        counts = {
            "Triangle": 0, "Square": 0, "Pentagon": 0,
            "Hexagon": 0, "Circle": 0
        }

        for contour in contours:
            area = cv2.contourArea(contour)
            if area < self.min_area:
                continue

            label = self.classify(contour)
            if label == "Unknown" or label == "Quadrilateral":
                continue

            counts[label] += 1
            x, y, w, h = cv2.boundingRect(contour)
            cv2.rectangle(result, (x, y), (x + w, y + h), (30, 220, 70), 2)
            cv2.putText(result, label, (x, max(25, y - 8)),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (20, 20, 20), 4)
            cv2.putText(result, label, (x, max(25, y - 8)),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

        total = sum(counts.values())
        cv2.putText(result, "Detected: {}".format(total), (20, 35),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
        summary = "  ".join("{}:{}".format(k, v) for k, v in counts.items())
        cv2.putText(result, summary, (20, 65),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 255), 2)
        return result, mask, counts

    def image_callback(self, msg):
        try:
            frame = self.bridge.imgmsg_to_cv2(msg, desired_encoding="bgr8")
        except CvBridgeError as error:
            rospy.logerr_throttle(2.0, "cv_bridge error: %s", error)
            return

        output, mask, counts = self.process_frame(frame)
        rospy.loginfo_throttle(
            2.0, "Detected shapes: %s",
            ", ".join("{}={}".format(k, v) for k, v in counts.items())
        )

        if self.show_window:
            cv2.imshow("Where Are The Shapes? - Detection", output)
            cv2.imshow("Foreground Mask", mask)
            cv2.waitKey(1)

    def shutdown(self):
        cv2.destroyAllWindows()


if __name__ == "__main__":
    rospy.init_node("shape_detector")
    node = ShapeDetector()
    rospy.on_shutdown(node.shutdown)
    rospy.spin()

#!/usr/bin/env python3

import rospy
import cv2

from sensor_msgs.msg import Image
from cv_bridge import CvBridge


def video_publisher():
    rospy.init_node('video_publisher')

    video_path = rospy.get_param('~video_path')

    publisher = rospy.Publisher(
        '/camera/image_raw',
        Image,
        queue_size=10
    )

    bridge = CvBridge()
    cap = cv2.VideoCapture(video_path)

    if not cap.isOpened():
        rospy.logerr("Tidak bisa membuka video: " + video_path)
        return

    fps = cap.get(cv2.CAP_PROP_FPS)

    if fps <= 0:
        fps = 24.0

    rate = rospy.Rate(fps)

    rospy.loginfo("Video Publisher started. Looping video...")

    while not rospy.is_shutdown():

        ret, frame = cap.read()

        # Mengulang video jika sudah mencapai frame terakhir
        if not ret:
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            continue

        msg = bridge.cv2_to_imgmsg(
            frame,
            encoding='bgr8'
        )

        publisher.publish(msg)

        rate.sleep()

    cap.release()


if __name__ == '__main__':
    video_publisher()

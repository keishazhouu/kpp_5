#!/usr/bin/env python3
import os
import cv2
import rospy
from sensor_msgs.msg import Image
from cv_bridge import CvBridge


def main():
    rospy.init_node("shape_video_publisher")
    video_path = rospy.get_param("~video_path", "")
    topic = rospy.get_param("~image_topic", "/shapes/image_raw")
    output_width = int(rospy.get_param("~output_width", 960))
    loop_video = bool(rospy.get_param("~loop", False))
    fps_override = float(rospy.get_param("~fps", 0.0))

    if not video_path or not os.path.isfile(video_path):
        rospy.logerr("Video tidak ditemukan. Set parameter ~video_path.")
        return

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        rospy.logerr("Gagal membuka video: %s", video_path)
        return

    source_fps = cap.get(cv2.CAP_PROP_FPS)
    publish_fps = fps_override if fps_override > 0 else (source_fps or 30.0)
    rate = rospy.Rate(publish_fps)
    pub = rospy.Publisher(topic, Image, queue_size=1)
    bridge = CvBridge()

    rospy.loginfo("Publishing %s ke %s pada %.2f FPS", video_path, topic, publish_fps)
    while not rospy.is_shutdown():
        ok, frame = cap.read()
        if not ok:
            if loop_video:
                cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                continue
            rospy.loginfo("Video selesai.")
            break

        if output_width > 0 and frame.shape[1] > output_width:
            scale = output_width / float(frame.shape[1])
            frame = cv2.resize(frame, (output_width, int(frame.shape[0] * scale)),
                               interpolation=cv2.INTER_AREA)

        msg = bridge.cv2_to_imgmsg(frame, encoding="bgr8")
        msg.header.stamp = rospy.Time.now()
        pub.publish(msg)
        rate.sleep()

    cap.release()


if __name__ == "__main__":
    main()

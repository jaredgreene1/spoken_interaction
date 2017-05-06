#!/usr/bin/env python

import actionlib
import rospy
import yaml
import sys
import time
import tf2_ros
import tf
import ast
from datetime import datetime
import random
from math import sin, cos, fabs
from landmark_vocal_resolution import *

from nav_msgs.msg import Odometry
from geometry_msgs.msg import PoseStamped, TransformStamped, PoseWithCovarianceStamped, Point
from move_base_msgs.msg import MoveBaseAction, MoveBaseGoal
from moveit_msgs.msg import PlaceLocation, MoveItErrorCodes
from spoken_interaction.msg import VerbalRequest, VerbalResponse, KeyValue
from visualization_msgs.msg import Marker

areaThreshold = 5

def storeLoc(global_location):
    global curr_global_pose
    curr_global_pose = global_location.pose.pose

# If further than thresh then it is a different landmark
def diff_landmarks(old_pos, new_pos):
    if (fabs(old_pos.x - new_pos.x) > areaThreshold) or \
        (fabs(old_pos.y - new_pos.y) > areaThreshold) or \
        (fabs(old_pos.z - new_pos.z) > areaThreshold):
            return True
    else:
        return False

# If key exists, are they diff? If so, overwrite?
def already_known(lm_known, lm_new, current_pos):
    if not lm_new in lm_known:
        return False
    else:
        if diff_landmarks(current_pos, lm_known[lm_new]):
            return True
        else:
            return False


def construct_landmark(lm_new, lm_pub):
    pos = curr_global_pose.position
    #tfPub = tf2_ros.StaticTransformBroadcaster()
    t = TransformStamped()
    t.header.stamp = rospy.Time.now()
    t.header.frame_id = "map"
    t.child_frame_id = lm_new
    t.transform.translation.x = pos.y
    t.transform.translation.y = pos.x
    t.transform.translation.z = 0
    t.transform.rotation.x    = 0.0
    t.transform.rotation.y      = 0.0
    t.transform.rotation.z      = 0.0
    t.transform.rotation.w      = 1
    #tfPub.sendTransform(t)

    if already_known(lm_known, lm_new, pos):
        return False
    else:
        lm_known[lm_new] = pos

        # make and publish the marker
        mrk = Marker()
        mrk.header.frame_id = lm_new
        mrk.header.stamp = rospy.Time.now()
        mrk.ns = "/landmarkers"
        mrk.id = int(random.random()*1000)
        mrk.type = 9
        mrk.action = 0
        mrk.pose = globalPose
        mrk.pose.orientation.w = 1
        mrk.scale.x = 5
        mrk.scale.y = 0
        mrk.scale.z = 0
        mrk.color.r = 0.2
        mrk.color.g = 0.4
        mrk.color.b = 1.0
        mrk.color.a = 0.7
        mrk.lifetime= rospy.Duration(0)
        mrk.frame_locked = True
        mrk.text = lm_new
        lm_pub.publish(mrk)
        return True

class MoveBaseClient(object):
    def __init__(self):
        self.client = actionlib.SimpleActionClient("move_base", MoveBaseAction)
        rospy.loginfo("Waiting for move_base...")
        self.client.wait_for_server()
        rospy.loginfo("have move base")
    def goto(self, lm_pos, theta, frame="map"):
        move_goal = MoveBaseGoal()
        move_goal.target_pose.pose.position.x = lm_pos.x
        move_goal.target_pose.pose.position.y = lm_pos.y
        move_goal.target_pose.pose.orientation.z = sin(theta/2.0)
        move_goal.target_pose.pose.orientation.w = cos(theta/2.0)
        move_goal.target_pose.header.frame_id = frame
        move_goal.target_pose.header.stamp = rospy.Time.now()

        # TODO wait for things to work
        self.client.send_goal(move_goal)
        self.client.wait_for_result()

def handle_exit():
    f = open(sys.argv[1], 'w+')
    yaml.dump(lm_known, f)
    f.close()

if __name__ == "__main__":
    rospy.init_node("remember_landmark")
    curr_global_pose = None

    # Load known landmarks for the map
    if sys.argv == 1:
        lm_known = {}
    else:
        landmarks_file = open(sys.argv[1], 'r')
        lm_known = yaml.load(landmarks_file)
        landmarks_file.close()

    try:
        # Setup clients, subscribers, publishers
        move_base = MoveBaseClient()
        global_location = rospy.Subscriber("amcl_pose", PoseWithCovarianceStamped, storeLoc)
        landmark_marker = rospy.Publisher("landmarks", Marker, queue_size=10)
        vocal_resolver = VocalResolver(lm_known)
        rospy.spin()

    # Make sure we save any new landmarks we learned about today
    finally:
        handle_exit()

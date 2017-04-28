#!/usr/bin/env python

import rospy
import cherrypy
from std_msgs.msg import String

class Root(object):
    @cherrypy.expose
    @cherrypy.tools.json_in()
    
    def index(self):
        print "3" 
        data = cherrypy.request.json
        action = data['result']['action']
        print "4" 
        act_log = "ACTION RECEIVED: " + action
        print "5" 
        act_log = "received something"
        print "6" 
        rospy.loginfo(act_log)
        print "7" 
        self.command_pub.publish(action)
        print "8" 

if __name__ == "__main__":
    # Create a node
    rospy.init_node("spoken_interaction")    

    #NOTE: it is definitely possible for a subscriber to take a while to execute a complex command
    #which could make optimal queue size an important question
    command_pub = rospy.Publisher("verbal_input", String, queue_size = 20)
    print "1" 
    cherrypy.quickstart(Root(), '/')

    print "2" 
#    rate = rospy.Rate(10)
#    while not rospy.is_shutdown():
#      test = "spoken command"
#        rospy.loginfo(test)
#       command_pub.publish(test)
#        rate.sleep()


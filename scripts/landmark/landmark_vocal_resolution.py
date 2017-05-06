import rospy
from geometry_msgs.msg import PoseStamped, TransformStamped, PoseWithCovarianceStamped, Point
from remember_landmark import *




def respond(pub, response_object, response):
    response_object.verbal_response = response[0] 
    response_object.context         = response[1] 
    response_object.timestamp       = str(datetime.now())
    pub.publish(response_object)

def pre_process(new_req1, new_req2, old_req):
    new_req1.clientInfo = new_req1.clientInfo =\
            old_req.clientInfo
    new_req1.request_id = new_req2.request_id = old_req.timestamp
    print new_req1
    print new_req2
    print old_req

class VocalResolver(object):
    def __init__(self,known_lms):
        self._input  = rospy.Subscriber("verbal_input", VerbalRequest, self.req_handler)
        self._output = rospy.Publisher("verbal_response", VerbalResponse, queue_size = 10)
        self._lm     = known_lms
        self._action_id_map = {'navigate_to_landmark': self.nav_to_lm,
                        'build_landmark': self.build_lm,
                        'navigate_to_coordinate':self.nav_to_coord}



    def req_handler(self, request):
        if request.action_id in self._action_id_map:
            receipt_response    = VerbalResponse()
            completion_response = VerbalResponse()
            pre_process(receipt_response, completion_response, request)
            self._action_id_map[request.action_id](request.parameters,
                                             receipt_response,
                                             completion_response)
        else:
            pass

    def nav_to_lm(self, parameters, receipt_response, completion_response):
        lm = next((x.value for x in parameters if x.key=='landmark'), None)
        
        
        VALID_final   =        ("Finished landmark navigation",'')
        INVALID_faultyInput =  ("I don't recognize that information", '')
        INVALID_missingKey =     ("I dont't know where that is!", '')

        if lm and lm in self._lm:
            VALID_initial =        ("Heading to " + lm + "now", 'navigating_to_landmark')
            respond(self._output, receipt_response, VALID_initial)
            move_base.goto(self._lm[lm], 0)
            respond(self._output, completion_response, VALID_final)
        elif lm:
            respond(self._output, completion_response, INVALID_faultyInput)
        else:
            respond(self._output, completion_response, INVALID_missingKey)


    def build_lm(self, parameters, receipt_response, completion_response):
        
        lm = next((x.value for x in parameters if x.key=='landmark'), None)
        
        FAILURE = ("I already know a location on this map by that name! " +\
                   "Are you trying to confuse me?", '')
        INVALID_missingKey =  ("I don't recognize that information", '')

        if lm:
            SUCCESS = ("Thanks! I'll remember that this is " + lm, '')
            respond(self._output, completion_response, SUCCESS) if\
            construct_landmark(lm, landmarkMarker) else\
            respond(self._output, completion_response, FAILURE)
        else:
            respond(self._output, completion_response, INVALID_faultyInput)


    def nav_to_coord(self, parameters, receipt_response, completion_response):
        VALID_initial =        ("Heading to the coordinates!", 'navigating_to_coordinates')
        VALID_final   =        ("Finished landmark navigation",'')
        INVALID_faultyInput =  ("Are you sure those were numbers?", '')
        INVALID_missingKey =     ("I didn't hear any coordinates?", '')

        pos = Point()
        coordinates = next((x for x in parameters if x.key=='coordinate'), None)
        if coordinates:
            coords = ast.literal_eval(coordinates.value)
            try:
                pos.x = int(coords['x'])
                pos.y = int(coords['y'])
                pos.z = 0
                respond(self._output, receipt_response, VALID_initial)
                move_base.goto(pos, 0)
                respond(completion_response, VALID_final)
            except ValueError:
                respond(self._output, completion_response, INVALID_faultyInput)
        else:
            respond(self._output, completion_response, INVALID_missingKey)


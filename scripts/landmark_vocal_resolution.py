import rospy
from geometry_msgs.msg import PoseStamped, TransformStamped, PoseWithCovarianceStamped, Point
from remember_landmark import *




def respond(pub, response_object, response):
    print "SENDING RESPONSES: "
    print response
    
    response_object.verbal_response = response[0] 
    response_object.context         = response[1] 
    response_object.timestamp       = str(datetime.now())
    
    pub.publish(response_object)

def build_responses(req):
    init_resp = VerbalResponse()
    end_resp  = VerbalResponse()
    
    init_resp.clientInfo = end_resp.clientInfo = req.clientInfo
    init_resp.request_id = end_resp.request_id = req.timestamp
    return init_resp, end_resp

def lm_to_point(lm):
    point = Point()
    point.x = lm[0]
    point.y = lm[1]
    return point


class VocalResolver(object):
    def __init__(self, known_lms, move_base, construct_landmark):
        self._input  = rospy.Subscriber("verbal_input", VerbalRequest, self.req_handler)
        self._output = rospy.Publisher("verbal_response", VerbalResponse, queue_size = 10)
        self._lm     = known_lms
        self._move_base = move_base
        self._construct_landmark = construct_landmark
        self._action_id_map = {'navigate_to_landmark': self.nav_to_lm,
                        'build_landmark': self.build_lm,
                        'navigate_to_coordinate':self.nav_to_coord}

    def req_handler(self, request):
        if request.action_id in self._action_id_map:
            receipt_response, completion_response = build_responses(request)
            print "DOES THE CHANEGE CARRY OVER *****************************************" 
            print receipt_response
             
            self._action_id_map[request.action_id](request.parameters,
                                             receipt_response,
                                             completion_response)
        else:
            pass

    def nav_to_lm(self, parameters, receipt_response, completion_response):
        lm = next((x.value for x in parameters if x.key=='landmark'), None)
        VALID_final   =        ("Finished landmark navigation",'')
        INVALID_missingKey =  ("I don't recognize that information", '')
        INVALID_faultyInput =     ("I dont't know where that is!", '')

        if lm:
            VALID_initial =        ("Heading to " + lm + "now", 'navigating_to_landmark')
            respond(self._output, receipt_response, VALID_initial)
            if move_to_landmark(lm, self._lm, self._move_base):
                respond(self._output, completion_response, VALID_final)
            else:
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
            self._construct_landmark(lm) else\
            respond(self._output, completion_response, FAILURE)
        else:
            respond(self._output, completion_response, INVALID_missingKey)


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
                self._move_base.goto(pos, 0)
                respond(self._output, completion_response, VALID_final)
            except ValueError:
                respond(self._output, completion_response, INVALID_faultyInput)
        else:
            respond(self._output, completion_response, INVALID_missingKey)


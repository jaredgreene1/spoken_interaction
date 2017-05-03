import rospy
from geometry_msgs.msg import PoseStamped, TransformStamped, PoseWithCovarianceStamped, Point
from remember_landmark import

def respond(response_object, message, context):
    receipt_response.verbal_response = message
    receipt_response.context         = context
    receipt_response.timestamp       = str(datetime.now())
    vocalResponse.publish(receipt_response)


class VocalResolver(object, move_base):
    def __init__(self):
        self.__input  = rospy.Subscriber("verbal_input", VerbalRequest, self.req_handler)
        self.__output = rospy.Publisher("verbal_response", VerbalResponse, queue_size = 10)

        action_id_map = {'navigate_to_landmark': nav_to_lm,
                        'build_landmark':build_lm,
                        'navigate_to_coordinate':nav_to_coord}

    def req_handler(request):
        if request.action_id in action_id_map:
            receipt_response    = VerbalResponse()
            completion_response = VerbalResponse()
            action_id_map[request.action_id](request.parameters,
                                             receipt_response,
                                             completion_response)
        else:
            pass

    def nav_to_lm(parameters, receipt_response, completion_response):
        VALID_initial =        ("Heading to landmark now", 'navigating_to_landmark')
        VALID_final   =        ("Finished landmark navigation",'')
        INVALID_faultyInput =  ("I don't recognize that information", '')
        INVALID_missingKey =     ("I dont't know where that is!", '')

        lm = next((x.value for x in parameters if x.key=='landmark'), None)
        if lm and lm in lm_known
            respond(receipt_response, VALID_initial)
            move_base.goto(lm_known[lm], 0)
            respond(completion_response, VALID_final)
        elif lm:
            respond(completion_response, INVALID_faultyInput)
        else:
            respond(completion_response, INVALID_faulty_input)


    def build_lm(parameters, receipt_response, completion_response):
        SUCCESS = ("Thanks! I'll remember that this is " + lm, '')
        FAILURE = ("I already know a location on this map by that name! " +\
                   "Are you trying to confuse me?", '')
        INVALID_missingKey =  ("I don't recognize that information", '')

        lm = next((x.value for x in parameters if x.key=='landmark'), None)
        if lm:
            if construct_landmark(lm_known, lm, landmarkMarker) \
            respond(completion_response, SUCCESS) else
            respond(completion_response, FAILURE)
        else:
            respond(completion_response, INVALID_faultyInput)


    def nav_to_coord(parameters, receipt_response, completion_response):
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
                respond(receipt_response, VALID_initial)
                move_base.goto(pos, 0)
                respond(completion_response, VALID_final)
            except ValueError:
                respond(completion_response, INVALID_faultyInput)
        else:
            respond(completion_response, INVALID_missingKey)

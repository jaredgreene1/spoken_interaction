import threading
import time

def mockThread():
    for i in robot:
        print i
        time.sleep(.5)


if __name__ == '__main__':
    robot = ['robot1']
    thread = threading.Thread(target=mockThread)
    thread.start()

    for i in range(5):
        robot_name = "robot_" + str(i)
        robot.append(robot_name)
        print "main is sleeping"
        time.sleep(.5)



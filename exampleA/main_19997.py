import vrep
import sys
import cv2
import numpy as np
import time
import random

vrep.simxFinish(-1)
clientID = vrep.simxStart('127.0.0.1', 19997, True, True, 5000, 5)
print('Client ID: ', clientID)

if clientID != -1:
    print('Connection successfull!')
else:
    sys.exit('Error!')

velocity = 50
tork = 100
_, left_motor_handle = vrep.simxGetObjectHandle(clientID, 'Pioneer_p3dx_leftMotor', vrep.simx_opmode_oneshot_wait)
_, right_motor_handle = vrep.simxGetObjectHandle(clientID, 'Pioneer_p3dx_rightMotor', vrep.simx_opmode_oneshot_wait)
_, camhandle = vrep.simxGetObjectHandle(clientID, 'Vision_sensor', vrep.simx_opmode_oneshot_wait)
_, resolution, image = vrep.simxGetVisionSensorImage(clientID, camhandle, 0, vrep.simx_opmode_streaming)
time.sleep(2)

def left():
    for i in range(tork):
        vrep.simxSetJointTargetVelocity(clientID, left_motor_handle, -velocity, vrep.simx_opmode_streaming)
        vrep.simxSetJointTargetVelocity(clientID, right_motor_handle, velocity, vrep.simx_opmode_streaming)

def right():
    for i in range(tork):
        vrep.simxSetJointTargetVelocity(clientID, left_motor_handle, velocity, vrep.simx_opmode_streaming)
        vrep.simxSetJointTargetVelocity(clientID, right_motor_handle, -velocity, vrep.simx_opmode_streaming)

def up():
    for i in range(tork):
        vrep.simxSetJointTargetVelocity(clientID, left_motor_handle, velocity, vrep.simx_opmode_streaming)
        vrep.simxSetJointTargetVelocity(clientID, right_motor_handle, velocity, vrep.simx_opmode_streaming)

def down():
    for i in range(tork):
        vrep.simxSetJointTargetVelocity(clientID, left_motor_handle, -velocity, vrep.simx_opmode_streaming)
        vrep.simxSetJointTargetVelocity(clientID, right_motor_handle, -velocity, vrep.simx_opmode_streaming)

def stop():
    for i in range(tork):
        vrep.simxSetJointTargetVelocity(clientID, left_motor_handle, 0, vrep.simx_opmode_streaming)
        vrep.simxSetJointTargetVelocity(clientID, right_motor_handle, 0, vrep.simx_opmode_streaming)




font = cv2.FONT_HERSHEY_SIMPLEX

def draw(mask,color):
    contours,_ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    for cont in contours:
        area = cv2.contourArea(cont)
        if area > 3000:
            mnt = cv2.moments(cont)
            if (mnt["m00"]==0): mnt["m00"]=1
            x = int(mnt["m10"]/mnt["m00"])
            y = int(mnt['m01']/mnt['m00'])
            newContour = cv2.convexHull(cont)
            cv2.circle(img,(x,y),7,(0,255,0),-1)
            cv2.putText(img,'{},{}'.format(x,y),(x+10,y), font, 0.75,(0,255,0),1,cv2.LINE_AA)
            cv2.drawContours(img, [newContour], 0, color, 3)

lightblue = np.array([100,100,20],np.uint8)
darkblue = np.array([125,255,255],np.uint8)

lightyellow = np.array([15,100,20],np.uint8)
darkyellow = np.array([45,255,255],np.uint8)

lightred1 = np.array([0,100,20],np.uint8)
darkred1 = np.array([5,255,255],np.uint8)
lightred2 = np.array([175,100,20],np.uint8)
darkred2 = np.array([179,255,255],np.uint8)


while True:
    _, resolution, image = vrep.simxGetVisionSensorImage(clientID, camhandle, 0, vrep.simx_opmode_buffer)
    img = np.array(image, dtype=np.uint8)
    img.resize([resolution[0], resolution[1], 3])
    img = np.rot90(img, 2)
    img = np.fliplr(img)
    img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)

    #
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    maskBlue = cv2.inRange(hsv, lightblue, darkblue)
    maskYellow = cv2.inRange(hsv, lightyellow, darkyellow)
    maskRed1 = cv2.inRange(hsv, lightred1, darkred1)
    maskRed2 = cv2.inRange(hsv, lightred2, darkred2)
    maskRed = cv2.add(maskRed1, maskRed2)
    draw(maskBlue, (255,0,0))
    draw(maskYellow, (0,255,0))
    draw(maskRed, (0,0,255))
    #

    cv2.imshow('port_19997', img)
    key = cv2.waitKey(1)
    # print('running', '.' * random.randint(0, 5))

    # a -> 97
    # d -> 100
    # w -> 119
    # s -> 115
    if key == 97:
        left()
        time.sleep(0.050)
        print('a')

    if key == 100:
        right()
        time.sleep(0.050)
        print('d')

    if key == 119:
        up()
        time.sleep(0.050)
        print('w')

    if key == 115:
        down()
        time.sleep(0.050)
        print('s')
    
    stop()
    if key == 27:
        cv2.destroyAllWindows()
        exit()
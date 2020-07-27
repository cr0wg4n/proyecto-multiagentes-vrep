# RECONOCEDOR DE FIGURAS
import vrep
import sys
import cv2
import numpy as np
import time
import random

vrep.simxFinish(-1)
clientID = vrep.simxStart('127.0.0.1', 19999, True, True, 5000, 5)
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
var = 'cuad'
colorf = (0,110,0)
def shaped(mask,color):
    contours,_ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    for cont in contours:
        area = cv2.contourArea(cont)
        approx = cv2.approxPolyDP(cont, 0.01* cv2.arcLength(cont,True), True)
        x = approx.ravel()[0]
        y = approx.ravel()[1]
        if area > 150:
            mnt = cv2.moments(approx)
            if (mnt["m00"]==0): mnt["m00"]=1
            x = int(mnt["m10"]/mnt["m00"])
            y = int(mnt['m01']/mnt['m00'])
            newContour = cv2.convexHull(approx)
            #cv2.circle(img,(x,y),7,(0,255,0),-1)
            cv2.drawContours(img, [newContour], 0, color, 5)
            if var == 'triang':
                if len(newContour) == 3:
                    triang(x,y)
                    break
            elif var == 'cuad':
                if len(newContour) >= 4 and len(newContour) <= 6:
                    cuadr(x,y)
                    break
            elif var == 'circ':
                if 10 < len(newContour):
                    circ(x,y)
                    break
            else:
                print('Figura no valida')
                break

def triang(x,y):
    cv2.putText(img, 'Triangulo', (x,y), font, 1, colorf, 2)

def cuadr(x,y):
    cv2.putText(img, 'Rectangulo', (x,y), font, 1, colorf, 2)

def circ(x,y):
    cv2.putText(img, 'Circulo', (x,y), font, 1, colorf, 2)

lightred1 = np.array([0,100,20])
darkred1 = np.array([5,255,255])
lightred2 = np.array([175,100,20])
darkred2 = np.array([179,255,255])
lightblue = np.array([100,100,20])
darkblue = np.array([125,255,255])
lightgreen = np.array([40,50,50])
darkgreen = np.array([80,255,255])


while True:
    _, resolution, image = vrep.simxGetVisionSensorImage(clientID, camhandle, 0, vrep.simx_opmode_buffer)
    img = np.array(image, dtype=np.uint8)
    img.resize([resolution[0], resolution[1], 3])
    img = np.rot90(img, 2)
    img = np.fliplr(img)
    img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)

    #
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    maskRed1 = cv2.inRange(hsv, lightred1, darkred1)
    maskRed2 = cv2.inRange(hsv, lightred2, darkred2)
    maskRed = cv2.add(maskRed1, maskRed2)
    maskBlue = cv2.inRange(hsv, lightblue, darkblue)
    maskGreen = cv2.inRange(hsv, lightgreen, darkgreen)
    kernel = np.ones((5,5), np.uint8)
    maskRed = cv2.erode(maskRed, kernel)
    maskBlue = cv2.erode(maskBlue, kernel)
    maskGreen = cv2.erode(maskGreen, kernel)

    shaped(maskRed, (0,0,255))
    shaped(maskBlue, (255,0,0))
    shaped(maskGreen, (0,255,0))
    #

    cv2.imshow('port_19999', img)
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
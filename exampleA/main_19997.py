# RECONOCEDOR DE COLORES
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

velocity = 13
tork = 32
tork_rotation = 8
areas = []

_, left_motor_handle = vrep.simxGetObjectHandle(clientID, 'Pioneer_p3dx_leftMotor', vrep.simx_opmode_oneshot_wait)
_, right_motor_handle = vrep.simxGetObjectHandle(clientID, 'Pioneer_p3dx_rightMotor', vrep.simx_opmode_oneshot_wait)
_, camhandle = vrep.simxGetObjectHandle(clientID, 'Vision_sensor', vrep.simx_opmode_oneshot_wait)
_, resolution, image = vrep.simxGetVisionSensorImage(clientID, camhandle, 0, vrep.simx_opmode_streaming)
time.sleep(2)

def left():
    for i in range(tork_rotation):
        vrep.simxSetJointTargetVelocity(clientID, left_motor_handle, -velocity, vrep.simx_opmode_streaming)
        vrep.simxSetJointTargetVelocity(clientID, right_motor_handle, velocity, vrep.simx_opmode_streaming)
        time.sleep(0.0001)
def right():
    for i in range(tork_rotation):
        vrep.simxSetJointTargetVelocity(clientID, left_motor_handle, velocity, vrep.simx_opmode_streaming)
        vrep.simxSetJointTargetVelocity(clientID, right_motor_handle, -velocity, vrep.simx_opmode_streaming)
        time.sleep(0.0001)

def up():
    for i in range(tork):
        vrep.simxSetJointTargetVelocity(clientID, left_motor_handle, -velocity, vrep.simx_opmode_streaming)
        vrep.simxSetJointTargetVelocity(clientID, right_motor_handle, -velocity, vrep.simx_opmode_streaming)
        time.sleep(0.0001)

def down():
    for i in range(int(tork/2)):
        vrep.simxSetJointTargetVelocity(clientID, left_motor_handle, velocity, vrep.simx_opmode_streaming)
        vrep.simxSetJointTargetVelocity(clientID, right_motor_handle, velocity, vrep.simx_opmode_streaming)
        time.sleep(0.0001)

def stop():
        vrep.simxSetJointTargetVelocity(clientID, left_motor_handle, 0, vrep.simx_opmode_streaming)
        vrep.simxSetJointTargetVelocity(clientID, right_motor_handle, 0, vrep.simx_opmode_streaming)
 

font = cv2.FONT_HERSHEY_SIMPLEX
var = 'azul'
redc = (0,0,255)
bluec = (255,0,0)
greenc = (0,255,0)

def draw(name, mask, color):
    contours,_ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    for cont in contours:
        area = cv2.contourArea(cont)
        if area > 150:
            mnt = cv2.moments(cont)
            if (mnt["m00"]==0): mnt["m00"]=1
            x = int(mnt["m10"]/mnt["m00"])
            y = int(mnt['m01']/mnt['m00'])
            newContour = cv2.convexHull(cont)
            cv2.circle(img,(x,y),7,(0,255,0),-1)
            if var == 'rojo':
                rojo(x,y,newContour)
            elif var == 'azul':
                azul(x,y,newContour)
            elif var == 'verde':
                verde(x,y,newContour)
            else:
                continue

def rojo(x,y,newContour):
    cv2.drawContours(img, [newContour], 0, redc, 3)
    put_center(x, y, redc)

def azul(x,y,newContour):
    cv2.drawContours(img, [newContour], 0, bluec, 3)
    put_center(x, y, bluec)

def verde(x, y, newContour):
    cv2.drawContours(img, [newContour], 0, greenc, 3)
    put_center(x, y, greenc)
    
def put_center(x,y,color):
    cv2.circle(img,(x,y),7,color,-1)
    cv2.putText(img,'{},{}'.format(x,y),(x+10,y), font, 0.75,(0,255,0),1,cv2.LINE_AA)
    
lightblue = np.array([100,100,20],np.uint8)
darkblue = np.array([125,255,255],np.uint8)
lightred1 = np.array([0,100,20],np.uint8)
darkred1 = np.array([5,255,255],np.uint8)
lightred2 = np.array([175,100,20],np.uint8)
darkred2 = np.array([179,255,255],np.uint8)
lightgreen = np.array([57,64,55], np.uint8)
darkgreen = np.array([77,255,255], np.uint8)


def interpolation(img, area, x, y):
    error = 3
    width = np.size(img, 1)
    height = np.size(img, 0)
    absolute_center_y = int(height / 2)
    absolute_center_x = int(width / 2)

    delta_x = absolute_center_x - x
    delta_y = absolute_center_y -y

    if abs(delta_x) <= error * 2:
        delta_x = 0
        
    if area < ((width - error) * (height - error)):
        if delta_x > 0:
            left()
        elif delta_x < 0:
            right()
    
        if delta_y > 0:
            up()
        else:
            pass
    else:
        print("llege al objetivo")


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
    maskGreen = cv2.inRange(hsv, lightgreen, darkgreen)
    maskRed1 = cv2.inRange(hsv, lightred1, darkred1)
    maskRed2 = cv2.inRange(hsv, lightred2, darkred2)
    maskRed = cv2.add(maskRed1, maskRed2)

    if var == 'azul':
        draw('blue', maskBlue, (255,0,0))
    elif var == 'verde':
        draw('green', maskGreen, (0,255,0))
    elif var == 'rojo':
        draw('red', maskRed, (0,0,255))
    else:
        print('Figura no valida')
        break

    # Seguir a los cubos más cercanos (green, yellow, red, blue)
    #draw('green', maskGreen, (0, 255, 0))
    #draw('blue', maskBlue, (255,0,0))
    #draw('yellow', maskYellow, (0,255,0))
    #draw('red', maskRed, (0,0,255))
    
    value = 0
    target = None
    for area in areas:
        if area["area"] > value:
            value = area["area"]
            target = area
    if target:
        print(target["name"])
        interpolation(hsv, target["area"] ,target["center"]["x"], target["center"]["y"])
    else:
        right()

    areas = []
    cv2.imshow('port_19997', img)
    key = cv2.waitKey(1)
    # print('running', '.' * random.randint(0, 5))

    # a -> 97
    # d -> 100
    # w -> 119
    # s -> 115
    if key == 97:
        left()

    if key == 100:
        right()

    if key == 119:
        up()

    if key == 115:
        down()

    stop()

    if key == 27:
        cv2.destroyAllWindows()
        exit()
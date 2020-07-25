import os 
import vrep
import sys
import cv2
import time
import random
import numpy as np

vrep.simxFinish(-1)
clientID = vrep.simxStart('127.0.0.1', 19997, True, True, 5000, 5)
print('Client ID: ', clientID)

if clientID != -1:
    print('Connection successfull!')
else:
    sys.exit('Error!')

velocity = 30
tork = 75
tork_rotation = 50
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
    for i in range(tork):
        vrep.simxSetJointTargetVelocity(clientID, left_motor_handle, velocity, vrep.simx_opmode_streaming)
        vrep.simxSetJointTargetVelocity(clientID, right_motor_handle, velocity, vrep.simx_opmode_streaming)
        time.sleep(0.0001)

def stop():
        vrep.simxSetJointTargetVelocity(clientID, left_motor_handle, 0, vrep.simx_opmode_streaming)
        vrep.simxSetJointTargetVelocity(clientID, right_motor_handle, 0, vrep.simx_opmode_streaming)
 

while True:
    _, resolution, image = vrep.simxGetVisionSensorImage(clientID, camhandle, 0, vrep.simx_opmode_buffer)
    img = np.array(image, dtype=np.uint8)
    img.resize([resolution[0], resolution[1], 3])
    img = np.rot90(img, 2)
    img = np.fliplr(img)
    img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
    cv2.imshow('port_19997', img)
    key = cv2.waitKey(1)
    # print('running', '.' * random.randint(0, 5))

    # a -> 97
    # d -> 100
    # w -> 119
    # s -> 115
    if key == 97:
        left()
        print('a')

    if key == 100:
        right()
        print('d')

    if key == 119:
        up()
        print('w')

    if key == 115:
        down()
        print('s')

    stop()

    if key == 27:
        cv2.destroyAllWindows()
        exit()
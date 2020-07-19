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

velocity = 15
_, left_motor_handle = vrep.simxGetObjectHandle(clientID, 'Pioneer_p3dx_leftMotor', vrep.simx_opmode_oneshot_wait)
_, right_motor_handle = vrep.simxGetObjectHandle(clientID, 'Pioneer_p3dx_rightMotor', vrep.simx_opmode_oneshot_wait)
_, camhandle = vrep.simxGetObjectHandle(clientID, 'Vision_sensor', vrep.simx_opmode_oneshot_wait)
_, resolution, image = vrep.simxGetVisionSensorImage(clientID, camhandle, 0, vrep.simx_opmode_streaming)
time.sleep(2)

def right():
    vrep.simxSetJointTargetVelocity(clientID, left_motor_handle, -velocity, vrep.simx_opmode_streaming)
    vrep.simxSetJointTargetVelocity(clientID, right_motor_handle, velocity, vrep.simx_opmode_streaming)

def left():
    vrep.simxSetJointTargetVelocity(clientID, left_motor_handle, velocity, vrep.simx_opmode_streaming)
    vrep.simxSetJointTargetVelocity(clientID, right_motor_handle, -velocity, vrep.simx_opmode_streaming)

def up():
    vrep.simxSetJointTargetVelocity(clientID, left_motor_handle, velocity, vrep.simx_opmode_streaming)
    vrep.simxSetJointTargetVelocity(clientID, right_motor_handle, velocity, vrep.simx_opmode_streaming)

def down():
    vrep.simxSetJointTargetVelocity(clientID, left_motor_handle, -velocity, vrep.simx_opmode_streaming)
    vrep.simxSetJointTargetVelocity(clientID, right_motor_handle, -velocity, vrep.simx_opmode_streaming)

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
        up()
        print('a')

    if key == 100:
        right()
        print('d')

    if key == 119:
        left()
        print('w')

    if key == 115:
        down()
        print('s')
    
    if key == 27:
        cv2.destroyAllWindows()
        exit()
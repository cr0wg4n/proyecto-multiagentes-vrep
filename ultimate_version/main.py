import vrep
import sys
import cv2
import random
import numpy as np
from models.robot import Robot
from models.endpoint import Endpoint


VELOCITY_TURBO = 60
VELOCITY_FAST = 60
VELOCITY_SLOW = 40
TORK_TUBO = 80
TORK_FAST = 50
TORK_SLOW = 33

VELOCITY_ROTATION_TURBO = 60
VELOCITY_ROTATION_FAST = 40
VELOCITY_ROTATION_SLOW = 28
TORK_ROTATE_TURBO = 55
TORK_ROTATE_FAST = 35
TORK_ROTATE_SLOW = 7

ERROR = 3
 
endpoints = ['Endpoint#0','Endpoint#1','Endpoint#2','Endpoint#3'] 
areas = []

vrep.simxFinish(-1)
client_id = vrep.simxStart('127.0.0.1', 19997, True, True, 5000, 5)
print('Client ID: ', client_id)

if client_id != -1:
    print('Conexión exitosa!')
else:
    sys.exit('Error!')

win_name = "camera_{}".format(random.randint(1,1000))
robot = Robot(  
                vrep, client_id,
                name= 'Pioneer_p3dx',
                name_motor_left='Pioneer_p3dx_leftMotor',
                name_motor_right='Pioneer_p3dx_rightMotor',
                name_camera='Vision_sensor',
                name_prox_sensor='Proximity_sensor',
                name_payload='Payload',
                velocity=VELOCITY_SLOW,
                velocity_rotation=VELOCITY_ROTATION_SLOW,
                tork=TORK_SLOW,
                tork_rotation=TORK_ROTATE_SLOW,
                error=ERROR
            )

font = cv2.FONT_HERSHEY_SIMPLEX

def draw(name, mask, color):
    contours,_ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    for cont in contours:
        area = cv2.contourArea(cont)
        if area > 50:
            mnt = cv2.moments(cont)
            if (mnt["m00"]==0): mnt["m00"]=1
            x = int(mnt["m10"]/mnt["m00"])
            y = int(mnt['m01']/mnt['m00'])
            newContour = cv2.convexHull(cont)
            cv2.circle(img,(x,y),7,(0,255,0),-1)
            cv2.putText(img,'{},{}'.format(x,y),(x+10,y), font, 0.75,(0,255,0),1,cv2.LINE_AA)
            cv2.drawContours(img, [newContour], 0, color, 3)
            areas.append({'name': name, 'area': area, 'center': {'x': x, 'y': y} })

lightblue = np.array([100,100,20],np.uint8)
darkblue = np.array([125,255,255],np.uint8)

lightyellow = np.array([15,100,20],np.uint8)
darkyellow = np.array([45,255,255],np.uint8)

lightred1 = np.array([0,100,20],np.uint8)
darkred1 = np.array([5,255,255],np.uint8)

lightred2 = np.array([175,100,20],np.uint8)
darkred2 = np.array([179,255,255],np.uint8)

lightgreen = np.array([57,64,55], np.uint8)
darkgreen = np.array([77,255,255], np.uint8)


while True:
    img = robot.read_camera()

    #
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    maskBlue = cv2.inRange(hsv, lightblue, darkblue)
    maskYellow = cv2.inRange(hsv, lightyellow, darkyellow)
    maskRed1 = cv2.inRange(hsv, lightred1, darkred1)
    maskRed2 = cv2.inRange(hsv, lightred2, darkred2)
    maskRed = cv2.add(maskRed1, maskRed2)
    maskGreen = cv2.inRange(hsv, lightgreen, darkgreen)

    # Seguir a los cubos más cercanos (green, yellow, red, blue)
    draw('green', maskGreen, (0, 255, 0))
    draw('blue', maskBlue, (255,0,0))
    draw('yellow', maskYellow, (0,255,0))
    draw('red', maskRed, (0,0,255))
    
    value = 0
    target = None
    if robot.searching:
        for area in areas:
            if area["area"] > value:
                value = area["area"]
                target = area
        if target:
            robot.tork_rotation=TORK_ROTATE_SLOW
            robot.interpolation(hsv, target["area"] ,target["center"]["x"], target["center"]["y"])
        else:
            robot.tork_rotation=TORK_ROTATE_FAST
            robot.move_right()
    else:
        robot.go_to_endpoint(endpoints)
    areas = []

    cv2.imshow(win_name, img)
    key = cv2.waitKey(1)

    # a -> 97
    # d -> 100
    # w -> 119
    # s -> 115
    if key == 97:
        robot.move_left()
    if key == 100:
        robot.move_right()
    if key == 119:
        robot.move_up()
    if key == 115:
        robot.move_down()
    if key == 27:
        cv2.destroyAllWindows()
        exit()

    robot.move_stop()
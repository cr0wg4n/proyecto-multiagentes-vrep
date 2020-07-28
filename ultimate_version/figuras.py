# RECONOCEDOR DE FIGURAS
import vrep
import sys
import cv2
import numpy as np
import random
from models.robot import Robot
from models.endpoint import Endpoint
import re
import socket

# Ejemplo para correr programa

#                             python figuras.py 127.0.0.1:19999# cuad


valid_figures = ['cuad', 'triang', 'circ']
ip_puerto = str(sys.argv[1])
r = re.match(r'^([0-9]{0,3}.[0-9]{0,3}.[0-9]{0,3}.[0-9]{0,3}):([0-9]{0,7})#(\d+)?$', ip_puerto)

if bool(r):
    ip, port, sufix = r.groups()
    if not sufix:
        sufix = ''
    else:
        sufix = '#' + str(sufix)
    figura = str(sys.argv[2])
    if not (figura in valid_figures): sys.exit('figura inválida')
else:
    sys.exit('Argumentos inválidos')


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
client_id = vrep.simxStart('127.0.0.1', 19999, True, True, 5000, 5)
print('Client ID: ', client_id)

if client_id != -1:
    print('Conexión exitosa!')
else:
    sys.exit('Error!')

win_name = "{}({})".format(random.randint(1, 300), figura)

var = figura
print('ip: {}   port: {}   robot_id: {}   figura: {}'.format(ip, port, sufix or 'padre', figura))


font = cv2.FONT_HERSHEY_SIMPLEX
colorf = (0,110,0)
lightred1 = np.array([0,100,20])
darkred1 = np.array([5,255,255])
lightred2 = np.array([175,100,20])
darkred2 = np.array([179,255,255])
lightblue = np.array([100,100,20])
darkblue = np.array([125,255,255])
lightgreen = np.array([40,50,50])
darkgreen = np.array([80,255,255])


robot = Robot(  
                vrep, client_id,
                name= 'Pioneer_p3dx{}'.format(sufix),
                name_motor_left='Pioneer_p3dx_leftMotor{}'.format(sufix),
                name_motor_right='Pioneer_p3dx_rightMotor{}'.format(sufix),
                name_camera='Vision_sensor{}'.format(sufix),
                name_prox_sensor='Proximity_sensor{}'.format(sufix),
                name_payload='Payload{}'.format(sufix),
                velocity=VELOCITY_SLOW,
                velocity_rotation=VELOCITY_ROTATION_SLOW,
                tork=TORK_SLOW,
                tork_rotation=TORK_ROTATE_SLOW,
                error=ERROR
            )


def shaped(mask,color):
    contours,_ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    for cont in contours:
        area = cv2.contourArea(cont)
        approx = cv2.approxPolyDP(cont, 0.01* cv2.arcLength(cont,True), True)
        x = approx.ravel()[0]
        y = approx.ravel()[1]
        if area > 10:
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
                    areas.append({'name': 'Triangulo', 'area': area, 'center': {'x': x, 'y': y} })
                    break
            elif var == 'cuad':
                if len(newContour) >= 4 and len(newContour) <= 6:
                    cuadr(x,y)
                    areas.append({'name': 'Cuadrado', 'area': area, 'center': {'x': x, 'y': y} })
                    break
            elif var == 'circ':
                if 10 < len(newContour):
                    circ(x,y)
                    areas.append({'name': 'Circulo', 'area': area, 'center': {'x': x, 'y': y} })
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
try:
    host = '127.0.0.1'
    port1 = 6000
    id_rob = str(robot.handle)
    id_roboto = bytes(id_rob, 'utf-8')
    msg = ' recogere figura '+ figura
    msg = bytes(msg, 'utf-8')
    s = socket.socket() 
    s.connect((host, port1))
    s.sendall(b'Soy el robot '+id_roboto+msg+b' !')
    print (s.recv(1024))
    s.close()
except:
    pass

while True:
    img = robot.read_camera()
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

    value = 0
    target = None
    if robot.searching:
        for area in areas:
            if area["area"] > value:
                value = area["area"]
                target = area
        if target:
            robot.tork_rotation=TORK_ROTATE_SLOW
            robot.interpolation(hsv, target["area"] ,target["center"]["x"], target["center"]["y"], (var=='circ'))
        else:
            robot.tork_rotation=TORK_ROTATE_FAST
            robot.move_right()
    else:
        robot.go_to_endpoint(endpoints)
    areas = []

    cv2.imshow(win_name, img)
    key = cv2.waitKey(1)
    robot.move_stop()

    if key == 27:
        cv2.destroyAllWindows()
        exit()
# RECONOCEDOR DE COLORES
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

#                             python colores.py 127.0.0.1:19999# rojo


valid_colors = ['rojo', 'azul', 'verde']
ip_puerto = str(sys.argv[1])
r = re.match(r'^([0-9]{0,3}.[0-9]{0,3}.[0-9]{0,3}.[0-9]{0,3}):([0-9]{0,7})#(\d+)?$', ip_puerto)

if bool(r):
    ip, port, sufix = r.groups()
    if not sufix:
        sufix = ''
    else:
        sufix = '#' + str(sufix)
    color = str(sys.argv[2])
    if not (color in valid_colors): sys.exit('color inválido')

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
client_id = vrep.simxStart('127.0.0.1', 19997, True, True, 5000, 5)
print('Client ID: ', client_id)

if client_id != -1:
    print('Conexión exitosa!')
else:
    sys.exit('Error!')

win_name = "{}({})".format(random.randint(1, 300), color)

var = color
print('ip: {}   port: {}   robot_id: {}   color: {}'.format(ip, port, sufix or 'padre', color))


font = cv2.FONT_HERSHEY_SIMPLEX
redc = (0,0,255)
bluec = (255,0,0)
greenc = (0,255,0)
lightblue = np.array([100,100,20],np.uint8)
darkblue = np.array([125,255,255],np.uint8)
lightred1 = np.array([0,100,20],np.uint8)
darkred1 = np.array([5,255,255],np.uint8)
lightred2 = np.array([175,100,20],np.uint8)
darkred2 = np.array([179,255,255],np.uint8)
lightgreen = np.array([57,64,55], np.uint8)
darkgreen = np.array([77,255,255], np.uint8)


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
            if var == 'rojo':
                rojo(x,y,newContour)
                areas.append({'name': name, 'area': area, 'center': {'x': x, 'y': y} })
            elif var == 'azul':
                azul(x,y,newContour)
                areas.append({'name': name, 'area': area, 'center': {'x': x, 'y': y} })
            elif var == 'verde':
                verde(x,y,newContour)
                areas.append({'name': name, 'area': area, 'center': {'x': x, 'y': y} })
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

try:
    host = '127.0.0.1'
    port1 = 6000
    id_rob = str(robot.handle)
    id_roboto = bytes(id_rob, 'utf-8')
    msg = ' recogere el color '+ color
    msg = bytes(msg, 'utf-8')
    s = socket.socket() 
    s.connect((host, port1))
    s.sendall(b'Soy el robot '+ id_roboto+ msg+ b' !')
    print (s.recv(1024))
    s.close()     
except:
    pass

while True:
    img = robot.read_camera()
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
    robot.move_stop()

    if key == 27:
        cv2.destroyAllWindows()
        exit()
# RECONOCEDOR DE COLORES Y FIGURAS
import vrep
import sys
import cv2
import numpy as np
import time
import random
from models.robot import Robot
from models.endpoint import Endpoint
from models.chat import Chat
import re
import socket
# Ejemplo para correr programa

#                             python mix.py 127.0.0.1:19999# rojo cuad

# Validación de argumentos de entrada
valid_colors = ['rojo', 'azul', 'verde']
valid_figures = ['cuad', 'triang', 'circ']
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
    figura = str(sys.argv[3])
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
client_id = vrep.simxStart(str(ip), int(port), True, True, 5000, 5)
print('Client ID: ', client_id)

if client_id != -1:
    print('Conexión exitosa!')
else:
    sys.exit('Error!')

win_name = "{}({}-{})".format(random.randint(1, 300), color, figura)

var1 = color
var2 = figura
print('ip: {}   port: {}   robot_id: {}   color: {}   figura: {}'.format(ip, port, sufix or 'padre', color, figura))
font = cv2.FONT_HERSHEY_SIMPLEX
redc = (0,0,255)
bluec = (255,0,0)
greenc = (0,255,0)
colorf = (0,110,0)

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

def triang(x, y, area):
    areas.append({'name': 'Triangulo', 'area': area, 'center': {'x': x, 'y': y} })
    cv2.putText(img, 'Triangulo', (x,y), font, 1, (0,110,0), 2)

def cuadr(x, y, area):
    areas.append({'name': 'Cuadrado', 'area': area, 'center': {'x': x, 'y': y} })
    cv2.putText(img, 'Rectangulo', (x,y), font, 1, (0,110,0), 2)

def circ(x, y, area):
    areas.append({'name': 'Circulo', 'area': area, 'center': {'x': x, 'y': y} })
    cv2.putText(img, 'Circulo', (x,y), font, 1, (0,110,0), 2)

def draw(name, mask, color):
    contours,_ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    for cont in contours:
        area = cv2.contourArea(cont)
        approx = cv2.approxPolyDP(cont, 0.01* cv2.arcLength(cont,True), True)
        x = approx.ravel()[0]
        y = approx.ravel()[1]
        if area > 50:
            mnt = cv2.moments(approx)
            if (mnt["m00"]==0): mnt["m00"]=1
            x = int(mnt["m10"]/mnt["m00"])
            y = int(mnt['m01']/mnt['m00'])
            newContour = cv2.convexHull(approx)
            cv2.drawContours(img, [newContour], 0, color, 3)
            #cv2.circle(img,(x,y),7,(0,255,0),-1)
            if var1 == 'rojo':
                rojo(x, y, newContour, area)
            elif var1 == 'azul':
                azul(x, y, newContour, area)
            elif var1 == 'verde':
                verde(x, y, newContour, area)
            else:
                continue

def rojo(x, y, newContour, area):
    cv2.drawContours(img, [newContour], 0, redc, 3)
    #put_center(x, y, redc)
    if var2 == 'triang':
        if len(newContour) == 3:
            triang(x, y, area)
    elif var2 == 'cuad':
        if len(newContour) >= 4 and len(newContour) <= 6:
            cuadr(x, y, area)
    elif var2 == 'circ':
        if 10 < len(newContour):
            circ(x, y, area)
    else:
        print('Figura no valida')

def azul(x, y, newContour, area):
    cv2.drawContours(img, [newContour], 0, bluec, 3)
    #put_center(x, y, bluec)
    if var2 == 'triang':
        if len(newContour) == 3:
            triang(x, y, area)
    elif var2 == 'cuad':
        if len(newContour) >= 4 and len(newContour) <= 6:
            cuadr(x, y, area)
    elif var2 == 'circ':
        if 10 < len(newContour):
            circ(x, y, area)
    else:
        print('Figura no valida')

def verde(x, y, newContour, area):
    cv2.drawContours(img, [newContour], 0, bluec, 3)
    if var2 == 'triang':
        if len(newContour) == 3:
            triang(x, y, area)
    elif var2 == 'cuad':
        if len(newContour) >= 4 and len(newContour) <= 6:
            cuadr(x, y, area)
    elif var2 == 'circ':
        if 10 < len(newContour):
            circ(x, y, area)
    else:
        print('Figura no valida')
    
def put_center(x, y, color):
    cv2.circle(img,(x,y), 7, color,-1)
    cv2.putText(img,'{},{}'.format(x,y), (x+10,y), font, 0.75, (0,255,0), 1, cv2.LINE_AA)

socket_host = '127.0.0.1'
socket_port = 6000
chat = Chat(socket_host, socket_port)
id_roboto = str(robot.handle)
try:
    if figura=='cuad':
        fig = 'cubo'
    elif figura == 'triang':
        fig = 'piramide'
    else:
        fig = 'esfera'
    msg = ' recogere color ' + color + ' y figura ' + fig
    response = chat.send_message("#"+id_roboto)
    print(response)
    response = chat.send_message('Soy el robot '+ id_roboto + msg+' !')
    print(response)
except Exception as error:
    print(error)
    pass

while True:

    img = robot.read_camera()
    #
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    maskBlue = cv2.inRange(hsv, lightblue, darkblue)
    maskRed1 = cv2.inRange(hsv, lightred1, darkred1)
    maskRed2 = cv2.inRange(hsv, lightred2, darkred2)
    maskRed = cv2.add(maskRed1, maskRed2)
    maskGreen = cv2.inRange(hsv, lightgreen, darkgreen)

    if var1 == 'azul':
        draw('blue', maskBlue, (255,0,0))
    elif var1 == 'verde':
        draw('green', maskGreen, (0,255,0))
    elif var1 == 'rojo':
        draw('red', maskRed, (0,0,255))
    else:
        print('Figura no valida')
        break
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
            robot.interpolation(hsv, target["area"] ,target["center"]["x"], target["center"]["y"], (var2=='circ'))
        else:
            robot.tork_rotation=TORK_ROTATE_FAST
            robot.move_right()
    else:
        if robot.go_to_endpoint(endpoints):
            try:
                response = chat.send_message("#"+id_roboto+" listo")
            except:
                pass
    areas = []

    cv2.imshow(win_name, img)
    key = cv2.waitKey(1)
    robot.move_stop()
    
    if key == 27:
        cv2.destroyAllWindows()
        exit()
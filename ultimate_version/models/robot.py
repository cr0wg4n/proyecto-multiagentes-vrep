import time
import numpy as np
import cv2
import math 
import random
from models.endpoint import Endpoint

class Robot:
    def __init__(self, vrep, client_id, name, name_motor_left, name_motor_right, name_camera, name_prox_sensor, name_payload, velocity=40, velocity_rotation=30, tork=30, tork_rotation=7, error=3):
        self.client_id = client_id
        self.velocity = velocity
        self.velocity_rotation = velocity_rotation
        self.tork = tork
        self.tork_rotation = tork_rotation
        self.error = error
        self.name = name
        self.name_prox_sensor = name_prox_sensor
        self.name_payload = name_payload
        self.figure_handle = None
        _, self.handle = vrep.simxGetObjectHandle(client_id, name, vrep.simx_opmode_oneshot_wait)
        _, self.payload_handle = vrep.simxGetObjectHandle(client_id, name_payload, vrep.simx_opmode_oneshot_wait)
        _, self.left_motor_handle = vrep.simxGetObjectHandle(client_id, name_motor_left, vrep.simx_opmode_oneshot_wait)
        _, self.right_motor_handle = vrep.simxGetObjectHandle(client_id, name_motor_right, vrep.simx_opmode_oneshot_wait)
        _, self.cam_handle = vrep.simxGetObjectHandle(client_id, name_camera, vrep.simx_opmode_oneshot_wait)
        _, resolution, image = vrep.simxGetVisionSensorImage(client_id, self.cam_handle, 0, vrep.simx_opmode_streaming)
        time.sleep(1)
        self.vrep = vrep
        self.searching = True


    def move_left(self):
        for i in range(self.tork_rotation):
            self.vrep.simxSetJointTargetVelocity(self.client_id, self.left_motor_handle, -self.velocity_rotation, self.vrep.simx_opmode_streaming)
            self.vrep.simxSetJointTargetVelocity(self.client_id, self.right_motor_handle, self.velocity_rotation, self.vrep.simx_opmode_streaming)
            time.sleep(0.0001)

    def move_right(self):
        for i in range(self.tork_rotation):
            self.vrep.simxSetJointTargetVelocity(self.client_id, self.left_motor_handle, self.velocity_rotation, self.vrep.simx_opmode_streaming)
            self.vrep.simxSetJointTargetVelocity(self.client_id, self.right_motor_handle, -self.velocity_rotation, self.vrep.simx_opmode_streaming)
            time.sleep(0.0001)

    def move_up(self):
        for i in range(self.tork):
            self.vrep.simxSetJointTargetVelocity(self.client_id, self.left_motor_handle, -self.velocity, self.vrep.simx_opmode_streaming)
            self.vrep.simxSetJointTargetVelocity(self.client_id, self.right_motor_handle, -self.velocity, self.vrep.simx_opmode_streaming)
            time.sleep(0.00015)

    def move_down(self):
        for i in range(int(self.tork/2)):
            self.vrep.simxSetJointTargetVelocity(self.client_id, self.left_motor_handle, self.velocity, self.vrep.simx_opmode_streaming)
            self.vrep.simxSetJointTargetVelocity(self.client_id, self.right_motor_handle, self.velocity, self.vrep.simx_opmode_streaming)
            time.sleep(0.00015)

    def move_stop(self):
        if random.randint(0,1) == 1: 
            self.vrep.simxSetJointTargetVelocity(self.client_id, self.left_motor_handle, 0, self.vrep.simx_opmode_streaming)
            self.vrep.simxSetJointTargetVelocity(self.client_id, self.right_motor_handle, 0, self.vrep.simx_opmode_streaming)
        else:
            
            self.vrep.simxSetJointTargetVelocity(self.client_id, self.right_motor_handle, 0, self.vrep.simx_opmode_streaming)
            self.vrep.simxSetJointTargetVelocity(self.client_id, self.left_motor_handle, 0, self.vrep.simx_opmode_streaming)

    def position(self, target=-1):
        _, pos = self.vrep.simxGetObjectPosition(self.client_id, self.handle, target, self.vrep.simx_opmode_oneshot_wait)
        return pos

    def rotationQ(self, target=-1):
        _, rot = self.vrep.simxGetObjectQuaternion(self.client_id, self.handle, target, self.vrep.simx_opmode_oneshot_wait)
        return rot

    def rotation(self, target=-1):
        res = []
        _, rot = self.vrep.simxGetObjectOrientation(self.client_id, self.handle, target, self.vrep.simx_opmode_oneshot_wait)
        for r in rot:
            if r * (180/math.pi) < 0:
                res.append(r * (180/math.pi) + 360)
            else:
                res.append(r * (180/math.pi))
        return res

    def payload_position(self, target=-1):
        _, pos = self.vrep.simxGetObjectPosition(self.client_id, self.payload_handle, target, self.vrep.simx_opmode_oneshot_wait)
        return pos

    def get_generic_position(self, handle, target=-1):
        _, pos = self.vrep.simxGetObjectPosition(self.client_id, handle, target, self.vrep.simx_opmode_oneshot_wait)
        return pos

    def value_rotation_to(self, target):
        me = self.position()
        radians = math.atan2(target[1] - me[1], target[0] - me[0])
        return math.degrees(radians) + 180


    def read_camera(self):
        _, resolution, image = self.vrep.simxGetVisionSensorImage(self.client_id, self.cam_handle, 0, self.vrep.simx_opmode_buffer)
        img = np.array(image, dtype=np.uint8)
        img.resize([resolution[0], resolution[1], 3])
        img = np.rot90(img, 2)
        img = np.fliplr(img)
        img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
        return img
    
    def read_prox_sensor(self):
        _, signal = self.vrep.simxGetFloatSignal(self.client_id, self.name_prox_sensor, self.vrep.simx_opmode_oneshot_wait)
        if signal < 0.40:
            return True
        return False
    
    def read_prox_target(self):
        _, target = self.vrep.simxGetIntegerSignal(self.client_id, "target_"+self.name_prox_sensor, self.vrep.simx_opmode_oneshot_wait)
        return target

    def interpolation(self, img, area, x, y, circle=False):
        width = np.size(img, 1)
        height = np.size(img, 0)
        absolute_center_y = int(height / 2)
        absolute_center_x = int(width / 2)

        delta_x = absolute_center_x - x
        delta_y = absolute_center_y + self.error * 2 - y

        if abs(delta_x) <= self.error * 2:
            delta_x = 0
        
        coeficient = 1
        if circle:
            coeficient = 10
            area = area * 1.2
        if area < ((width - (self.error * coeficient)) * (height - (self.error * coeficient))):
            if delta_x > 0:
                self.move_left()
            elif delta_x < 0:
                self.move_right()
            self.move_up()
            # if delta_y > 0:
            #     self.move_up()
            # else:
            #     print('bug')
            return False
        else:
            print('cerca')
            if self.read_prox_sensor():
                self.figure_handle = self.read_prox_target()
                self.vrep.simxSetObjectPosition(self.client_id, self.figure_handle, self.payload_handle, (0,0,0), self.vrep.simx_opmode_oneshot_wait)
                self.searching = False
            return True

    def set_searching_velocity(self):
        self.velocity = 40
        self.velocity_rotation = 28
        self.tork = 33
        self.tork_rotation = 7

    def go_to_point(self, target):
        close_to_me = target.is_close_to_me(self.position())
        rotation = self.value_rotation_to(target.position())
        rotation_y = self.rotation()[2]
        delta_rotation = rotation - rotation_y
        self.tork_rotation = 100
        self.velocity_rotation = 100
        self.tork = 250
        self.velocity = 230
        if not close_to_me:
            # self.move_up()
            if abs(delta_rotation) > self.error * 2:
                if delta_rotation < 0:
                    self.move_right()
                else:
                    self.move_left()
            else:
                self.move_up()
        else:
            return True
        self.move_stop()
        return False

    def go_to_endpoint(self, endpoints):
        endpoint_target = None
        aux = 1000 
        for endpoint in endpoints:
            endpoint_obj = Endpoint(self.vrep, self.client_id, endpoint)
            distante = endpoint_obj.distance_between_points(self.position())
            if  distante < aux:
                aux = distante
                endpoint_target = endpoint_obj
        print(endpoint_target.name)
        if self.go_to_point(endpoint_target):
            x = random.random() / 8
            y = random.random() / 8
            self.vrep.simxSetObjectPosition(self.client_id, self.figure_handle, endpoint_target.handle, (x, y, 1), self.vrep.simx_opmode_oneshot_wait)
            self.figure_handle = None
            self.set_searching_velocity()
            self.searching = True
            print("ya llegue")
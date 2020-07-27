
import math
class Endpoint():
    def __init__(self, vrep, client_id, name):
        self.client_id = client_id
        self.name = name
        _, self.handle = vrep.simxGetObjectHandle(self.client_id, name, vrep.simx_opmode_oneshot_wait)
        self.vrep = vrep
        self.distance = 0

    def position(self, target=-1):
        _, pos = self.vrep.simxGetObjectPosition(self.client_id, self.handle, target, self.vrep.simx_opmode_oneshot_wait)
        return pos

    def rotation(self, target=-1):
        _, rot = self.vrep.simxGetObjectOrientation(self.client_id, self.handle, target, self.vrep.simx_opmode_oneshot_wait)
        return rot

    def rotationQ(self, target=-1):
        _, rot = self.vrep.simxGetObjectQuaternion(self.client_id, self.handle, target, self.vrep.simx_opmode_oneshot_wait)
        return rot
        
    def distance_between_points(self, target):
        a = self.position()
        self.distance = math.sqrt(math.pow((target[0]-a[0]), 2) + math.pow((target[1]-a[1]), 2))
        return self.distance
    
    def is_close_to_me(self, target):
        if self.distance_between_points(target) <= 1.3:
            return True
        return False


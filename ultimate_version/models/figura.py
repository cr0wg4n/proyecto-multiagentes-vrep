import math

class Figure():
    def __init__(self, client_id, vrep, name, figure=None, color=None):
        _, self.handle = vrep.simxGetObjectHandle(client_id, name, vrep.simx_opmode_oneshot_wait)
        self.client_id = client_id
        self.vrep = vrep
        self.name = name
        self.figure = figure
        self.color = color
        self.pos = None

    def position(self, target=-1):
        _, pos = self.vrep.simxGetObjectPosition(self.client_id, self.handle, target, self.vrep.simx_opmode_oneshot_wait)
        self.pos = pos
        return pos

    def distance_between_points(self, target):
        a = self.position()
        self.distance = math.sqrt(math.pow((target[0]-a[0]), 2) + math.pow((target[1]-a[1]), 2))
        return self.distance
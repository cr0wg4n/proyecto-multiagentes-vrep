import socket
import vrep
import re
from models.figura import Figure
import sys

port1 = 6000

vrep.simxFinish(-1)
client_id = vrep.simxStart('127.0.0.1', 19998, True, True, 5000, 1)
print('Client ID: ', client_id)

if client_id != -1:
    print('Conexión exitosa!')
else:
    sys.exit('Error!')

object_names = ["Pyramid", "Shakesphere", "Cube", "Pioneer_p3dx"]

objects = {
   "Pyramid": [],
   "Shakesphere": [],
   "Cube": [],
   "Pioneer_p3dx": [],
}

def update_db():
   # mapping 
   for figure in object_names:
      counter = 0
      figure_object = Figure(client_id, vrep, figure)
      objects[figure].append(figure_object) 
      while True:
         figure_object = Figure(client_id, vrep, figure+"#{}".format(counter))
         if figure_object.handle != 0:
            objects[figure].append(figure_object)
         else: 
            break
         counter+=1

def get_all_objects():
   res = []
   for _object in object_names:
      for obj in objects[_object]:
         res.append(obj)
   return res

def is_id_message(msg):
   r = re.match(r'^\#(\d+)', msg)
   if bool(r):
      return int(r.groups()[0])
   return None

def add_non_repeat_list(lst, item):
   if not item in lst:
      lst.append(item)
      job_status["robot_{}".format(item)] = {
         "figures": 0
      }
   return lst

def robot_done_job(msg):
   r = re.match(r'^\#(\d+)\s?listo', msg)
   if bool(r):
      _id = int(r.groups()[0])
      if not _id in lista_robots:
         add_non_repeat_list(lista_robots, _id)
      job_status["robot_{}".format(_id)]["figures"]+= 1
      return True 
   return None


# all objects
s = socket.socket()          
print ("Servidor iniciado")
s.bind(('', port1))         
print ("Puerto del servidor %s" %(port1))
s.listen(5)      
print ("Servidor escuchando..")

lista_robots = []
job_status = {}
update_db()
while True: 
   # update_db()
   c, addr = s.accept()      
   print ('Robot conectado', addr)
   client_message = c.recv(1024).decode('utf-8')
   if is_id_message(client_message):
      get_all_objects()
      add_non_repeat_list(lista_robots, is_id_message(client_message))
      robot_done_job(client_message)

   print(client_message,'\n')
   print(job_status)
   # print(lista_robots)
   message_to_client = 'Identifiquese robot!'
   c.sendall(message_to_client.encode())
   c.close()
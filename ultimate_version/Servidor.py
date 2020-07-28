import socket

# port for our server.
port1 = 6000

# We create a socket object for the server.
s = socket.socket()          
print ("Servidor iniciado")
  
# The server listen the requests from other computers on the network.
s.bind(('', port1))         
print ("Puerto del servidor %s" %(port1))
  
# put the socket into listening mode.
s.listen(5)      
print ("Servidor escuchando..")
lista_robot = []
while True: 
  
   # Wait for connection with a client. 
   c, addr = s.accept()      
   print ('Robot conectado', addr)
   
   # Read the message from the client.
   print (c.recv(1024))
   lista_robot.append(c)
   # send a message to the client.  
   c.sendall(b'Identifiquese robot!')
  
   # Close the socket (connection with the client)
   c.close()
   print("Robot desconectado")
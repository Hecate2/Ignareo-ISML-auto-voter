import zmq
import time
import sys
from  multiprocessing import Process
 
def server(port="5556"):
	context = zmq.Context()
	socket = context.socket(zmq.REP)
	socket.bind("tcp://*:%s" % port)
	print ("Running server on port: ", port)
	# serves only 5 request and dies
	for reqnum in range(5):
		# Wait for next request from client
		message = socket.recv()
		print ("Received request #%s: %s" % (reqnum, message))
		socket.send( ("World from %s" % port).encode("ascii") )
         
def client(ports=["5556"]):
	context = zmq.Context()
	print ("Connecting to server with ports %s" % ports)
	socket = context.socket(zmq.REQ)
	for port in ports:
		socket.connect ("tcp://localhost:%s" % port)
	for request in range (20):
		print ("Sending request", request,"...")
		socket.send ("Hello".encode("ascii"))
		message = socket.recv()
		print ("Received reply ", request, "[", message, "]")
		time.sleep (1) 
 
 
if __name__ == "__main__":
	# Now we can run a few servers 
	server_ports = range(5550,5558,2)
	for server_port in server_ports:
		Process(target=server, args=(server_port,)).start()
        
	# Now we can connect a client to all these servers
	Process(target=client, args=(server_ports,)).start()


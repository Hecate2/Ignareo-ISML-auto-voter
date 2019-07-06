import zmq,time
from base64 import b64encode

def client(ports=["5555"]):
    context = zmq.Context()
    print ("Connecting to server with ports %s" % ports)
    socket = context.socket(zmq.REQ)
    for port in ports:
        socket.connect ("tcp://localhost:%s" % port)
        
    count=5000
    f=open(r'1A4YFD81.jpg','rb')
    img=b64encode(f.read())
    time_start=time.time()
    for request in range (count):
        #print ("Sending request", request,"...")
        socket.send (img)
        message = socket.recv()
        #print ("Received reply ", request, "[", message, "]")
        #time.sleep (1)
    print(count,'images in',time.time()-time_start,'seconds')

if __name__ == "__main__":
    client()

import zmq,time
from io import BytesIO
from base64 import b64encode


def client(ports=["5556"]):
    context = zmq.Context()
    print ("Connecting to server with ports %s" % ports)
    sockets = [context.socket(zmq.REQ) for port in ports]
    length=len(sockets)
    for i in range(length):
        sockets[i].connect ("tcp://localhost:%s" % ports[i])
        
    count=102
    #count=12
    count0=0
    f=open(r'1A4YFD81.jpg','rb')
    img=b64encode(f.read())
    f.close()
    time_start=time.time()
    while count0<count:
        for i in range(length):
            #print ("Sending request", request,"...")
            sockets[i].send (img)
            #print(message)
            #print ("Received reply ", request, "[", message, "]")
            #time.sleep (1)
        count0=count0+length
        #time.sleep(1)
        for i in range(length):
            message = sockets[i].recv()
            #print(message)

    print(count0,'images in',time.time()-time_start,'seconds')

if __name__ == "__main__":
    client(range(5551,5554,1))

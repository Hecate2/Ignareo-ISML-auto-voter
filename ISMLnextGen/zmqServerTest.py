import zmq

def server(port="5555"):
    context = zmq.Context()
    socket = context.socket(zmq.REP)
    socket.bind("tcp://*:%s" % port)
    print ("Running server on port: ", port)
    # serves only 5 request and dies
    #for reqnum in range(5):
    i=1
    while(1):
        # Wait for next request from client
        message = socket.recv()
        #print ("Received request #%s: %s" % (i, message))
        socket.send( ("Message from %s" % port).encode("ascii") )
        i=i+1

if __name__ == "__main__":
    server()

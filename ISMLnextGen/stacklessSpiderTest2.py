#! python2
#coding:utf-8

import stackless
import stacklesssocket
stacklesssocket.install()

import urllib2
import urllib
import https
import ssl
import json

client_cert_key = "etcd-client-key.pem" # file path
client_cert_pem = "etcd-client.pem"     # file path 
ca_certs = "etcd-ca.pem"                # file path

handlers = []

handlers.append( https.HTTPSClientAuthHandler( 
    key = client_cert_key,
    cert = client_cert_pem,
    ca_certs = ca_certs,
    ssl_version = ssl.PROTOCOL_SSLv23,
    ciphers = 'TLS_RSA_WITH_AES_256_CBC_SHA' ) )

http = urllib2.build_opener(*handlers)

#import requests
import time

def test_urllib2(i):
    print "urllib2 test", i
    #r=urllib2.urlopen('http://www.httpbin.org/get').read()
    r=urllib2.urlopen('https://www.internationalsaimoe.com/').read()
    with open("./tmp.txt",'a') as f:
        f.write(r.encode('utf8'))
    print "finished",i

def test_requests(i):
    print "requests test", i
    r=requests.get('https://www.internationalsaimoe.com/')
    with open("./tmp.txt",'a') as f:
        f.write(r.text.encode(r.encoding))
    print "finished",i

##for i in range(5):
##    stackless.tasklet(test_urllib2)(i)

##for i in range(2):
##    stackless.tasklet(test_requests)(i)

##start=time.time()
##stackless.run()
##print time.time()-start
##r=requests.get('https://www.internationalsaimoe.com/')
##with open("./tmp/tmp.txt",'a') as f:
##    f.write(r.text.encode(r.encoding))
#r=http.open('https://www.internationalsaimoe.com/').read()
req=urllib2.Request(url='https://www.internationalsaimoe.com/')
r=urllib2.urlopen(req)
print r.read()

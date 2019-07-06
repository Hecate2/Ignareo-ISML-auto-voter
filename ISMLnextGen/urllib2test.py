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

# request https
# GET
resp = http.open('https://xxxx:2379/v2/members')
data = resp.read()

# POST
req = urllib2.Request(url)  
data = urllib.urlencode(data)
resp = http.open(req, data)

# PUT
request = urllib2.Request(url, data=json_data)
request.add_header('Content-Type', 'application/json')
request.get_method = lambda: 'PUT'
resp = http.open(request)

# DELETE
request = urllib2.Request(url, data=data)
request.get_method = lambda: 'DELETE'
resp = http.open(request)

resp.close()

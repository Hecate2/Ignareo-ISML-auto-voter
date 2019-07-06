#! python2
#coding:utf-8

import urllib2, httplib, ssl, socket

DEFAULT_HTTP_TIMEOUT = 10 #seconds

# http://code.activestate.com/recipes/577548-https-httplib-client-connection-with-certificate-v/
# http://stackoverflow.com/questions/1875052/using-paired-certificates-with-urllib2

class HTTPSClientAuthHandler(urllib2.HTTPSHandler):
    '''
    Allows sending a client certificate with the HTTPS connection.
    This version also validates the peer (server) certificate since, well...
    WTF IS THE POINT OF SSL IF YOU DON"T AUTHENTICATE THE PERSON YOU"RE TALKING TO!??!
    '''
    def __init__(self, key=None, cert=None, ca_certs=None, ssl_version=None, ciphers=None):
        urllib2.HTTPSHandler.__init__(self)
        self.key = key
        self.cert = cert
        self.ca_certs = ca_certs
        self.ssl_version = ssl_version
        self.ciphers = ciphers

    def https_open(self, req):
        # Rather than pass in a reference to a connection class, we pass in
        # a reference to a function which, for all intents and purposes,
        # will behave as a constructor
        return self.do_open(self.get_connection, req)

    def get_connection(self, host, timeout=DEFAULT_HTTP_TIMEOUT):
        return HTTPSConnection( host, 
                key_file = self.key, 
                cert_file = self.cert,
                timeout = timeout,
                ciphers = self.ciphers,
                ca_certs = self.ca_certs )


class HTTPSConnection(httplib.HTTPSConnection):
    '''
    Overridden to allow peer certificate validation, configuration
    of SSL/ TLS version and cipher selection.  See:
    http://hg.python.org/cpython/file/c1c45755397b/Lib/httplib.py#l1144
    and `ssl.wrap_socket()`
    '''
    def __init__(self, host, **kwargs):
        self.ciphers = kwargs.pop('ciphers',None)
        self.ca_certs = kwargs.pop('ca_certs',None)
        self.ssl_version = kwargs.pop('ssl_version', ssl.PROTOCOL_SSLv23)

        httplib.HTTPSConnection.__init__(self,host,**kwargs)

    def connect(self):
        sock = socket.create_connection( (self.host, self.port), self.timeout )

        if self._tunnel_host:
            self.sock = sock
            self._tunnel()

        self.sock = ssl.wrap_socket( sock, 
                keyfile = self.key_file, 
                certfile = self.cert_file,
                ca_certs = self.ca_certs,
                cert_reqs = ssl.CERT_REQUIRED if self.ca_certs else ssl.CERT_NONE )

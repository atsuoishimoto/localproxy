#!/usr/bin/env python

import urlparse, os, copy
from urllib import unquote
from twisted.web.http import HTTPFactory
from twisted.web.server import Site, NOT_DONE_YET
from twisted.web import resource
from twisted.web.resource import Resource
from twisted.web.static import File
import twisted.internet
import twisted.internet.ssl
from twisted.internet.protocol import Protocol, ClientFactory
from twisted.web.proxy import Proxy, ProxyRequest
from twisted.python.compat import intToBytes


def _split_host(uri):
    # CONNECT method does not send URI, but SERVER:PORT string.
    port = 80
    url = urlparse.urlparse(uri)
    host = url.hostname
    if host:
        if url.port:
            port = int(url.port)
    else:
        if ':' in uri:
            host, port = uri.split(':')
            port = int(port)

    return host, port

class LocalDirs(Resource):
    def __init__(self):
        Resource.__init__(self)

    def getChild(self, path, request):
        host = request.getHeader('Host')
        localpath = os.path.join(os.getcwd(), host)

        url = urlparse.urlparse(request.uri)
        path = os.path.join(localpath, url.path.lstrip('/'))

        if url.query:
            arg = path + '?' + url.query
            if os.path.exists(arg):
                path = arg

        if os.path.isdir(path):
            index = os.path.join(path, 'index.html')
            if os.path.exists(index):
                path = index

        print 'path:', path

        path, last = os.path.split(path)
        ret = File(path).getChild(last, request)
        ret.isLeaf = True
        return ret

class ConnectToClient(Protocol):
    income = None

    def connectionMade(self):
        self.factory.income_request.channel.connected_port = self
        self.factory.income_request.result(200, "CONNECTED")

    def connectionLost(self, reason):
        self.income.transport.loseConnection()

    def dataReceived(self, data):
        self.income.transport.write(data)


class ConnectToClientFactory(ClientFactory):
    protocol = ConnectToClient

    def __init__(self, host, port, request):
        self.income_request = request
        self.host = host
        self.port = port

    def clientConnectionFailed(self, connector, reason):
        self.income_request.result(500, "Connection failed", str(reason))



class LocalFileProxyRequest(ProxyRequest):
    def process(self):
        print 'uri:', self.uri

        host, port = _split_host(self.uri)
        localpath = os.path.join(os.getcwd(), host)

        if self.method != 'CONNECT':
            if os.path.isdir(localpath):
                self.process_local(localpath)
            else:
                ProxyRequest.process(self)
        else:
            if os.path.isdir(localpath):
                self._connect_local()
            else:
                self._connect()

    def _connect(self):
        host, port = _split_host(self.uri)
        clientFactory = ConnectToClientFactory(host, port, self)
        self.reactor.connectTCP(host, port, clientFactory)

    def _connect_local(self):
        clientFactory = ConnectToClientFactory('localhost', 8081, self)
        self.reactor.connectTCP('localhost', 8081, clientFactory)

    def process_local(self, localpath):
        file = LocalDirs().getChild(None, self)
        body = file.render(self)
        if body == NOT_DONE_YET:
            return

        self.setHeader(b'content-length',
                       intToBytes(len(body)))
        self.write(body)
        self.finish()


    def result(self, code, message, body=''):
        self.setResponseCode(code, message)
        self.setHeader('Content-Length', len(body))
        self.write(body)
        self.finish()

class LocalFileProxy(Proxy):
    requestFactory = LocalFileProxyRequest
    connected_port = None

    def requestDone(self, request):
        if request.method != 'CONNECT':
            Proxy.requestDone(self, request)
        else:
            self.connected_port.income = self
            
    def connectionLost(self, reason):
        if self.connected_port:
            self.connected_port.transport.loseConnection()
        Proxy.connectionLost(self, reason)

    def dataReceived(self, data):
        if self.connected_port:
            self.connected_port.transport.write(data)
        else:
            Proxy.dataReceived(self, data)


def main():
    factory = HTTPFactory()
    factory.protocol = LocalFileProxy
    twisted.internet.reactor.listenTCP(8080, factory)

    if os.path.exists('privkey.pem'):
        rsrc = LocalDirs()
        factory = Site(rsrc)
        twisted.internet.reactor.listenSSL(8081, factory, 
            twisted.internet.ssl.DefaultOpenSSLContextFactory(
                'privkey.pem', 'cacert.pem'))

    twisted.internet.reactor.run()


if __name__ == '__main__':
    main()

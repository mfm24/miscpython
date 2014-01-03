# Trying SSL with bottle
# ie combo of http://www.piware.de/2011/01/creating-an-https-server-in-python/
# and http://dgtool.blogspot.com/2011/12/ssl-encryption-in-python-bottle.html
# without cherrypy?
# requires ssl

# to create a server certificate, run eg
# openssl req -new -x509 -keyout server.pem -out server.pem -days 365 -nodes
# DON'T distribute this combined private/public key to clients!
# (see http://www.piware.de/2011/01/creating-an-https-server-in-python/#comment-11380)
from bottle import Bottle, get, run, ServerAdapter

class SSLWSGIRefServer(ServerAdapter):
    def run(self, handler): # pragma: no cover
        from wsgiref.simple_server import make_server, WSGIRequestHandler
        import ssl
        if self.quiet:
            class QuietHandler(WSGIRequestHandler):
                def log_request(*args, **kw): pass
            self.options['handler_class'] = QuietHandler
        srv = make_server(self.host, self.port, handler, **self.options)
        srv.socket = ssl.wrap_socket (srv.socket, certfile='server.pem', server_side=True)
        srv.serve_forever()

@get("/x")
def get_x():
	return "Hi there"

#instead of:
#run(host="0.0.0.0", port=8090)
#we use:
srv = SSLWSGIRefServer(host="0.0.0.0", port=8090)
run(server=srv)
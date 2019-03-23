from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs
from PyQt5.QtCore import QThread
import json

def makeHandlerClass(child):
	class CustomHandler(reqHandler, object):
		def __init__(self, *args, **kwargs):
			self.child = child
			super(CustomHandler, self).__init__(*args, **kwargs)
	return CustomHandler

class reqHandler(BaseHTTPRequestHandler):
	def do_GET(self):
		req = parse_qs(urlparse(self.path).query)
		data = json.loads(req['json'][0])
		self.child.notify(data)
		self.send_response(200)
		self.end_headers()
		return

class httpListener(QThread):
	def __init__(self, port):
		QThread.__init__(self)
		self.observers = set()
		self.port = port

	def run(self):
		handlerclass = makeHandlerClass(self)
		self.httpserver = HTTPServer(('', self.port), handlerclass)
		sa = self.httpserver.socket.getsockname()
		print('Listening on ' + str(sa[0]) + ':' + str(sa[1]))
		self.httpserver.serve_forever()

	def stop(self):
		self.httpserver.shutdown()
		self.httpserver.socket.close()
		self.wait()

	def notify(self, data):
		for obs in self.observers:
			obs.notify(data)
	    
	def attach(self, obs):
		self.observers.add(obs)
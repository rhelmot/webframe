#!/usr/bin/python
import sys, os, re
import BaseHTTPServer

datare = re.compile('/robots.txt|/favicon.ico|/data/(?!ajax)')
forbiddenre = re.compile('/data/(sensitive|template)')
noindexesre = re.compile('/data/(lib|script|sensitive|template)')

def _bare_address_string(self):
    host, port = self.client_address[:2]
    return '%s' % host

BaseHTTPServer.BaseHTTPRequestHandler.address_string = \
        _bare_address_string

class HandlerClass (BaseHTTPServer.BaseHTTPRequestHandler):
	def do_GET(self):
		self.do_request()
		return
	def do_POST(self):
		self.do_request()
		return
	def do_request(self):
		host = self.headers.get('host').split(':')
		hostport = host[1] if len(host) > 1 else '80'
		host = host[0]
		hostkeys = host.split('.')
		while len(hostkeys) > 0:
			if os.path.exists('.'.join(hostkeys) + '/index.py'):
				break
			hostkeys = hostkeys[1:]
		hostpath = '.'.join(hostkeys)
		if forbiddenre.match(self.path) is not None:
			#forbidden something
			msg = '\r\nYou can\'t go here.'
			self.send_response(403)
			self.send_header('Content-length', str(len(msg)))
			self.wfile.write(msg)
			return
		if datare.match(self.path) is not None:
			try:
				reqmed = open(os.path.join(hostpath, self.path[1:])).read()
				self.send_response(200)
				self.send_header('Content-length', str(len(reqmed)))
				import mimetypes
				type = mimetypes.guess_type(self.path)[0]
				if type is None:
					type = 'application/octet-stream'
				self.send_header('Content-type', type)
				self.send_header('Connection', 'Close')		#TODO: why the hell am I hanging on keep-alive connections?
				self.end_headers()
				self.wfile.write(reqmed)
				#print 'successful resource request', self.path
				return
			except IOError as ex:
				if ex.errno == 21 and noindexesre.match(self.path) is None:
					self.basic_response(200, 'Directory indexes! Not actually a thing yet.')
				else:
					self.basic_response(404, '404 Not Found\r\n\r\nThe file you requested does not exist.')
				return
		os.environ['WEBFRAME_SERVER'] = host
		os.environ['SERVER_PORT'] = hostport
		#try:
		import webframe
		reload(webframe)
		webframe.setup(self)
		if not hostpath == '':
			os.chdir(hostpath)
		import index
		reload(index)
		index.main()
		#except Exception as e:
		#	resp = 'Internal server error! Here\'s the deal:\n\n' + e.args[0]+'\n'
		#	for i in e.args[1:]:
		#		resp += i[0] + ':' + str(i[1]) + '\n' + i[3] + '\n'
		#	self.basic_response(500, resp)
		#return
	def basic_response(self, code, msg):
		self.send_response(code)
		self.send_header('Content-length', str(len(msg)))
		self.send_header('Connection', 'Close')
		self.end_headers()
		self.wfile.write(msg)
		return
	

def main():
			
	ServerClass  = BaseHTTPServer.HTTPServer
	Protocol     = "HTTP/1.1"

	if sys.argv[1:]:
		port = int(sys.argv[1])
	else:
		port = 80
	server_address = ('0.0.0.0', port)

	HandlerClass.protocol_version = Protocol
	httpd = ServerClass(server_address, HandlerClass)

	sa = httpd.socket.getsockname()
	print "Serving HTTP on", sa[0], "port", sa[1], "..."
	httpd.serve_forever()

if __name__ == '__main__':
	main()
#!/usr/bin/python
import sys, os, re
import BaseHTTPServer

globalargs = {}

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
		global globalargs
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
				return
			except IOError as ex:
				if ex.errno == 21 and noindexesre.match(self.path) is None:
					self.basic_response(200, 'Directory indexes! Not actually a thing yet.')
				else:
					self.basic_response(404, '404 Not Found\r\n\r\nThe file you requested does not exist.')
				return
		import webframe
		try:
			if globalargs['debug']:
				reload(webframe)
			webframe.setupSwitch((self, host, hostport))
			if hostpath != '':
				if '.' not in sys.path:
					sys.path.append('.')
				os.chdir(hostpath)
			import index
			if globalargs['debug']:
				reload(index)
			index.main()
		except Exception as e:
			resp = 'Internal server error!'
			import traceback
			tb = '\n'.join(traceback.format_exception(*sys.exc_info()))
			print tb
			if globalargs['printerrors']:
				resp += ' Here\'s the deal:\n\n' + tb
				if len(webframe.documentErrors) != 0:
					resp += '\n\nIn addition, webframe accumulated the following errors:\r\n\t\n'
					resp += '\n'.join(webframe.documentErrors)
			self.basic_response(500, resp)
		return
	def basic_response(self, code, msg):
		self.send_response(code)
		self.send_header('Content-length', str(len(msg)))
		self.send_header('Connection', 'Close')
		self.end_headers()
		self.wfile.write(msg)
		return
	

def main(port=80, bindaddr='0.0.0.0', debug=False, printerrors=True, logfile=None, loglevel_stdout=3, loglevel_file=3):
	global globalargs
	globalargs = { 	'port': port,
			'bindaddr': bindaddr,
			'debug': debug,
			'printerrors': printerrors,
			'logfile': logfile,
			'loglevel_stdout': loglevel_stdout,
			'loglevel_file': loglevel_file }
	ServerClass  = BaseHTTPServer.HTTPServer
	Protocol     = "HTTP/1.1"

	server_address = (bindaddr, port)

	HandlerClass.protocol_version = Protocol
	httpd = ServerClass(server_address, HandlerClass)

	sa = httpd.socket.getsockname()
	print "Serving HTTP on", sa[0], "port", sa[1], "..."
	httpd.serve_forever()

log_levels = ['crit','error','warning','access','debug']

def usage():
	print 'Webframe server -- serve webframe sites'
	print 'Usage: python server.py [options]'
	print 'You will need to run as root to bind to a port lower than 1024'
	print ''
	print 'Options:'
	print '	-p, --port <port>			Specify a port for the server to run on (default 80)'
	print '	-b, --bindaddr <address>		Address to bind server on (default all interfaces "0.0.0.0")'
	print '	-d, --debug				Enable debugging output'
	print '	-e, --printerrors			Show users stacktraces on 500 errors instead of generic error page'
	print '	-f, --logfile <file>			Use a file for logging'
	print '	-l, --loglevel_stdout <level>		Change verbosity for logging on stdout'
	print '	-L, --loglevel_file <level>		Change verbosity for logging to log file'
	print '	-h, --help				Print this message and exit'
	print ''
	print 'Log levels:'
	print '	crit				Log only server faults'
	print '	error				Log the above plus runtime errors'
	print '	warning				Log the above plus runtime warnings'
	print '	access				Log the above plus metadata on connections'
	print '	debug				Log the above plus debugging minutia'
	print ''
	print 'NOTICE: None of the logging stuff is implimented at all, hahaha.'

if __name__ == '__main__':
	import getopt
	kwargs = {}
	try:
		(opts, args) = getopt.getopt(sys.argv[1:], 'p:b:def:l:L:h', ['--port=', '--bind=', '--debug', '--printerrors', '--logfile=', '--loglevel_stdout=', '--loglevel_file=', '--help'])
	except getopt.GetoptError as e:
		print e
		usage()
		sys.exit(2)
	for (opt, arg) in opts:
		if opt in ('-h', '--help'):
			usage()
			sys.exit(0)
		if opt in ('-p', '--port'):
			kwargs['port'] = int(arg)
		if opt in ('-b', '--bindaddr'):
			kwargs['bindaddr'] = arg
		if opt in ('-d', '--debug'):
			kwargs['debug'] = True
		if opt in ('-e', '--printerrors'):
			kwargs['printerrors'] = True
		if opt in ('-f', '--logfile'):
			kwargs['logfile'] = arg
		if opt in ('-l', '--loglevel_stdout'):
			if arg in log_levels:
				kwargs['loglevel_stdout'] = log_levels.index(arg)
			else:
				print 'Invalid log level:',arg
				usage()
				sys.exit(2)
		if opt in ('-L', '--loglevel_file'):
			if arg in log_levels:
				kwargs['loglevel_file'] = log_levels.index(arg)
			else:
				print 'Invalid log level:',arg
				usage()
				sys.exit(2)
	main(**kwargs)

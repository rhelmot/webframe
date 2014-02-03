# __init__.py - Initializaion functions for Webframe
#
# Copyright 2014 Andrew Dutcher

import cgi, os, urlparse, urllib

def enableDebug():
	global debugging
	debugging = True
	import cgitb
	cgitb.enable()

def debug(msg):
	global debugMsgs
	debugMsgs += [msg]

def addHeader(key, val):
	global headers
	headers[key] = val

def setTitle(title):
	global documentTitle
	documentTitle = title

def addScript(source):
	global documentScripts
	documentScripts += [source]

def addRawScript(js):
	global rawScript
	rawScript += js + '\n'

def addCss(source):
	global documentCss
	documentCss += [source]

def addContent(content):
	global documentContent
	documentContent += content

def addError(message):
	global documentErrors
	documentErrors += [message]

DEBUGHTML = '''<div id="pyGenDebug" style="
			position: fixed;
			bottom: 20px;
			left: 20px;
			right: 20px;
			height: 20%;
			overflow-y: scroll;
			z-index: 20;
			background-color:#FFFF70;
			color: black;
			border: solid 3px #FFC000; 
			margin: 50px; 
			padding: 50px;" 
		onclick="
			document.getElementById('pyGenDebug').style.display = 'none';">
	Debug data:<br /><br />
	<strong>%s</strong><br /><br />
	Click this box to close it.</div>'''

ERRORHTML = '''<div id="pyGenError" style="
			background-color:pink; 
			color: black; 
			border: solid 3px red; 
			margin: 50px; 
			padding: 50px;" 
		onclick="
			document.getElementById(\pyGenError').style.display = 'none';
			document.getElementById('pyGenDoc').style.display= 'block';">
	The following errors were encountered while rendering this document:<br /><br />
	<strong>%s+</strong><br /><br />
	Click this box to display the (potentially incorrectly) rendered page.</div>
	<div id="pyGenDoc" style="display: none;">'''

def site():
	global documentTitle, documentScripts, rawScript, documentCss, documentContent, documentErrors, headers, debugging, debugMsgs, docroot, responseCode
	addRawScript('var basePath = "' + docroot[:-1] + '";')
	iswebpage = (('Content-type' in headers) and (headers['Content-type'] == 'text/html'))
	if data.connection:
		data.connection.close()
	if iswebpage:
		outdata = '<html><head>'
		outdata += '<title>'+documentTitle+'</title>'
		if not rawScript == '':
			outdata += '<script>\n' + rawScript + '</script>'
		outdata += ''.join(['<script src="'+a+'"></script>\n' for a in documentScripts])
		outdata += ''.join(['<link rel="stylesheet" type="text/css" href="'+a+'" />' for a in documentCss])
		outdata += '</head>\n<body>'
		if debugging and len(debugMsgs) != 0:
			outdata += DEBUGHTML % '<br />'.join(debugMsgs)
		if len(documentErrors) != 0:
			outdata += ERRORHTML % '<br />'.join(documentErrors)
		outdata += documentContent
		if len(documentErrors) != 0:
			outdata += '</div>'
		outdata += '</body>\n</html>'
	else:
		outdata = documentContent
	addHeader('Content-length', len(outdata))
	if wserv:
		addHeader('Connection', 'Close')
		wserv.send_response(int(responseCode))
		for key, val in headers.iteritems():
			wserv.send_header(key, val)
		wserv.end_headers()
	else:
		print 'Status: ' + str(responseCode)
		print ''.join([key + ': ' + str(headers[key]) + '\n' for key in headers.keys()])
	if not iswebpage:
		if wserv:
			wserv.wfile.write(documentContent)
		else:
			print documentContent
		return
	if wserv:
		wserv.wfile.write(outdata)
	else:
		print outdata


import data, cookie, auth, util

def setupSwitch(sdata=None):
	global wserv
	wserv = None
	if sdata is not None:
		wserv, host, port = sdata
		environ={
			'QUERY_STRING': urlparse.urlparse(wserv.path).query, 
			'REQUEST_METHOD': wserv.command, 
			'CONTENT_TYPE' if 'Content-Type' in wserv.headers else 'blagralkdfs': wserv.headers.get('Content-Type') if 'Content-Type' in wserv.headers else ''
		}
		form = cgi.FieldStorage(fp=wserv.rfile, headers=wserv.headers if wserv.command == 'POST' else None, environ=environ, keep_blank_values=1)
		if 'cookie' not in wserv.headers:
			wserv.headers['cookie'] = ''
		setup(host, wserv.path, port, wserv.command, wserv.client_address[0], form, wserv.headers['cookie'], )
	elif 'GATEWAY_INTERFACE' in os.environ:
		host = os.environ['SERVER_NAME']
		path = (os.environ['REDIRECT_URL'] if 'REDIRECT_URL' in os.environ else os.environ['REQUEST_URI'] if 'REQUEST_URI' in os.environ else '')[1:]
		form = cgi.FieldStorage(keep_blank_values=1)
		if not 'HTTP_COOKIE' in os.environ:
			os.environ['HTTP_COOKIE'] = ''
		setup(host, path, os.environ['SERVER_PORT'], os.environ['REQUEST_METHOD'], os.environ['REMOTE_ADDR'], form, os.environ['HTTP_COOKIE'])
	else:
		setup()

def setup(host='localhost', path='/', port=80, rmethod='GET', remoteaddr=None, rform=None, cookiestring=''):
	global hostname, pathkeys, docroot, form, params, debugging, debugMsgs, permission, documentTitle, documentScripts, rawScript, documentCss, documentContent, documentErrors, headers, responseCode, method, remoteAddress
	debugging = False
	debugMsgs = []

	permission = False
	documentTitle = 'Untitled Document'
	documentScripts = []
	rawScript = ''
	documentCss = []
	documentContent = ''
	documentErrors = []
	headers = {}
	
	responseCode = '200'
	headers['Content-type'] = 'text/plain;charset=utf-8'
	form = {}
	params = {}
	
	hostname = host
	method = rmethod
	remoteAddress = remoteaddr
	if hostname.startswith('dev.'):
		enableDebug()
	pathkeys = map(urllib.unquote_plus, path.split('?',1)[0].split('/'))
	while len(pathkeys) > 0 and pathkeys[0] == '':
		pathkeys = pathkeys[1:]
	while len(pathkeys) > 0 and pathkeys[-1] == '':
		pathkeys = pathkeys[:-1]
	docroot = 'http://' + hostname
	if int(port) != 80:
		docroot += ':' + str(port)
	docroot += '/'
	if rform is not None:
		form = rform
		params = {a: urllib.unquote(form[a].value) for a in form.keys() if not form[a].filename}
	if cookiestring != '':
		cookie.init(cookiestring)

setupSwitch()

###DEPRECATED FUNCTIONS

def template(*args):
	debug('Deprecation warning: use webframe.util.template instead of webframe.template')
	return util.template(*args)

def checkKeys(*args):
	debug('Deprecation warning: use webframe.util.checkKeys instead of webframe.checkKeys')
	return util.checkKeys(*args)

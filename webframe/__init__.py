import cgi, os, urlparse




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
		#debugging = True;
		if debugging and len(debugMsgs) != 0:
			outdata += '<div id="pyGenDebug" style="position: fixed; bottom: 20px; left: 20px; right: 20px; height: 20%; overflow-y: scroll; z-index: 20; background-color:#FFFF70; color: black; border: solid 3px #FFC000; margin: 50px; padding: 50px;" onclick="document.getElementById(\'pyGenDebug\').style.display = \'none\';">Debug data:<br /><br /><strong>'+'<br />'.join(debugMsgs)+'</strong><br /><br />Click this box to close it.</div>'
		if len(documentErrors) != 0:
			outdata += '<div id="pyGenError" style="background-color:pink; color: black; border: solid 3px red; margin: 50px; padding: 50px;" onclick="document.getElementById(\'pyGenError\').style.display = \'none\'; document.getElementById(\'pyGenDoc\').style.display= \'block\';">The following errors were encountered while rendering this document:<br /><br /><strong>'+'<br />'.join(documentErrors)+'</strong><br /><br />Click this box to display the (potentially incorrectly) rendered page.</div><div id="pyGenDoc" style="display: none;">'
		outdata += documentContent
		if len(documentErrors) != 0:
			outdata += '</div>'
		outdata += '</body>\n</html>'
	else:
		outdata = documentContent
	addHeader('Content-length', len(outdata))
	addHeader('Connection', 'Close')
	if wserv:
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

def setup(instance=None):
	import urllib
	global hostname, pathkeys, docroot, form, params, debugging, debugMsgs, permission, documentTitle, documentScripts, rawScript, documentCss, documentContent, documentErrors, headers, responseCode, wserv
	
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

	docroot = '/'
	pathkeys = []
	hostname = 'localhost'

	responseCode = '200'
	headers['Content-type'] = 'text/plain;charset=utf-8'
	wserv = False
	if instance is not None and 'WEBFRAME_SERVER' in os.environ:
		wserv = instance
		hostname = os.environ['WEBFRAME_SERVER']
		if len(hostname) > 4 and hostname[:4] == 'dev.':
			enableDebug()
		ppath = urlparse.urlparse(instance.path)
		pathkeys = ppath.path.split('/')[1:]
		if pathkeys[-1] == '':
			pathkeys = pathkeys[:-1]
		pathkeys = map(urllib.unquote_plus, pathkeys)
		docroot = 'http://' + hostname
		if os.environ['SERVER_PORT'] != '80':
			docroot += ':' + os.environ['SERVER_PORT']
		docroot += '/'
		environ={'QUERY_STRING': ppath.query, 'REQUEST_METHOD':instance.command, 'CONTENT_TYPE' if 'Content-Type' in instance.headers else 'blagralkdfs':instance.headers.get('Content-Type') if 'Content-Type' in instance.headers else ''}
		form = cgi.FieldStorage(fp=instance.rfile, headers=instance.headers if instance.command == 'POST' else None, environ=environ, keep_blank_values=1)
		params = form
		print params
		params = {a: urllib.unquote(form[a].value) for a in form.keys() if not form[a].filename}
		print params
		if 'cookie' in instance.headers:
			os.environ['HTTP_COOKIE'] = instance.headers['cookie']
			cookie.reload()
	elif 'SERVER_NAME' in os.environ:
		hostname = os.environ['SERVER_NAME']
		if len(hostname) > 4 and hostname[:4] == 'dev.':
			enableDebug()
		pathkeys = (os.environ['REDIRECT_URL'] if 'REDIRECT_URL' in os.environ else os.environ['REQUEST_URI'] if 'REQUEST_URI' in os.environ else '')[1:]
		pathkeys = urllib.unquote_plus(pathkeys)
		pathkeys = pathkeys.split('?', 1)[0].split('/')
		if pathkeys[-1] == '':
			pathkeys = pathkeys[:-1]
		docroot = 'http://' + hostname
		if os.environ['SERVER_PORT'] != '80':
			docroot += ':' + os.environ['SERVER_PORT']
		docroot += '/'
		form = cgi.FieldStorage(keep_blank_values=1)
		params = {a: form[a].value for a in form.keys() if not form[a].filename}

setup()

###DEPRECATED FUNCTIONS

def template(*args):
	debug('Deprecation warning: use webframe.util.template instead of webframe.template')
	return util.template(*args)

def checkKeys(*args):
	debug('Deprecation warning: use webframe.util.checkKeys instead of webframe.checkKeys')
	return util.checkKeys(*args)

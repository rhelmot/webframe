debugging = False
debugMsgs = []

documentTitle = 'Untitled Document'
documentScripts = []
rawScript = ''
documentCss = []
documentContent = ''
documentErrors = []
headers = {}
responseCode = '200'

headers['Content-type'] = 'text/plain;charset=utf-8'

import data, cookie, auth, cgi, os
form = cgi.FieldStorage(keep_blank_values=1)
params = {a: form[a].value for a in form.keys()}
if 'SERVER_NAME' in os.environ:
	pathkeys = (os.environ['REDIRECT_URL'] if 'REDIRECT_URL' in os.environ else os.environ['REQUEST_URI'] if 'REQUEST_URI' in os.environ else '')[1:]
	pathkeys = pathkeys.split('?', 1)[0].split('/')
	if pathkeys[-1] == '':
		pathkeys = pathkeys[:-1]
	docroot = 'http://' + os.environ['SERVER_NAME']
	if os.environ['SERVER_PORT'] != '80':
		docroot += ':' + os.environ['SERVER_PORT']
	docroot += '/'
else:
	docroot = '/'
	pathkeys = []
permission = False


def checkKeys(item, *args):
	try:
		for i in args:
			item[i]
	except:
		return False
	return True


def enableDebug():
	global debugging
	debugging = True
	import cgitb
	cgitb.enable()

def debug(msg):
	global debugMsgs
	debugMsgs += [msg]

templateCache = {}

def template(file, vars, cache=False):
	global templateCache
	if cache and file in templateCache:
		buf = templateCache[file]
	else:
		buf = file if '{{' in file else open(file).read()
		if cache:
			templateCache['file'] = buf
	for var, val in vars.iteritems():
		buf = buf.replace('{{' + str(var) + '}}', str(val))
	ifstat = False
	def stripTag(buf, startindex, conditionMet):
		if conditionMet:
			buf = buf[:startindex] + buf[buf.index('}}', startindex)+2:]
		else:
			buf = buf[:startindex] + buf[buf.index('{{', startindex+2):]
		return buf
	def meetCond(cstring):
		cond = cstring.split('=', 1)
		return not ((not cond[0] in vars) or (len(cond) == 1 and (vars[cond[0]] == False or vars[cond[0]] == '')) or (len(cond) == 2 and not str(vars[cond[0]]) == cond[1]))
	while '{{~' in buf:
		perp = buf.index('{{~')
		direc = perp + 3
		endirec = buf.index('}}')
		if buf[direc:direc+3] == 'if ':
			if meetCond(buf[direc+3:endirec]):
				ifstat = False
				buf = stripTag(buf, perp, True)
			else:
				ifstat = True
				buf = stripTag(buf, perp, False)
		elif buf[direc:direc+5] == 'elif ':
			if ifstat:
				if meetCond(buf[direc+5:endirec]):
					ifstat = False
					buf = stripTag(buf, perp, True)
				else:
					ifstat = True
					buf = stripTag(buf, perp, False)
			else:
				buf = stripTag(buf, perp, False)
		elif buf[direc:direc+4] == 'else':
			if ifstat:
				buf = stripTag(buf, perp, True)
				ifstat = False
			else:
				buf = stripTag(buf, perp, False)
		elif buf[direc:direc+5] == 'endif':
			buf = stripTag(buf, perp, True)
	return buf

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
	#debug(str(cookie.cookies))
	if data.connection:
		data.connection.close()
	#headers['Content-length'] = len(documentContent)
	print 'Status: ' + responseCode
	print ''.join([key + ': ' + str(headers[key]) + '\n' for key in headers.keys()])
	if not iswebpage:
		print documentContent
		return
	print '<html><head>'
	print '<title>'+documentTitle+'</title>'
	if not rawScript == '':
		print '<script>\n' + rawScript + '</script>'
	print ''.join(['<script src="'+a+'"></script>\n' for a in documentScripts])
	print ''.join(['<link rel="stylesheet" type="text/css" href="'+a+'" />' for a in documentCss])
	print '</head>\n<body>'
	#debugging = True;
	if debugging and len(debugMsgs) != 0:
		print '<div id="pyGenDebug" style="position: fixed; bottom: 20px; left: 20px; right: 20px; height: 20%; overflow-y: scroll; z-index: 20; background-color:#FFFF70; color: black; border: solid 3px #FFC000; margin: 50px; padding: 50px;" onclick="document.getElementById(\'pyGenDebug\').style.display = \'none\';">Debug data:<br /><br /><strong>'+'<br />'.join(debugMsgs)+'</strong><br /><br />Click this box to close it.</div>'
	if len(documentErrors) != 0:
		print '<div id="pyGenError" style="background-color:pink; color: black; border: solid 3px red; margin: 50px; padding: 50px;" onclick="document.getElementById(\'pyGenError\').style.display = \'none\'; document.getElementById(\'pyGenDoc\').style.display= \'block\';">The following errors were encountered while rendering this document:<br /><br /><strong>'+'<br />'.join(documentErrors)+'</strong><br /><br />Click this box to display the (potentially incorrectly) rendered page.</div><div id="pyGenDoc" style="display: none;">'
	print documentContent
	if len(documentErrors) != 0:
		print '</div>'
	print '</body>\n</html>'

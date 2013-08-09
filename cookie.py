# cookies. why did it have to be cookies.
# Wdy, DD-Mon-YYYY HH:MM:SS GMT ==> strftime('%a, %d-%b-%Y %H:%M:%S GMT')

import urllib, os, datetime
cookies = {}
if 'HTTP_COOKIE' in os.environ:
	cookies = {urllib.unquote_plus(item.split('=', 1)[0]): urllib.unquote_plus(item.split('=', 1)[1]) for item in os.environ['HTTP_COOKIE'].split('; ')}

def setCookie(name, value, expires=False, path='/', domain=False, comment=False):
	cookies[name] = value
	import webframe
	string = urllib.quote_plus(name) + '=' + urllib.quote_plus(value)
	if comment is not False:
		string += '; Comment=' + urllib.quote_plus(comment)
	if domain is not False:
		string += '; Domain=' + urllib.quote_plus(domain)
	if expires is not False:
		string += '; expires=' + expires.strftime('%a, %d-%b-%Y %H:%M:%S GMT')
	if path is not False:
		string += '; Path=' + path
	webframe.addHeader('Set-Cookie', string)

def delCookie(name):
	setCookie(name, '', expires=datetime.datetime.now() - datetime.timedelta(1))

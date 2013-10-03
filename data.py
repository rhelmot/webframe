import MySQLdb

connection = False
cursor = False

def connect(name):
	global connection, cursor
	with open('data/sensitive/dblogin') as fd:
		connection = MySQLdb.connect(fd.readline()[:-1], fd.readline()[:-1], fd.readline()[:-1], 'dutcher_'+name)
	cursor = connection.cursor(MySQLdb.cursors.DictCursor)

def query(string, args=False):
	global cursor
	import webframe
	try:
		if args is not False:
			if isinstance(args, str) or isinstance(args, int):
				args = {'0': args}
			if isinstance(args, list) or isinstance(args, tuple):
				args = {str(a): b for a, b in enumerate(args)}
			string = webframe.util.template(string, {a: nq(b) for a,b in args.iteritems()})
		#webframe.addContent('Query: ' + string + '\n')
		cursor.execute(string)
	except MySQLdb.Error, e:
		connection.rollback()
		webframe.addError('MySQL Error ' + str(e.args[0]) + ': '+e.args[1])
		return False
	connection.commit()
	return True

def getRow():
	global cursor
	return cursor.fetchone()

def getRows():
	global cursor
	return cursor.fetchall()

def getQuery(string, args=False):
	res = query(string, args)
	return getRows() if res else res

def nq(string, char='"'):
	return str(string).replace('\\', '\\\\').replace(char, '\\'+char)

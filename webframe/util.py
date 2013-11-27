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
                        buf = buf[:startindex] + buf[buf.index('{{~', startindex+2):] 
                return buf 
        def meetCond(cstring): 
                cond = cstring.split('=', 1) 
                return not ((not cond[0] in vars) or (len(cond) == 1 and (vars[cond[0]] == False or vars[cond[0]] == '' or vars[cond[0]] is None or vars[cond[0]] == 'False')) or (len(cond) == 2 and not str(vars[cond[0]]) == cond[1])) 
        while '{{~' in buf: 
                perp = buf.index('{{~') 
                direc = perp + 3 
                endirec = buf.index('}}', perp) 
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

def urlTitle(title):
	title = title.lower()
	title = title.replace(' ', '-')
	title = title.translate(None, '!@#$%^&*()+={}[],<>/\\|~`:;"')
	if len(title) > 80:
		title = title[:80]
	return title

def checkKeys(item, *args):
	try:
		for i in args:
			item[i]
	except:
		return False
	return True

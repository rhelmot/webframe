# auth.py - authentication functions for Webframe
#
# Copyright 2014 Andrew Dutcher

import webframe
import time, math, os, hashlib
from Crypto.Cipher import AES

hashes = ['rmd320', 'sha3', 'rmd160', 'sha1', 'sha512', 'md5']

def basichash(x):
	if hashes == []:
		return x
	a = hashlib.new(hashes[0])
	a.update(x)
	return a.hexdigest()

second = 1
minute = 60*second
hour = 60*minute
day = 24*hour
week = 7*day
month = 30*day
year = 365*day

timeout = hour
keyfile = 'data/sensitive/ckeys'

try:
	loadKeys(keyfile)
except:
	secretServerKey = '0123456789ABCDEF'
	otherServerKey = 'FEDCBA9876543210'

while True:
	try:
		basichash('asdf')
		break
	except:
		hashes = hashes[1:]

def loadKeys(keyfile):
	global secretServerKey, otherServerKey
	with open(keyfile) as fd:
		secretServerKey = fd.readline()[:-1]
		otherServerKey = fd.readline()[:-1]

def genTokenSimple(tokenString):
	return AES.new(ipv4Key(), AES.MODE_CBC, secretServerKey).encrypt(timeStr() + pad16(tokenString)).encode('base64')[:-1].encode('rot13')

def checkTokenSimple(token):
	try:
		canidate = AES.new(ipv4Key(), AES.MODE_CBC, secretServerKey).decrypt(token.decode('rot13').decode('base64'))
	except:
		return False
	if len(canidate) < 16 or not canidate[:16].isdigit():
		return False
	tim = int(canidate[:16])
	if tim + timeout < timeInt():
		return False
	if not checkpad(canidate[16:]):
		return False
	return unpad(canidate[16:])

def timeInt():
	return int(math.floor(time.time()))

def timeStr():
	tint = str(timeInt())
	while len(tint) < 16:
		tint = '0' + tint
	return tint

def ipv4Int():
    if webframe.remoteAddress is None:
        return 0xFFFFFFFF
    else:
        return sum(int(byte) << (8 * (3-i)) for i, byte in enumerate(webframe.remoteAddress.split('.')))

def ipv4Key():
	ipint = ipv4Int()
	ipkey = str(hex((ipint + (ipint << 32) + (ipint << 64) + (ipint << 96))))[2:-1]
	return xor(ipkey, otherServerKey)

def pad16(text):
	lastblock = len(text)%16
	remaining = 16-lastblock
	return text + chr(remaining)*remaining

def checkpad(text):
	if len(text) == 0:
		return False
	num = ord(text[-1])
	if len(text) < num:
		return False
	if not text[-num:] == text[-1]*num:
		return False
	return True

def unpad(text):
	padding_length = ord(text[-1])
	return text[:-padding_length]

def saltHash(text):
	return basichash('q9' + text + '37a\n')

def xor(string, key):
	o = ''
	i = 0
	for c in string:
		o += chr(ord(key[i%len(key)])^ord(c))
		i += 1
	return o



def checkPerm(permset, permission):
	if permission == '' or permission is None:
		return True
	for antiperm in [a[1:] for a in permset.split(',') if a[0] == '!']:
		if matchPerm(antiperm, permission):
			return False
	for perm in [a for a in permset.split(',') if not a[0] == '!']:
		if matchPerm(perm, permission):
			return True
	return False

def matchPerm(perm, prosp):
	if perm == '*' or perm == prosp:
		return True
	if '*' in perm:
		if perm[-1] == '*':
			if perm[:-1] == prosp[:len(perm)-1]:
				return True
		else:
			index = perm.index('*')
			if (perm[:index] + perm[index+1:]) == (prosp[:index] + prosp[index-len(perm)+1:]):
				return True
	return False

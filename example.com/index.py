#!/usr/bin/python
# -*- coding: utf-8 -*-
#  index.py

import os, sys
npath = os.path.split(os.path.realpath(__file__))[0]
sys.path.append(os.path.realpath(npath + '/data/lib/python'))

import webframe

def main():
	webframe.addHeader('Content-type', 'text/html')
	webframe.setTitle('Hello, webframe!');
	webframe.addCss('/data/style.css')
	webframe.addScript('/data/script/script.js')
	webframe.addContent(webframe.util.template('data/template/site.html.pyt', {'content': 'Hello, world!'}))
	webframe.site()

if __name__ == '__main__':
        main()

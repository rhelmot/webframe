#!/bin/bash

# webframe setup script! easy as pie!
# to be run SERVERSIDE, got that?

# set up directory structure
echo "Setting up directory structure..."

mkdir data
mkdir data/img
mkdir data/script
mkdir data/template
mkdir data/sensitive
mkdir data/user
chmod 777 data/user
echo -n "[INPUT] Relative path to library: "
read WEBFLIBPATH
ln -s ../$WEBFLIBPATH data/lib


# generate base functionality files
echo "Generating base-functionality files..."

echo "-index.py"
echo -n "#!/usr/bin/python2.7
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
	webframe.addScript('/data/lib/util.js')
	webframe.addScript('/data/script/script.js')
	webframe.addContent(webframe.template('data/template/site.html.pyt', {'content': 'Hello, world!'}))
	webframe.site()

if __name__ == '__main__':
        main()
" > index.py
chmod 755 index.py

echo "-data/script/script.js"
echo -n "//Javascript document
" > data/script/script.js

echo "-data/style.css"
echo -n "/* Main CSS document */

html, body {
	height: 100%;
	margin: 0px;
	padding: 0px;
}

body {
	background-color: #DDD;
	font-family: sans-serif;
	color: black;
	text-align: center;
}

#container {
	min-height: 100%;
	height: auto !important;
	height: 100%;
	margin-bottom: -3em;
}

header {
	display: inline-block;
	font-size: 4em;
	color: #333;
	margin-bottom: 20px;
}

main {
	display: block;
	margin: 0px auto 20px;
	background-color: white;
	padding: 10px;
	border-radius: 7px;
	width: 40%;
	min-width: 400px;
	text-align: left;
}

a {
	color: #444;
	text-decoration: none;
}
a:visited { color: #555; }
a:hover {
	color: #333;
	text-decoration: underline;
}
a:active { color: #222; }

#push { height: 3em; }

footer {
	display: block;
	font-size: .6em;
	color: #888;
	background-color: white;
	padding: 2em 0px;
	width: 100%;
	height: 1em;
}
" > data/style.css

echo "-data/template/site.html.pyt"
echo -n "<div id=\"container\">
<header>
Default Webframe Site
</header>
<main>
{{content}}
</main>
<div id=\"push\"></div>
</div>
<footer>
&copy; Copyright 2013 <a href="http://andrewdutcher.com">Andrew Dutcher</a>. Site powered by <a href="https://github.com/rhelmot/webframe">webframe</a>.
</footer>
" > data/template/site.html.pyt


# Write htaccess files
echo "Writing .htaccess files..."

echo "-./"
echo -n "AddHandler cgi-script .py
RewriteEngine on
RewriteCond %{REQUEST_FILENAME} !-f
RewriteCond %{REQUEST_FILENAME} !-d
RewriteRule ^.*$ index.py [L]
DirectoryIndex index.py index.php index.html index.htm
" > .htaccess

echo "-data/"
echo "Options -Indexes
" > data/.htaccess

echo "-data/sensitive"
echo -n "Order Deny,Allow
Deny from All
" > data/sensitive/.htaccess


# Generate sensitive data
echo "Generating sensitive data..."

echo -n "[INPUT] Database server: "
read WEBFDBSERVER
echo -n "[INPUT] Database username: "
read WEBFDBUSER
echo -n "[INPUT] Database password: "
read -s WEBFDBPWD
echo ""
echo $WEBFDBSERVER > data/sensitive/dblogin
echo $WEBFDBUSER >> data/sensitive/dblogin
echo $WEBFDBPWD >> data/sensitive/dblogin
openssl rand -base64 12 > data/sensitive/ckeys 2> /dev/null
openssl rand -base64 12 >> data/sensitive/ckeys 2> /dev/null


# Git setup
echo "Setting up Git repository..."

git init > /dev/null
git config receive.denyCurrentBranch ignore
echo -n "#!/bin/sh
GIT_WORK_TREE=../ git checkout -f
" > .git/hooks/post-receive
chmod +x .git/hooks/post-receive
git add . > /dev/null
git commit -m 'Initial webframe autocommit' > /dev/null

# Finished! Print clone info

echo "Done! Clone your new site with:"
WEBFGITPORT=
if [ "$SSH_CONNECTION" != "" ]; then
	WEBFSSHARR=(${SSH_CONNECTION})
	if [ "${WEBFSSHARR[3]}" != "22" -a "${WEBFSSHARR[3]}" != "" ]; then
		WEBFGITPORT=:${WEBFSSHARR[3]}
	fi
fi
echo "git clone ssh://$USER@$HOSTNAME$WEBFGITPORT$PWD"

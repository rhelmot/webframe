Webframe
========

When you just want a goddamned website
--------------------------------------

If I were to say something about "the purpose of webframe is to provide an unobtrusive yet powerful blah blah blah" I'd be lying because I wrote this for myself because I wanted a library I knew how to use and could be held accountable for. That being said, I think it's pretty cool.

Organization
------------

Webframe is designed to run behind apache as Python CGI, although I may expand that in the future when I have more platforms to deal with. Webframe encourages (and requires, at least to some degree) a specific site structure with the following elements:

-Each site runs out of a folder and all nondata requests are served by index.py with some help from .htaccess
-Each site has a `data/` folder which contains the static data needed for rendering the site, with the exception of the data/user folder which can hold file uploads and such.
-`data/lib` is symlinked to a basic library that you can reuse for all your sites, containing at the very least a python/ directory (added to your pythonpath at runtime) which contains the webframe package.
-MySQL as the database
-You work seperately from your dev/production servers and update them through git

Setup
-----

Do the following on the server side:
-Make your standard `lib/` directory somewhere
-Make a `python/` directory inside `lib/` and `cd` to it
-Clone this repository: `git clone https://github.com/rhelmot/webframe.git`

And then for each website you set up:
-Configure apache to serve files out of a certain directory. Make sure that the `AllowOverride` directive is set to `all`
-`cd` to that folder
-Run the following: `[path to]lib/python/webframe/webframe_init.sh`
-Input any inforation it asks you for
-When it finishes, you can clone your repository with the line it gives you. If you want to be able to test your site locally, be sure to repeat the `lib/python/webframe` directory-creating step!

If you plan on using databases, please remote the `'dutcher_'+` bit on line 9 of `auth.py`. I use shared hosting and all my databases start with that, so it's convenient to have that in there.

Templating
----------

Webframe has an easy-to-use templating system. Here is an overview of its features:
-`webframe.util.template( (<template string> | <path to template file>), <content dict>, cache=False)`
-`{{keyname}}` will be replaced with `value` if the dict contains `'keyname': 'value'`
-`{{~if auth=admin}}Controls{{~elif auth}}Logged in{{~else}}Anonymous{{~endif}}` yields different values depending on the value of `auth` in the content dict
--All values are truthy except for `False` and `''`
--`{{~if` blocks do not nest
--No logical operations or tests other than equality are supported
-If you're loading the same template file many times, set the third argument to `True` to cache its value

Databases
---------

-Provide database information at initialization
-Initialize with `webframe.data.connect(<database name>)`
-`webframe.data.query()` runs a query (False on failure) whose results can be accessed through `webframe.data.getRow()` and `webframe.data.getAll()`
-`webframe.data.getQuery()` returns a tuple of all returned rows or False on failure
-Rows are returned as dicts, with common types parsed
-Prepared-esque queries supported-- The query string is parsed by webframe.util.template()
-Supports sanitation by escaping backslashes and double quotes in templated items. *Only use double-quotes in your queries.*
-Uses `mysqldb` for querying stuff

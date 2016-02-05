Guetzli, A Deliciously Fast and Simple CMS Based on Files
=========================================================

[![Join the chat at https://gitter.im/muellermichel/guetzli](https://badges.gitter.im/Join%20Chat.svg)](https://gitter.im/muellermichel/guetzli?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge)

Guetzli came about when we became too frustrated with Wordpress and its cesspool of plugins constantly breaking each other just to provide basic features like backups and multilingual pages. Guetzli is

1) Insanely simple. It's written in less than 300 lines of Python Flask.

2) Powerful. Add as many pages and languages as you like by editing the content directory using favourite local file editor, no server restarts required. Even changing the template or the configuration doesn't require a restart. Need to rollout to production? Just git push & pull, rollout done.

3) Fast. On a puny 2GB Hetzner VPS it was measured to get [345 requests per second from the outside internet and 600 requests per second from within the same network](docs/benchmark.txt), using the [multithreaded uwsgi implementation](run_server).

What's with the name? 'Guetzli' is the Swiss German word for cookie. It's a good metaphor for this CMS, since it's small, quickly digested and comes with [biscuit](docs/documentation.md#the-biscuit) and [chocolate](docs/documentation.md#the-chocolate).

[![Screencast: Writing a Unified Stencil Code](/../master/docs/Screencast_Thumbnail.png)](https://www.youtube.com/watch?v=MEUrirTZ-D8) ![Choco Guetzli](/../master/docs/Choco_leibniz.jpg)

Setup
-----
1) Fork this repository so you can create your own site.

2) Clone your repo and `cd` into it.

3) Copy `sites/basic-example` or `sites/minimal` into a new subdirectory of sites that holds the contents of your site. Commit it to your repo.

4) `sudo pip install Flask pystache ipaddress`.

3) Feed guetzli to the python: `python ./server.py --site [site-subdir-name]`. For additional options, see `python ./server.py --help`.
WARNING: This is only meant for development, do *not* use this for production purposes (as it could make your machine vulnerable). For production deployment please see [Going Live!](docs/documentation.md#going-live).

4) Enjoy on localhost:5000. For a production ready deployment, please see [Going Live!](docs/documentation.md#going-live)

Design Principles
-----------------
1) No Database! The filesystem is more than enough for a simple multi-page web appearance.

2) File changes need to be reflected in the next request.

3) Nevertheless, hit the file system the least amount possible - use file modification dates and in-memory cache to do the least amount of File I/O possible.

4) Cache the result of all potentially expensive operations (like json.loads or even regex matches).

Features
--------
1) Localized posts, e.g. blogging.

2) Automatic reloading of modified resources on the next request, including `content/config.json`. You should never have to restart this server.

3) Automatic pulling from changes on github repository (requires webhook setup, see [Going Live!](docs/documentation.md#going-live)).

4) Full multilanguage support. Add as many languages as you like by editing `content/config.json` and add the linked pages in language-subfolders under `content/pages` (see the example in the repo). Guetzli will match the one that best represents the client's request header and lists the other options just in case.

5) Mustache templating - in the template, pages and posts.

6) Localized strings, defined in `content/config.json`.

7) Extensions - handle user submitted content, add your own datasources to guetzli.

7) Redirect to (localized) default page if a page can't be found.

8) All URL params are checked to only contain letters, numbers, underscores and dashes (which is also the restriction for the page filenames) - no funny business in your file system!

Documentation
-------------
All you need to know should be in the [documentation](docs/documentation.md). Otherwise, please open up an issue with your question.

Dependencies
------------
1) Python version >= 2.7.7

2) Flask

3) pystache

License
-------
LGPL

Authors
-------
Michel Müller, System Architect [Protogrid](http://protogrid.com)

Mark Schmitz, Web Engineer [Protogrid](http://protogrid.com)

Contributors
------------
Thanks to Renato Testa, Chief DevOps [Protogrid](http://protogrid.com), for contributing the VPS performance benchmarks!

ToDo
----
1) Forms & Mailing support

2) Dockerization



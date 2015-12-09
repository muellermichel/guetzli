Guetzli, A deliciously fast and simple Filesystem-Web-CMS
=========================================================

Guetzli came about when we became too frustrated with Wordpress and its cesspool of plugins constantly breaking each other just to provide basic features like backups and multilingual pages. Guetzli is

1) Insanely simple. It's written in less than 200 lines of Python Flask.

2) Powerful. Add as many pages and languages as you like by editing the content directory using favourite local file editor, no server restarts required. Even changing the template or the configuration doesn't require a restart. Need to rollout to production? Just git push & pull, rollout done.

3) Fast. On a 2012 Macbook Pro with SSD it's doing 400-500 requests per second *just using the single threaded Flask toy server*. Multi-threaded wsgi-servers on a decent VPS will be even happier with Guetzli.

Setup
-----
1) Clone this repo and `cd` into it.

2) `sudo pip install Flask pystache`.

3) `python ./server.py`.

4) Enjoy on localhost:5000.

Design Principles
-----------------
1) No Database! The filesystem is more than enough for a simple multi-page web appearance.

2) File changes need to be reflected in the next request.

3) Nevertheless, hit the file system the least amount possible - use file modification dates and in-memory cache to do the least amount of File I/O possible.

4) Cache the result of all potentially expensive operations (like json.loads or even regex matches).

Features
--------
1) Full multilanguage support. Add as many languages as you like by editing `content/config.json` and add the linked pages in language-subfolders under `content/pages` (see the example in the repo). Guetzli will match the one that best represents the client's request header and lists the other options just in case.

2) Mustache templating, both within the page contents as well as the template.

3) Redirect to (localized) default page if a page can't be found.

4) All URL params are checked to only contain letters, numbers, underscores and dashes (which is also the restriction for the page filenames) - no funny business in your file system!

*content/config.json*
```
    {
      "pagename_by_language_and_title": {
        "en": {
          "About Protogrid":"001-about",
          "Events":"002-events"
        },
        "de": {
          "Über Protogrid":"001-about",
          "Ereignisse":"002-events",
          "Speziell für Deutschsprechende":"00Z-special"
        }
      },
      "active_languages": [
        {"language":"English", "id":"en"},
        {"language":"German", "id":"de"},
        {"language":"Spanish", "id":"es"}
      ],
      "default_page": "001-about",
      "default_language": "en"
    }
```

Dependencies
------------
1) Python 2.x

2) Flask

3) pystache

License
-------
LGPL

Authors
-------
Michel Müller, System Architect [Protogrid](http://protogrid.com)

Mark Schmitz, Web Engineer [Protogrid](http://protogrid.com)

ToDo
----
1) Forms & Mailing support

2) Dockerization



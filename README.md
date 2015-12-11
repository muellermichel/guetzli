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
1) Localized posts, e.g. blogging.

2) Automatic reloading of modified resources on the next request, including `content/config.json`. You should never have to restart this server.

2) Full multilanguage support. Add as many languages as you like by editing `content/config.json` and add the linked pages in language-subfolders under `content/pages` (see the example in the repo). Guetzli will match the one that best represents the client's request header and lists the other options just in case.

3) Mustache templating, both within the page contents as well as the template.

4) Localized strings, defined in `content/config.json`.

5) Redirect to (localized) default page if a page can't be found.

6) All URL params are checked to only contain letters, numbers, underscores and dashes (which is also the restriction for the page filenames) - no funny business in your file system!

HowTo
-----
*Add/Change/Remove a (blog-) post*

Add/Change/Remove a file under `content/posts/[post-type]/[language]` using a `YYYY-MM-DD-[AuthorShortname]-[AnyTitle].html` filename format. See the existing examples. Specially available tags for blog entries are `{{ author }}` `{{ post_path }}` (URL to the standalone entry) and  `{{ publishing_date }}`.

*Add/Change/Remove a page*

Add/Change/Remove a file under `content/pages/[language]`. From the moment the file exists, the page is reachable under the URL `/[language]/[filename(without .html)]`.

*Link a page in the menu*

Add `{"title": "[Given Title]", "name":[filename(without .html)]}` under the correct language list in `content/config.json` --> `pages_by_language`.

*Add a new localized string*

Add it in `content/config.json` --> `strings_by_template_reference` using the reference as key (see examples) and use it with `{{ reference }}` in any page, post or template.

*Change the appearance*

Edit `design/template.html`.

*Add a new post type*

1) Add a new directory with language subdirectories under `content/posts`.

2) Copy `design/blog-items` as `design/[post-dir-name]-items`. Adapt it to your needs.

3) Add the `{{ [post-dir-name]_items }}` tag on a page where you'd like to list your posts.

4) Reference the posts directory in `content/config.json` --> `active_post_types_by_pagename` (see the blog as an example).

*example content/config.json*
```
    {
      "pages_by_language": {
        "en": [
          {"title": "About Protogrid", "name": "001-about"},
          {"title": "Blog", "name": "002-blog"},
          {"title": "Events", "name": "003-events"}
        ],
        "de": [
          {"title": "Über Protogrid", "name": "001-about"},
          {"title": "Blog", "name": "002-blog"},
          {"title": "Ereignisse", "name": "003-events"},
          {"title": "Speziell für Deutschsprechende", "name": "00Z-special"}
        ]
      },
      "active_languages": [
        {"language": "English", "id":"en"},
        {"language": "German", "id":"de"},
        {"language": "Spanish", "id":"es"}
      ],
      "strings_by_template_reference": {
        "date_particle": {"en": "on", "de": "am"},
        "page_localized": {"en": "page", "de": "Seite"},
        "of_localized": {"en": "of", "de": "von"},
        "blog_posts_localized": {"en": "blog posts", "de": "Blog-Einträge"},
        "to_localized": {"en": "to", "de": "bis"}
      },
      "active_post_types_by_pagename": {
        "002-blog": [
          {"posts_directory": "blog", "items_per_page": 3}
        ]
      },
      "authors_by_shortname": {
        "mmu": "Michel Müller",
        "msc": "Mark Schmitz"
      },
      "default_pagename": "001-about",
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

2) Blogging

3) Dockerization



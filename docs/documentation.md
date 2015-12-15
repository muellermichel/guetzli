Guetzli Documentation
=====================

Guetzli, a deliciously fast and simple Filesystem-Web-CMS. For setup and design, please see the [README](../README.md).

**Contents**

[The Biscuit (dynamic content)](#the-biscuit)

[The Chocolate (static content)](#the-chocolate)

[Templating](#templating)

[HowTo](#howto)

[Going Live!](#going-live)

The Biscuit
-----------
Dynamic content (i.e. the 'bisc') is the backbone of Guetzli. It's generated using the pages and posts under `./content` and the templates under `./design`. To your visitors it is served using the following URLs:

`/`

The root landing page matches the visitor's language to the available ones listed in `content/config.json` --> `active_languages` and serves the page defined as default in `content/config.json` --> `default_pagename`, rendered using `design/template.html`. In case there is no language match it uses `content/config.json` --> `default_language`.

`/bisc`

Same as root.

`/bisc/[language]`

Same as root, but serves a specific language.

`/bisc/[language]/[pagename]`

Serves a specific page if available under `content/pages/[language]/[pagename].html` using `design/template.html`. If unavailable, serves `default_pagename` in the chosen language.

`/bisc/[language]/[post-type]/[post-id]`

Serves a specific post if available under `content/posts/[post-type]/[language]/[post-id].html` using `design/template.html`. If unavailable, serves `default_pagename` in the chosen language. [post-id] should be in `YYYY-MM-DD-[author_shortname]-[post_name]` format.

Additionally, Guetzli recognizes the following URL arguments (after `?`):

* `page_number=[integer larger than one]` - page requested for post listings.

The Chocolate
-------------
HTML pages are fine, but they may be a bit boring and dry to some visitors. To make your Guetzli more tasty, add some static files like CSS, images, javascript or whatever you like under `./design/static/[your-folder-structure]`. This is served as `/choco/[your-folder-structure]`.

Templating
----------
This section serves as a reference for templating with Guetzli. Please have a look at the provided example that comes with the repository, it's mostly self explanatory.

**The following tags are available everywhere (pages, posts and templates)**

* `{{ reference }}` for every reference defined in the current language in `content/config.json` --> `strings_by_template_reference`

* `{{ current_path }}` - relative URL of the currently rendered page.

* `{{ pagename }}` - the filename (without `.html`) of the currently served page (also serves as the page's identifier in the URL).

*  `{{#menu}} .. {{/menu}}` - repeats the content for each menu entry defined in the current language in `content/config.json` --> `pages_by_language`. Offers the following tags for each entry:

  * `{{ url }}` - the relative URL to the page.

  * `{{ title }}` - the title as defined in the page metadata in `content/config.json`.

* `{{#languages}} .. {{/languages}}` - repeats the content for each language defined in `content/config.json` --> `active_languages`. Offers the following tags for each entry:

  * `{{ id }}` - the language locale as defined in the language metadata in `content/config.json`.

  * `{{ language }}` - the human readable language string as defined in the language metadata in `content/config.json`.

**The following tags are additionally available on pages for each post type that has been registered for the respective page in `content/config.json` --> `active_post_types_by_pagename`**

  * `{{{ [post-type]_listing }}}` - renders a page of [post-type] in the current language. A page contains `content/config.json` --> `active_post_types_by_pagename` --> [pagename] --> [items_per_page] many posts. Each post is defined in a file under `content/posts/[post-type]/[language]` where [post-type] is given by `content/config.json` --> `active_post_types_by_pagename` --> [pagename] --> [posts_directory].

**The following tags are additionally available in posts**

* `{{ author }}` - either the [author_shortname] as defined in the post filename or - if available - the author's name as defined in `content/config.json` --> `authors_by_shortname`.

* `{{ post_path }}` - the relative URL of the post.

* `{{ publishing_date }}` - the date as defined in the post filename.

**The following tags are additionally available in `design/template.html`**

* `{{{ content }}}` - the content of the currently accessed page.

**The following tags are additionally available in post listings templates `design/[post-type]-items.html`**

  * `{{#[post-type]_items}} .. {{/[post-type]_items}}` - repeats the content for each post on the current page. Offers the following tags for each post:

    * {{ item }} - the content for the current post.

  * `{{ first_item_number }}` - a one-based number for the first displayed post on the current page.

  * `{{ last_item_number }}` - a one-based number for the last displayed post on the current page.

  * `{{ number_of_items }}` - the total number of posts available.

  * `{{ number_of_pages }}` - the total number of pages available.

  * `{{ next_page }}` - page number of the next page or `None` if not available.

  * `{{ previous_page }}` - page number of the previous page or `None` if not available.

HowTo
-----
**Add/Change/Remove a (blog-) post**

Add/Change/Remove a file under `content/posts/[post-type]/[language]` using a `YYYY-MM-DD-[author_shortname]-[post_name].html` filename format. See the existing examples. Specially available tags for blog entries are `{{ author }}` `{{ post_path }}` (URL to the standalone entry) and  `{{ publishing_date }}`.

**Add/Change/Remove a page**

Add/Change/Remove a file under `content/pages/[language]`. From the moment the file exists, the page is reachable under the URL `/[language]/[filename(without .html)]`.

**Link a page in the menu**

Add `{"title": "[Given Title]", "name":[filename(without .html)]}` under the correct language list in `content/config.json` --> `pages_by_language`.

**Add a new localized string**

Add it in `content/config.json` --> `strings_by_template_reference` using the reference as key (see examples) and use it with `{{ reference }}` in any page, post or template.

**Change the appearance**

Edit `design/template.html`.

**Add a new post type**

1) Add a new directory with language subdirectories under `content/posts`.

2) Copy `design/blog-items.html` as `design/[post-dir-name]-items.html`. Adapt it to your needs.

3) Add the `{{ [post-dir-name]_items }}` tag on a page where you'd like to list your posts.

4) Reference the posts directory in `content/config.json` --> `active_post_types_by_pagename` (see the blog as an example).

**example content/config.json**
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

Going Live!
-----------
To feed Guetzli to many visitors, see the `run_server` script for a production ready multi-threaded execution of this CMS. You need uwsgi to use this script (`./run_server`). Adapt the concurrency (`--processes` for dynamic content `--offload-threads` for static content) to your hardware. It's best to deploy it using the system process manager of your environment (systemd, upstart, docker..). If you have a production config for any of these systems, please share so others can profit from your work.
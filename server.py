#!/usr/bin/python
# -*- coding: UTF-8 -*-

# Copyright (C) 2014 Michel Müller

# This file is part of Guetzli.

# Guetzli is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# Guetzli is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Lesser General Public License for more details.

# You should have received a copy of the GNU Lesser General Public License
# along with Guetzli. If not, see <http://www.gnu.org/licenses/>.

from __future__ import division
import os, codecs, json, re, math, logging
import pystache
from flask import Flask, abort, redirect, url_for, request, jsonify
app = Flask(__name__, static_folder="./design/static", static_url_path="/choco")

_file_content_by_path = {}
_file_modification_date_by_path = {}
_checked_path_components = {}
_content_config = {}
_post_filenames_by_subdirectory_and_language = {}
_post_directory_modification_dates_by_subdirectory_and_language = {}
_site = "basic-example"
_autopull_key = None
logging.getLogger().setLevel(logging.INFO)

if __name__ != '__main__':
	import sys
	if len(sys.argv) > 1:
		_site = sys.argv[1]
	if len(sys.argv) > 2:
		_autopull_key = sys.argv[2]
	logging.info("setup completed as embedded application for site %s, passed arguments %s" %(_site, sys.argv))

class NotFoundError(Exception):
	pass

class UsageError(Exception):
	pass

def get_repo_path():
	return os.path.dirname(os.path.abspath(__file__))

def get_site_path():
	return os.path.join(get_repo_path(), 'sites', _site)

def get_template_path(template_name = "template"):
	return os.path.join(get_site_path(), 'design', template_name) + '.html'

def get_page_path(pagename, language):
	return os.path.join(get_site_path(), 'content', 'pages', language, pagename) + '.html'

def get_post_path(posts_subdirectory, language, post_id=None):
	posts_path = os.path.join(get_site_path(), 'content', 'posts', posts_subdirectory, language)
	if post_id == None:
		return posts_path
	return os.path.join(posts_path, post_id) + '.html'

def get_file_content(path):
	if not os.path.isfile(path):
		if path in _file_content_by_path:
			del _file_content_by_path[path]
		if path in _file_modification_date_by_path:
			del _file_modification_date_by_path[path]
		raise NotFoundError(path)
	previous_modification_date = _file_modification_date_by_path.get(path)
	curr_modification_date = os.path.getmtime(path)
	if previous_modification_date and curr_modification_date <= previous_modification_date:
		return _file_content_by_path[path], False
	with codecs.open(path, encoding="utf-8") as f:
		file_content = f.read()
	_file_content_by_path[path] = file_content
	_file_modification_date_by_path[path] = curr_modification_date
	return file_content, True

def render_file_content(path, ctx):
	return pystache.render(get_file_content(path)[0], ctx)

def get_content_config():
	config_path = os.path.join(get_site_path(), 'content', 'config') + '.json'
	file_content, has_changed = get_file_content(config_path)
	global _content_config
	if not has_changed:
		return _content_config
	try:
		_content_config = json.loads(file_content)
	except Exception:
		raise UsageError("Wrong format or syntax error in %s, please compare with basic-example." %(config_path))
	return _content_config

def get_post_content(ctx, content_config, posts_path, posts_subdirectory, file_name):
	match = re.match(r'(\d{4}-\d{2}-\d{2})-(\w*)-?(.*?)\.\w*', file_name)
	author_shortname = None
	publishing_date = None
	if match:
		publishing_date = match.group(1)
		author_shortname = match.group(2)
	author = content_config.get('authors_by_shortname', {}).get(author_shortname, author_shortname)
	ctx.update({
		"post_path": url_for(
			'page_view',
			pagename=posts_subdirectory,
			language=ctx["language"],
			post_id=file_name.split('.')[0]
		),
		"author": author,
		"publishing_date": publishing_date
	})
	return render_file_content(os.path.join(posts_path, file_name), ctx)

def get_posts_page_and_page_info(ctx, content_config, posts_subdirectory, items_per_page, page_number):
	posts_path = get_post_path(posts_subdirectory, ctx['language'])
	if not os.path.isdir(posts_path):
		raise NotFoundError(posts_path)
	identifier_tuple = (posts_subdirectory, ctx['language'])
	previous_directory_modification_date = _post_directory_modification_dates_by_subdirectory_and_language.get(
		identifier_tuple
	)
	curr_directory_modification_date = os.path.getmtime(posts_path)
	file_names = None
	if previous_directory_modification_date \
	and curr_directory_modification_date <= previous_directory_modification_date:
		file_names = _post_filenames_by_subdirectory_and_language.get(identifier_tuple)
	else:
		file_names = sorted(
			[file_name for file_name in os.listdir(posts_path) if os.path.isfile(os.path.join(
				posts_path,
				file_name
			))],
			reverse=True
		)
		_post_filenames_by_subdirectory_and_language[identifier_tuple] = file_names
		_post_directory_modification_dates_by_subdirectory_and_language[
			identifier_tuple
		] = curr_directory_modification_date
	number_of_pages = int(math.ceil(len(file_names) / items_per_page))
	start_item = (page_number - 1) * items_per_page
	page_info = {
		"first_item_number": start_item + 1,
		"last_item_number": min(start_item + items_per_page, len(file_names)),
		"number_of_items": len(file_names),
		"number_of_pages": number_of_pages,
		"next_page": page_number + 1 if page_number < number_of_pages else None,
		"previous_page": page_number - 1 if page_number > 1 else None
	}
	page = []
	for file_name in file_names[start_item:start_item + items_per_page]:
		page.append({
			"item": get_post_content(ctx, content_config, posts_path, posts_subdirectory, file_name)
		})
	return page, page_info

def get_posts_listing(ctx, content_config, posts_subdirectory, items_per_page, page_number=1):
	try:
		page, page_info = get_posts_page_and_page_info(ctx, content_config, posts_subdirectory, items_per_page, page_number)
		ctx[posts_subdirectory + "_items"] = page
		ctx.update(page_info)
	except NotFoundError:
		pass
	return render_file_content(get_template_path(posts_subdirectory + "-items"), ctx)

def get_page_content(ctx, content_config):
	for entry in content_config.get("active_post_types_by_pagename", {}).get(ctx["pagename"], []):
		posts_subdirectory = entry["posts_directory"]
		items_per_page = entry.get("items_per_page")
		if not isinstance(items_per_page, int) or items_per_page <= 0:
			items_per_page = 5
		ctx[posts_subdirectory + "_listing"] = get_posts_listing(
			ctx,
			content_config,
			posts_subdirectory,
			items_per_page,
			ctx["page_number"]
		)
	return render_file_content(get_page_path(ctx["pagename"], ctx["language"]), ctx)

def get_menu(language, content_config):
	menu = []
	for page in content_config.get('pages_by_language', {}).get(language, []):
		menu.append({
			"title": page["title"],
			"url": url_for("page_view", pagename=page["name"], language=language)
		})
	return menu

def is_valid_path_component(component):
	'''making sure that the client cannot manipulate his way to parts of the file system where we don't want him to'''
	if not component:
		return True
	if component in _checked_path_components:
		return True
	if re.match(r'^[A-Za-z0-9_-]*$', component):
		_checked_path_components[component] = None
		return True
	return False

@app.errorhandler(500)
def custom_error_handler(error):
	if hasattr(error, "description")
		return error.description.get('message', "")
	return str(error)

@app.route('/', defaults={'pagename': None, 'language': None, 'post_id': None}, methods=['GET'])
@app.route('/bisc', defaults={'pagename': None, 'language': None, 'post_id': None}, methods=['GET'])
@app.route('/bisc/<language>', defaults={'pagename': None, 'post_id': None}, methods=['GET'])
@app.route("/bisc/<language>/<pagename>", defaults={'post_id': None}, methods = ['GET'])
@app.route("/bisc/<language>/<pagename>/<post_id>", methods = ['GET'])
def page_view(pagename, language, post_id):
	if not is_valid_path_component(pagename) \
	or not is_valid_path_component(language) \
	or not is_valid_path_component(post_id):
		abort(403)
	try:
		content_config = get_content_config()
		active_languages = content_config.get('active_languages', [])
		default_pagename = content_config.get('default_pagename', 'index')
		if language == None:
			language = request.accept_languages.best_match([
				language_hash['id'] for language_hash in active_languages
			])
		if language == None:
			language = content_config.get('default_language', 'en')
		if pagename == None:
			pagename = default_pagename
		ctx = {
			"page_number": request.args.get('page_number', 1, type=int),
			"pagename": pagename,
			"language": language,
			"menu": get_menu(language, content_config),
			"languages": content_config.get('active_languages', []),
			"current_path": url_for('page_view', pagename=pagename, language=language)
		}
		ctx.update({
			key: lang_dict.get(language)
			for key, lang_dict in content_config.get("strings_by_template_reference", {}).iteritems()
		})
		if post_id != None:
			ctx["content"] = get_post_content(
				ctx,
				content_config,
				get_post_path(pagename, language),
				pagename,
				post_id + '.html'
			)
		else:
			ctx["content"] = get_page_content(ctx, content_config)
		return render_file_content(get_template_path(), ctx)
	except UsageError as e:
		abort(500, {'message': str(e)})
	except NotFoundError as e:
		if not pagename or not language \
		or (pagename == 'index') \
		or (post_id == None and str(e) != get_page_path(pagename, language)) \
		or (post_id and str(e) != get_post_path(pagename, language, post_id)):
			abort(500, {'message': 'sorry, %s could not be found' %(str(e))})
		elif pagename == default_pagename:
			abort(404)
		else:
			return redirect(url_for('page_view', language=language))
	raise Exception("Well that's embarassing - this should never happen.")

@app.route("/autopull", methods=['POST'])
def autopull_view():
	#adapted from https://github.com/razius/github-webhook-handler
	import ipaddress, requests
	request_ip = ipaddress.ip_address(u'{0}'.format(request.remote_addr))
	hook_blocks = requests.get('https://api.github.com/meta').json()['hooks']
	for block in hook_blocks:
		if ipaddress.ip_address(request_ip) in ipaddress.ip_network(block):
			break
	else:
		abort(403)
	if request.headers.get('X-GitHub-Event') == "ping":
		return json.dumps({'msg': 'Hi!'})
	if request.headers.get('X-GitHub-Event') != "push":
		return json.dumps({'msg': "wrong event type"})
	payload = json.loads(request.data)
	if _autopull_key: # Check if POST request signature is valid
		import hmac, hashlib
		signature = request.headers.get('X-Hub-Signature').split('=')[1]
		mac = hmac.new(_autopull_key, msg=request.data, digestmod=hashlib.sha1)
		if not hmac.compare_digest(mac.hexdigest(), signature):
			abort(403)
	import subprocess
	logging.info("pulling latest repo version upon request by github webhook")
	subp = subprocess.Popen("git pull", cwd=get_repo_path())
	subp.wait()
	return 'OK'

if __name__ == "__main__":
	import optparse
	optparser = optparse.OptionParser()
	optparser.add_option("--site", dest="site")
	optparser.add_option("--autopull-key", dest="autopull_key")
	(options, args) = optparser.parse_args()
	if options.site:
		_site = options.site
	if options.autopull_key:
		_autopull_key = options.autopull_key.encode() if type(_autopull_key) == unicode else options.autopull_key
	logging.info("setup completed as main application for site %s" %(_site))
	app.run(debug=True)

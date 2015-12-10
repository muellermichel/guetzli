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

import os, codecs, json, re
import pystache
from flask import Flask, abort, redirect, url_for, request
app = Flask(__name__)

_file_content_by_path = {}
_file_modification_date_by_path = {}
_checked_path_components = {}
_content_config = {}

class NotFoundError(Exception):
	pass

def base_path():
	return os.path.dirname(os.path.abspath(__file__))

def get_file_content(path):
	if not os.path.isfile(path):
		if path in _file_content_by_path:
			del _file_content_by_path[path]
		if path in _file_modification_date_by_path:
			del _file_modification_date_by_path[path]
		raise NotFoundError()
	previous_modification_date = _file_modification_date_by_path.get(path)
	current_modification_date = os.path.getmtime(path)
	if previous_modification_date and current_modification_date <= previous_modification_date:
		return _file_content_by_path[path], False
	with codecs.open(path, encoding="utf-8") as f:
		file_content = f.read()
	_file_content_by_path[path] = file_content
	_file_modification_date_by_path[path] = current_modification_date
	return file_content, True

def get_content_config():
	file_content, has_changed = get_file_content(
		os.path.join(base_path(), 'content', 'config') + '.json'
	)
	global _content_config
	if not has_changed:
		return _content_config
	_content_config = json.loads(file_content)
	return _content_config

def get_template():
	template, _ = get_file_content(os.path.join(base_path(), 'design', 'template') + '.html')
	return template

def get_page_path(pagename, language):
	return os.path.join(base_path(), 'content', 'pages', language, pagename) + '.html'

def get_page_content(ctx):
	page, _ = get_file_content(get_page_path(ctx["pagename"], ctx["language"]))
	return pystache.render(page, ctx)

def get_menu(language, content_config):
	menu = []
	for title in content_config['pagename_by_language_and_title'].get(language, {}):
		pagename = content_config['pagename_by_language_and_title'][language][title]
		menu.append({
			"title": title,
			"url": "/%s/%s" %(language, pagename)
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

@app.route('/', defaults={'page': None, 'language': None})
@app.route('/<language>', defaults={'page': None})
@app.route("/<language>/<page>")
def page_view(page, language):
	if not is_valid_path_component(page) or not is_valid_path_component(language):
		abort(403)
	content_config = get_content_config()
	if language == None:
		language = request.accept_languages.best_match([
			language_hash['id'] for language_hash in content_config['active_languages']
		])
	if language == None:
		language = content_config['default_language']
	pagename = page if page != None else content_config['default_page']
	is_default_page = pagename == content_config['default_page']
	ctx = {
		"pagename": pagename,
		"language": language,
		"menu": get_menu(language, content_config),
		"languages": content_config['active_languages'],
	}
	try:
		ctx["content"] = get_page_content(ctx)
	except NotFoundError:
		if is_default_page:
			abort(404)
		else:
			return redirect(url_for('page_view', language=language))
	return pystache.render(get_template(), ctx)

if __name__ == "__main__":
	app.run(debug=True)
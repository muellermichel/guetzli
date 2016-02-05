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

import json, logging
from flask import Flask, abort, redirect, url_for, request
from tools.guetzli import \
	NotFoundError, UsageError, \
	set_site, get_site, \
	get_repo_path, get_template_path, get_page_path, get_post_path, \
	get_content_config, get_post_content, get_page_content, get_menu, \
	render_file_content, is_valid_path_component

_autopull_key = None
_autopull_branch = None

logging.getLogger().setLevel(logging.INFO)
if __name__ == '__main__': #Option parsing for toy server startup
	import optparse
	optparser = optparse.OptionParser()
	optparser.add_option("--site", dest="site")
	optparser.add_option("--autopull-key", dest="autopull_key")
	optparser.add_option("--autopull-branch", dest="autopull_branch")
	(options, args) = optparser.parse_args()
	if options.site:
		set_site(options.site)
	if options.autopull_key:
		_autopull_key = options.autopull_key.encode() if type(_autopull_key) == unicode else options.autopull_key
	if options.autopull_branch:
		_autopull_branch = options.autopull_branch
else: #Option parsing for wsgi startup
	import sys
	if len(sys.argv) > 1:
		set_site(sys.argv[1])
	if len(sys.argv) > 2:
		_autopull_key = sys.argv[2]
	if len(sys.argv) > 3:
		_autopull_branch = sys.argv[3]

app = Flask(__name__, static_folder="./sites/%s/design/static" %(get_site()), static_url_path="/choco")

@app.errorhandler(500)
def custom_error_handler(error):
	if hasattr(error, "description"):
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

@app.route("/autopull", methods=['GET', 'POST'])
def autopull_view():
	#adapted from https://github.com/razius/github-webhook-handler
	import ipaddress, requests
	request_ip = ipaddress.ip_address(u'{0}'.format(request.remote_addr))
	hook_blocks = requests.get('https://api.github.com/meta').json()['hooks']
	for block in hook_blocks:
		if ipaddress.ip_address(request_ip) in ipaddress.ip_network(block):
			break
	else:
		logging.info("someone tried request autopull from unsupported IP %s" %(request_ip))
		abort(403)
	if request.headers.get('X-GitHub-Event') == "ping":
		return json.dumps({'msg': 'Hi!'})
	if request.headers.get('X-GitHub-Event') != "push":
		return json.dumps({'msg': "wrong event type"})
	if request.method == 'POST':
		payload = json.loads(request.data)
		if _autopull_key: # Check if POST request signature is valid
			import hmac, hashlib
			signature = request.headers.get('X-Hub-Signature').split('=')[1]
			mac = hmac.new(_autopull_key, msg=request.data, digestmod=hashlib.sha1)
			if not hmac.compare_digest(mac.hexdigest(), signature):
				logging.info("hash did not match for autopull" %(request_ip))
				abort(403)
		import subprocess
		logging.info("pulling latest repo version upon request by github webhook")
		branch = _autopull_branch if autopull_branch else "master"
		subp = subprocess.Popen(
			["git", "checkout", branch, "&&", "git", "pull", "origin", branch],
			cwd=get_repo_path()
		)
		subp.wait()
	return 'OK'

if __name__ == "__main__":
	logging.info("setup completed as main application for site %s; running on port 5000 accessible from localhost" %(get_site()))
	app.run(debug=True)
else:
	logging.info("setup completed as embedded application for site %s, passed arguments %s; running on your chosen port accessible from everywhere" %(get_site(), sys.argv))
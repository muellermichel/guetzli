#!/usr/bin/python
# -*- coding: UTF-8 -*-

# Copyright (C) 2016 Michel Müller

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

# Contributors:
# * Mark Schmitz

import json, logging, os
from flask import Flask, abort, redirect, url_for, request
from tools.guetzli import \
	NotFoundError, UsageError, NotAllowedError, \
	set_site, get_site, \
	get_repo_path, get_page_path, get_post_path, get_content_config, \
	get_context_with_rendered_content, render_with_template

_autopull_key = None
_autopull_branch = None
_untrusted_autopull = False

logging.getLogger().setLevel(logging.INFO)
if __name__ == '__main__': #Option parsing for toy server startup
	import optparse
	optparser = optparse.OptionParser()
	optparser.add_option("--site", dest="site")
	optparser.add_option("--autopull-key", dest="autopull_key")
	optparser.add_option("--autopull-branch", dest="autopull_branch")
	optparser.add_option("--enable-untrusted-autopull", dest="untrusted_autopull", default=False, action='store_true')
	(options, args) = optparser.parse_args()
	if options.site:
		set_site(options.site)
	if options.autopull_key:
		_autopull_key = options.autopull_key.encode() if type(_autopull_key) == unicode else options.autopull_key
	_autopull_branch = options.autopull_branch if options.autopull_branch else "master"
	_untrusted_autopull = options.untrusted_autopull
else: #Option parsing for wsgi startup
	import sys
	if len(sys.argv) > 1:
		set_site(sys.argv[1])
	if len(sys.argv) > 2:
		_autopull_key = sys.argv[2]
	_autopull_branch = sys.argv[3] if len(sys.argv) > 3 else "master"
	_untrusted_autopull = len(sys.argv) > 4 and sys.argv[4] == "true"
logging.info("Autopulling is set up: %s; Branch: %s; Untrusted connections allowed: %s" %(
	_autopull_key != None or _untrusted_autopull,
	_autopull_branch,
	_untrusted_autopull
))

app = Flask(__name__, static_folder="./sites/%s/design/static" %(get_site()), static_url_path="/choco")

extensions_directory_list = os.listdir("extensions")
for file_name in extensions_directory_list:
	basename_and_file_ext = os.path.splitext(file_name)
	if basename_and_file_ext[1] != ".py":
		continue
	if basename_and_file_ext[0] == "__init__":
		continue
	guetzli_extension_name = basename_and_file_ext[0]
	guetzli_extension_endpoint = "/%s" %(guetzli_extension_name.replace('_', '-'))
	guetzli_extension_module = __import__("extensions.%s" %(guetzli_extension_name), fromlist=["extensions"])
	logging.info("registering %s extension with endpoint %s" %(guetzli_extension_name, guetzli_extension_endpoint))
	app.register_blueprint(getattr(guetzli_extension_module, guetzli_extension_name), url_prefix=guetzli_extension_endpoint)

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
	try:
		return render_with_template(get_context_with_rendered_content(
			language=language,
			page_or_post_type=pagename,
			post_id=post_id
		))
	except NotAllowedError:
		abort(403)
	except UsageError as e:
		abort(500, {'message': str(e)})
	except NotFoundError as e:
		if not pagename or not language \
		or (pagename == 'index') \
		or (post_id == None and str(e) != get_page_path(pagename, language)) \
		or (post_id and str(e) != get_post_path(pagename, language, post_id)):
			abort(500, {'message': 'sorry, %s could not be found' %(str(e))})
		elif pagename == get_content_config().get('default_pagename', 'index'):
			abort(404)
		else:
			return redirect(url_for('page_view', language=language))
	raise Exception("Well that's embarassing - this should never happen.")

@app.route("/autopull", methods=['GET', 'POST'])
def autopull_view():
	#adapted from https://github.com/razius/github-webhook-handler
	import ipaddress, requests
	if not _untrusted_autopull and not _autopull_key:
		logging.warning("someone tried request autopull, but there is no autopull secret configured for this guetzli instance - aborting")
		abort(500)
	if not _untrusted_autopull:
		request_ip = ipaddress.ip_address(u'{0}'.format(request.remote_addr))
		hook_blocks = requests.get('https://api.github.com/meta').json()['hooks']
		for block in hook_blocks:
			if ipaddress.ip_address(request_ip) in ipaddress.ip_network(block):
				break
		else:
			logging.info("someone tried request autopull from unsupported IP %s" %(request_ip))
			abort(403)
	if request.headers.get('X-GitHub-Event') == "ping":
		logging.info("Received and answered Ping event from github")
		return json.dumps({'msg': 'Hi!'})
	if request.headers.get('X-GitHub-Event') != "push" \
	and request.headers.get('X-Gitlab-Event') != "Push Hook":
		logging.warning("We have received a webhook, but it is the wrong event type - aborting")
		abort(403)
	if request.method == 'POST':
		if not _untrusted_autopull and _autopull_key: # Check if POST request signature is valid
			import hmac, hashlib
			signature = request.headers.get('X-Hub-Signature').split('=')[1]
			mac = hmac.new(_autopull_key, msg=request.data, digestmod=hashlib.sha1)
			try:
				if not hmac.compare_digest(mac.hexdigest(), signature):
					logging.info("hash did not match for autopull" %(request_ip))
					abort(403)
			except AttributeError:
				# What compare_digest provides is protection against timing attacks,
				# fallback to string comparison for python < 2.7.7
				logging.warning("webhooks are used without timing attack protection available from python 2.7.7 - please update if possible")
				if not str(mac.hexdigest()) == str(signature):
					abort(403)
		import subprocess
		logging.info("pulling latest repo version upon request by github webhook")
		branch = _autopull_branch if _autopull_branch else "master"
		subp = subprocess.Popen(
			["git", "checkout", branch],
			cwd=get_repo_path()
		)
		subp.wait()
		subp = subprocess.Popen(
			["git", "pull", "origin", branch],
			cwd=get_repo_path()
		)
		subp.wait()
	return 'OK'

if __name__ == "__main__":
	logging.info("setup completed as main application for site %s; running on port 5000 accessible from localhost" %(get_site()))
	app.run(debug=True)
else:
	logging.info("setup completed as embedded application for site %s, passed arguments %s; running on your chosen port accessible from everywhere" %(get_site(), sys.argv))
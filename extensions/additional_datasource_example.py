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

from flask import abort
from tools.guetzli import NotAllowedError, UsageError, NotFoundError, \
	Extension, render_with_template, get_context_with_rendered_content

additional_datasource_example = Extension('additional_datasource_example')

#registering and defining a view for the /additional_datasource_example/ endpoint
@additional_datasource_example.route('/', methods=['GET'], defaults={'language': None})
@additional_datasource_example.route('/<language>', methods=['GET'])
def example_view(language):
	try:
		return render_with_template(get_context_with_rendered_content(
			language=language,
			page_or_post_type='00X-my-extended-page',
			additional_context={
				"my_additional_tag": "hello world!",
				"my_example_list": [{"value": "one"}, {"value": "two"}, {"value": "three"}]
			}
		))
	except NotAllowedError:
		abort(403)
	except UsageError as e:
		abort(500, {'message': str(e)})
	except NotFoundError:
		abort(404)
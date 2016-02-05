import logging, json
from flask import abort, redirect, url_for, request
from tools.guetzli import Extension, send_mail

form_example = Extension('form_example')

#registering and defining a post handler for the /form_example/<language> endpoint
@form_example.route('/<language>', methods=['POST'])
def handler(language):
	logging.info("form content submitted: " + str(request.form))
	try:
		send_mail(
			recipients=["john.smith@example.com"],
			sender=request.form["e-mail"],
			subject="form submitted",
			text=json.dumps(request.form)
		)
		send_mail(
			recipients=[request.form["e-mail"]],
			sender="john.smith@example.com",
			subject="Thank you for contacting us!",
			text="We will get back to you as soon as possible"
		)
	except Exception as e:
		logging.error("Something went wrong when trying to send an E-Mail: Type of error: %s, Message: %s" %(
			type(e),
			str(e)
		))
	return redirect(url_for('page_view', pagename="00X-success", language=language))
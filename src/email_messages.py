from google.appengine.api import mail

from flask import get_template_attribute


def send_message(address, macro_name, **kwargs):
    # get message body
    body = get_template_attribute('email_messages.html', macro_name)(**kwargs)

    # try to get message subject
    try:
        subject = get_template_attribute('email_messages.html', macro_name+"_subject")(**kwargs)
    except AttributeError:
        subject = "Notification"
    
    # send mail
    mail.send_mail(sender="HashBounty <noreply@example.com>",
              to=address,
              subject=subject,
              body=body)

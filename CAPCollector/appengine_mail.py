"""A Django E-Mail backend for Google App Engine."""

__author__ = "shakusa@google.com (Steve Hakusa)"

import logging

from django.conf import settings
from django.core.mail.backends import base
from django.utils import text
from google.appengine.api import app_identity
from google.appengine.api import mail


class EmailBackend(base.BaseEmailBackend):
  """Django email backend for AppEngine's mail API."""

  def send_messages(self, email_messages):
    """Sends one or more EmailMessage objects and returns the number sent.

    Args:
      email_messages: A list of django.core.mail.EmailMessage objects.

    Returns:
      An int indicating the number of successfully sent messages.
    """
    num_sent = 0
    for email in email_messages:
      if self._send(email):
        num_sent += 1
    return num_sent

  def _send(self, email):
    """Send the message using the appengine mail API."""
    try:
      ae_email = self._convert_message(email)
      ae_email.send()
      logging.debug("Sent mail %s to %s", ae_email.subject, ae_email.to)
    except (ValueError, mail.Error) as err:
      logging.warn(err)
      if not self.fail_silently:
        raise
      return False
    return True

  def _convert_message(self, django_email):
    """Convert a Django EmailMessage to an App Engine EmailMessage."""

    django_email.reply_to = django_email.extra_headers.get("Reply-To", None)

    html_body = None
    if django_email.alternatives:
      if django_email.alternatives[0]:
        html_body = django_email.alternatives[0][0]

    logging.info("Subject without formatting: %s", django_email.subject)

    from_email = "admin@%s.appspotmail.com" % app_identity.get_application_id()

    ae_kwargs = {
        "sender": from_email,
        "subject": self._format_subject(settings.EMAIL_SUBJECT_PREFIX
                                        + django_email.subject),
        "to": django_email.to,
    }

    if django_email.reply_to:
      ae_kwargs["reply_to"] = django_email.reply_to

    if django_email.cc:
      ae_kwargs["cc"] = django_email.cc

    if django_email.bcc:
      ae_kwargs["bcc"] = django_email.bcc

    ae_kwargs["body"] = django_email.body

    if html_body:
      ae_kwargs["html"] = html_body

    ae_email = mail.EmailMessage(**ae_kwargs)
    ae_email.check_initialized()
    return ae_email

  def _format_subject(self, subject):
    """Escape CR and LF characters, and limit length.

    RFC 2822"s hard limit is 998 characters per line. So, minus "Subject: "
    the actual subject must be no longer than 989 characters.

    Args:
      subject: A string containing the original subject.

    Returns:
      A string containing the formatted subject.
    """
    formatted_subject = subject.replace("\n", "\\n").replace("\r", "\\r")
    truncator = text.Truncator(formatted_subject)
    formatted_subject = truncator.chars(985)
    return formatted_subject

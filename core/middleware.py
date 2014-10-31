"""CAPCollector application core middlewares."""

__author__ = "arcadiy@google.com (Arkadii Yakovets)"

import logging


class ErrorLogMiddleware(object):
  """Logs exceptions."""
  def process_exception(self, unused_request, exception):
    logging.exception(exception)

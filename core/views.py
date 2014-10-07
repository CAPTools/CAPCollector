"""Django views for core CAP collector functionality."""

__author__ = "Arkadii Yakovets (arcadiy@google.com)"

import json
import os

from bs4 import BeautifulSoup
from core import utils
from django.conf import settings
from django.contrib.auth import authenticate
from django.http import Http404
from django.http import HttpResponse
from django.http import HttpResponseBadRequest
from django.template.loader import render_to_string
from django.views.generic import View


class FeedView(View):
  """Feed representation (either XML or HTML)."""

  def get(self, request, *args, **kwargs):
    feed_type = kwargs["feed_type"]

    if "alert_id" in kwargs:
      filename = "%s.xml" % kwargs["alert_id"]
      alert_file_path = os.path.join(settings.ACTIVE_ALERTS_DATA_DIR, filename)
      try:
        with open(alert_file_path, "r") as alert_file:
          alert_content = alert_file.read()
      except IOError:
        raise Http404

      if feed_type == "html":
        context = {
            "alert": utils.ParseAlert(alert_content, feed_type, filename)
        }
        response = render_to_string("core/alert.html.tmpl", context)
        return HttpResponse(BeautifulSoup(response, feed_type).prettify())

      return HttpResponse(alert_content, content_type="text/xml")

    return HttpResponse(utils.GenerateFeed(feed_type),
                        content_type="text/%s" % feed_type)


class PostView(View):
  """Handles new alert creation."""

  def post(self, request, *args, **kwargs):
    username = request.POST.get("uid")
    password = request.POST.get("password")
    xml_string = request.POST.get("xml")

    if not username or not password or not xml_string:
      return HttpResponseBadRequest()

    authenticated = authenticate(username=username, password=password)
    alert_id = None
    error_message = ""
    is_valid = False

    # TODO(arcadiy): refactor permissions error handling.
    if authenticated:
      alert_id, is_valid, error_message = utils.CreateAlert(xml_string,
                                                            username)
    response = {
        "authenticated": True if authenticated else False,
        "error": error_message,
        "uuid": alert_id,
        "valid": is_valid,
    }

    return HttpResponse(json.dumps(response), content_type="application/json")

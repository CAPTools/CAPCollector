"""Django views for core CAP collector functionality."""

__author__ = "Arkadii Yakovets (arcadiy@google.com)"

import json

from bs4 import BeautifulSoup
from core import models
from core import utils
from django.conf import settings
from django.contrib.auth import authenticate
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.http import Http404
from django.http import HttpResponse
from django.http import HttpResponseBadRequest
from django.template.loader import render_to_string
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView
from django.views.generic import View


class FeedView(View):
  """Feed representation (either XML or HTML)."""

  def get(self, request, *args, **kwargs):
    feed_type = kwargs["feed_type"]

    if "alert_id" in kwargs:
      try:
        alert = models.Alert.objects.get(uuid=kwargs["alert_id"])
      except models.Alert.DoesNotExist:
        raise Http404

      if feed_type == "html":
        context = {
            "alert": utils.ParseAlert(alert.content, feed_type, alert.uuid)
        }
        response = render_to_string("core/alert.html.tmpl", context)
        return HttpResponse(BeautifulSoup(response, feed_type).prettify())

      return HttpResponse(alert.content, content_type="text/xml")

    return HttpResponse(utils.GenerateFeed(feed_type),
                        content_type="text/%s" % feed_type)


class AlertTemplateView(View):
  """Area/message templates view."""

  @method_decorator(login_required)
  def dispatch(self, *args, **kwargs):
    return super(AlertTemplateView, self).dispatch(*args, **kwargs)

  def get(self, request, *args, **kwargs):
    template_id = request.GET.get("template_id")

    if "template_type" not in kwargs or not template_id:
      return HttpResponseBadRequest()
    template_type = kwargs["template_type"]
    if template_type == "area":
      template_model = models.AreaTemplate
    elif template_type == "message":
      template_model = models.MessageTemplate

    try:
      template = template_model.objects.get(id=template_id)
    except template_model.DoesNotExist:
      raise Http404
    return HttpResponse(template.content, content_type="text/xml")


class IndexView(TemplateView):
  template_name = "index.html.tmpl"

  @method_decorator(login_required)
  def dispatch(self, *args, **kwargs):
    return super(IndexView, self).dispatch(*args, **kwargs)

  def get_context_data(self, **kwargs):
    context = super(IndexView, self).get_context_data(**kwargs)
    area_templates = models.AreaTemplate.objects.order_by("title")
    message_templates = models.MessageTemplate.objects.order_by("title")
    context["area_templates"] = area_templates
    context["message_templates"] = message_templates
    context['map_default_viewport'] = settings.MAP_DEFAULT_VIEWPORT
    return context


class PostView(View):
  """Handles new alert creation."""

  @method_decorator(login_required)
  def post(self, request, *args, **kwargs):
    username = request.POST.get("uid")
    password = request.POST.get("password")
    xml_string = request.POST.get("xml")

    if not username or not password or not xml_string:
      return HttpResponseBadRequest()

    user = authenticate(username=username, password=password)
    alert_id = None
    error_message = ""
    is_valid = False

    if (not user or
        not user.groups.filter(name=settings.ALERT_CREATORS_GROUP_NAME)):
      raise PermissionDenied

    alert_id, is_valid, error_message = utils.CreateAlert(xml_string, username)
    response = {
        "error": error_message,
        "uuid": alert_id,
        "valid": is_valid,
    }

    return HttpResponse(json.dumps(response), content_type="application/json")

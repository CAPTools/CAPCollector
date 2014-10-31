# Copyright (c) 2013, Carnegie Mellon University. All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# Redistributions of source code must retain the above copyright notice, this
# list of conditions and the following disclaimer.
#
# Redistributions in binary form must reproduce the above copyright notice, this
# list of conditions and the following disclaimer in the documentation and/or
# other materials provided with the distribution.
#
# Neither the name of the Carnegie Mellon University nor the names of its
# contributors may be used to endorse or promote products derived from
# this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.


"""Helpers for core CAP Collector module."""


import copy
from datetime import datetime
import logging
import lxml
import os
import re
import uuid

from bs4 import BeautifulSoup
from core import models
from dateutil import parser
from django.conf import settings
from django.core.urlresolvers import reverse
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.translation import ugettext
import pytz

try:
  import xmlsec
  XMLSEC_DEFINED = True
except ImportError:
  # This module is not available on AppEngine.
  # https://code.google.com/p/googleappengine/issues/detail?id=1034
  XMLSEC_DEFINED = False


def GetCurrentDate():
  """The current date helper."""
  return datetime.now(pytz.utc)


def GenerateFeed(feed_type="xml"):
  """Generates XML for alert feed based on active alert files.

  Args:
    feed_type: (string) Either xml of html.

  Returns:
    String. Ready to serve XML feed content.
  """

  # Build feed header.
  now = timezone.now().isoformat()
  time_str, tz_str = now.split("+")
  feed_updated = "%s+%s" % (time_str.split(".")[0], tz_str)
  feed_url = settings.SITE_URL + reverse("feed", args=[feed_type])
  entries = []

  # For each unexpired message, get the necessary values and add it to the feed.
  for alert in models.Alert.objects.filter(
      updated=False,
      expires_at__gt=GetCurrentDate()).order_by("-created_at"):
    entries.append(ParseAlert(alert.content, feed_type, alert.uuid))

  feed_dict = {
      "entries": entries,
      "feed_url": feed_url,
      "updated": feed_updated,
      "version": settings.VERSION,
  }

  feed_template = "core/feed." + feed_type + ".tmpl"

  return BeautifulSoup(
      render_to_string(feed_template, feed_dict), feed_type).prettify()


def ParseAlert(xml_string, feed_type, alert_uuid):
  """Parses select fields from the CAP XML file at file_name.

  Primary use is intended for populating a feed <entry>.

  Note:
  - This code assumes the input alert XML has only one <info>.
  - The parsed XML does not contain all fields in the CAP specification.
  - The code accepts both complete and partial CAP messages.

  Args:
    xml_string: (string) Alert XML string.
    feed_type: (string) Alert feed representation (XML or HTML).
    alert_uuid: (string) Alert UUID.

  Returns:
    Dictionary.
    Keys/values corresponding to alert XML attributes or empty dictionary.
  """

  def GetFirstText(xml_element):
    """Returns the first text item from an XML element."""
    if xml_element and len(xml_element):
      return xml_element[0].text
    return ""

  def GetAllText(xml_element):
    """Returns an array of text items from multiple elements."""
    if xml_element and len(xml_element):
      return [item.text for item in xml_element]
    return []

  def GetNameValuePairs(xml_elements):
    """Returns a list of dictionaries for paired elements."""
    pair_list = []
    for xml_element in xml_elements:
      name_element, value_element = xml_element.getchildren()
      pair_list.append({
          "name": name_element.text,
          "value": value_element.text})
    return pair_list

  def GetCapElement(element_name, xml_tree):
    """Extracts elements from CAP XML tree."""
    element = "//p:" + element_name
    finder = lxml.etree.XPath(element, namespaces={"p": settings.CAP_NS})
    return finder(xml_tree)

  alert_dict = {}
  try:
    xml_tree = lxml.etree.fromstring(xml_string)
    expires_str = GetFirstText(GetCapElement("expires", xml_tree))

    # Extract the other needed values from the CAP XML.
    sender = GetFirstText(GetCapElement("sender", xml_tree))
    sender_name = GetFirstText(GetCapElement("senderName", xml_tree))
    name = sender
    if sender_name:
      name = name + ": " + sender_name

    title = GetFirstText(GetCapElement("headline", xml_tree))
    if not title:
      title = ugettext("Alert Message")  # Force a default.

    link = "%s%s" % (settings.SITE_URL,
                     reverse("alert", args=[alert_uuid, feed_type]))
    expires = parser.parse(expires_str) if expires_str else None
    sent_str = GetFirstText(GetCapElement("sent", xml_tree))
    sent = parser.parse(sent_str) if sent_str else None

    alert_dict = {
        "title": title,
        "event": GetFirstText(GetCapElement("event", xml_tree)),
        "link": link,
        "web": GetFirstText(GetCapElement("web", xml_tree)),
        "name": name,
        "sender": sender,
        "sender_name": sender_name,
        "expires": expires,
        "msg_type": GetFirstText(GetCapElement("msgType", xml_tree)),
        "references": GetFirstText(GetCapElement("references", xml_tree)),
        "alert_id": GetFirstText(GetCapElement("identifier", xml_tree)),
        "category": GetFirstText(GetCapElement("category", xml_tree)),
        "response_type": GetFirstText(GetCapElement("responseType", xml_tree)),
        "sent": sent,
        "description": GetFirstText(GetCapElement("description", xml_tree)),
        "instruction": GetFirstText(GetCapElement("instruction", xml_tree)),
        "urgency": GetFirstText(GetCapElement("urgency", xml_tree)),
        "severity": GetFirstText(GetCapElement("severity", xml_tree)),
        "certainty": GetFirstText(GetCapElement("certainty", xml_tree)),
        "language": GetFirstText(GetCapElement("language", xml_tree)),
        "parameters": GetNameValuePairs(GetCapElement("parameter", xml_tree)),
        "area_desc": GetFirstText(GetCapElement("areaDesc", xml_tree)),
        "geocodes": GetNameValuePairs(GetCapElement("geocode", xml_tree)),
        "circles": GetAllText(GetCapElement("circle", xml_tree)),
        "polys": GetAllText(GetCapElement("polygon", xml_tree)),
    }
    # Non-CAP-compliant fields used for message templates.
    expiresDurationMinutes = GetFirstText(
        GetCapElement("expiresDurationMinutes", xml_tree))
    if expiresDurationMinutes:
      alert_dict["expiresDurationMinutes"] = expiresDurationMinutes
  # We don't expect any invalid XML alerts.
  except lxml.etree.XMLSyntaxError as e:
    logging.exception(e)
  return alert_dict


def SignAlert(xml_tree, username):
  """Sign XML with user key/certificate.

  Args:
    xml_tree: (string) Alert XML tree.
    username: (string) Username of the alert author.

  Returns:
    String.
    Signed alert XML tree if your has key/certificate pair
    Unchanged XML tree otherwise.
  """

  if not XMLSEC_DEFINED:
    return xml_tree

  key_path = os.path.join(settings.CREDENTIALS_DIR, username + ".key")
  cert_path = os.path.join(settings.CREDENTIALS_DIR, username + ".cert")

  try:
    signed_xml_tree = copy.deepcopy(xml_tree)
    xmlsec.add_enveloped_signature(signed_xml_tree, pos=-1)
    xmlsec.sign(signed_xml_tree, key_path, cert_path)
    return signed_xml_tree
  except (IOError, xmlsec.exceptions.XMLSigException):
    return xml_tree


def CreateAlert(xml_string, username):
  """Creates alert signed by userame from provided XML string.

  Args:
    xml_string: (string) XML content.
    username: (string) Username of the alert author.

  Returns:
    A tuple of (msg_id, valid, error) where:
      msg_id: (string) Unique alert ID (UUID)
      valid: (bool) Whether alert has valid XML or not.
      error: (string) Error message in case XML is invalid.
  """

  msg_id = None
  valid = False
  xml_string = xml_string.replace("\n", "")

  try:
    # Clean up the XML format a bit.
    xml_string = re.sub("> +<", "><", xml_string)
    # Now parse into etree and validate.
    xml_tree = lxml.etree.fromstring(xml_string)

    with open(os.path.join(settings.SCHEMA_DIR,
                           settings.CAP_SCHEMA_FILE), "r") as schema_file:
      schema_string = schema_file.read()
    xml_schema = lxml.etree.XMLSchema(lxml.etree.fromstring(schema_string))
    valid = xml_schema.validate(xml_tree)
    error = xml_schema.error_log.last_error
  except lxml.etree.XMLSyntaxError as e:
    error = "Malformed XML: %s" % e

  if valid:
    msg_id = str(uuid.uuid4())
    # Assign <identifier> and <sender> values.
    find_identifier = lxml.etree.XPath("//p:identifier",
                                       namespaces={"p": settings.CAP_NS})
    identifier = find_identifier(xml_tree)[0]
    identifier.text = msg_id

    # Set default <web> field if one was not filled by user.
    find_web = lxml.etree.XPath("//p:info/p:web",
                                namespaces={"p": settings.CAP_NS})
    web = find_web(xml_tree)[0]
    if web.text == "pending":
      web.text = "%s%s" % (settings.SITE_URL,
                           reverse("alert", args=[msg_id, "html"]))

    find_sender = lxml.etree.XPath("//p:sender",
                                   namespaces={"p": settings.CAP_NS})
    sender = find_sender(xml_tree)[0]
    sender.text = username + "@" + settings.SITE_DOMAIN

    find_sent = lxml.etree.XPath("//p:sent",
                                 namespaces={"p": settings.CAP_NS})
    sent = find_sent(xml_tree)[0]

    find_expires = lxml.etree.XPath("//p:expires",
                                    namespaces={"p": settings.CAP_NS})
    expires = find_expires(xml_tree)[0]

    find_references = lxml.etree.XPath("//p:references",
                                       namespaces={"p": settings.CAP_NS})
    has_references = len(find_references(xml_tree)) != 0

    # Sign the XML tree.
    xml_tree = SignAlert(xml_tree, username)

    # Re-serialize as string.
    signed_xml_string = lxml.etree.tostring(xml_tree, pretty_print=False)
    alert_obj = models.Alert()
    alert_obj.uuid = msg_id
    alert_obj.created_at = sent.text
    alert_obj.expires_at = expires.text
    alert_obj.content = signed_xml_string
    alert_obj.save()

    if has_references:
      for element in find_references(xml_tree):
        updated_alert_uuid = element.text.split(",")[1]
        models.Alert.objects.filter(
            uuid=updated_alert_uuid).update(updated=True)

  return (msg_id, valid, error)

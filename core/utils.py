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
import os
import re
import uuid
import xml

from bs4 import BeautifulSoup
from dateutil import parser
from django.conf import settings
from django.core.urlresolvers import reverse
from django.template.loader import render_to_string
from django.utils.translation import ugettext
from lxml import etree
import pytz
import xmlsec


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
  feed_url = settings.SITE_URL + reverse("feed", args=[feed_type])
  entries = []

  # For each unexpired message, get the necessary values and add it to the feed.
  filenames = sorted(os.listdir(settings.ACTIVE_ALERTS_DATA_DIR), reverse=True,
                     key=lambda path: os.path.getctime(
                         os.path.join(settings.ACTIVE_ALERTS_DATA_DIR, path)))
  for filename in filenames:
    if filename.startswith("."):
      continue

    file_path = os.path.join(settings.ACTIVE_ALERTS_DATA_DIR, filename)
    with open(file_path, "r") as alert_file:
      xml_string = alert_file.read()

    alert_dict = ParseAlert(xml_string, feed_type, filename)

    # Move expired msg to expired directory.
    if GetCurrentDate() > alert_dict["expires"]:
      os.rename(file_path, os.path.join(settings.INACTIVE_ALERTS_DATA_DIR,
                                        filename))
      continue  # And go on to the next message.

    entries.append(alert_dict)

  feed_dict = {
      "entries": entries,
      "feed_url": feed_url,
      "version": settings.VERSION,
  }

  feed_template = "core/feed." + feed_type + ".tmpl"

  return BeautifulSoup(
      render_to_string(feed_template, feed_dict), feed_type).prettify()


def ParseAlert(xml_string, feed_type, file_name):
  """Parses alert XML (accepts both complete and partial CAP messages).

  Args:
    xml_string: (string) Alert XML string.
    feed_type: (string) Alert feed representation (XML or HTML).
    file_name: (string) Alert file name.

  Returns:
    Dictionary.
    Keys/values corresponding to alert XML attributes or empty dictionary.
  """

  def GetFirstText(xml_element):
    """Returns the first text item from an XML element."""
    if xml_element and len(xml_element):
      return str(xml_element[0].text)
    return ""

  def GetAllText(xml_element):
    """Returns an array of text items from multiple elements."""
    if xml_element and len(xml_element):
      return [str(item.text) for item in xml_element]
    return []

  def GetCapElement(element_name, xml_tree):
    """Extracts elements from CAP XML tree."""
    element = "//p:" + element_name
    finder = etree.XPath(element, namespaces={"p": settings.CAP_NS})
    return finder(xml_tree)

  alert_dict = {}
  try:
    xml_tree = etree.fromstring(xml_string)
    expires_string = GetFirstText(GetCapElement("expires", xml_tree))

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
                     reverse("alert", args=[file_name.rstrip(".xml"),
                                            feed_type]))
    expires = parser.parse(expires_string) if expires_string else None
    updated_string = GetFirstText(GetCapElement("sent", xml_tree))
    updated = parser.parse(updated_string) if updated_string else None

    alert_dict = {
        "title": title,
        "link": link,
        "name": name,
        "expires": expires,
        "alert_id": GetFirstText(GetCapElement("identifier", xml_tree)),
        "category": GetFirstText(GetCapElement("category", xml_tree)),
        "response_type": GetFirstText(GetCapElement("responseType", xml_tree)),
        "updated": updated,
        "description": GetFirstText(GetCapElement("description", xml_tree)),
        "instruction": GetFirstText(GetCapElement("instruction", xml_tree)),
        "urgency": GetFirstText(GetCapElement("urgency", xml_tree)),
        "severity": GetFirstText(GetCapElement("severity", xml_tree)),
        "certainty": GetFirstText(GetCapElement("certainty", xml_tree)),
        "area_desc": GetFirstText(GetCapElement("areaDesc", xml_tree)),
        "circles": GetAllText(GetCapElement("circle", xml_tree)),
        "polys": GetAllText(GetCapElement("polygon", xml_tree)),
    }
  except etree.XMLSyntaxError:  # We don't expect any invalid XML alerts.
    pass  # TODO(arcadiy): log the exception after Django logging system setup.
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
    xml_string = xml.dom.minidom.parseString(xml_string).toprettyxml()
    # Now parse into etree and validate.
    xml_tree = etree.fromstring(xml_string)

    with open(os.path.join(settings.SCHEMA_DIR,
                           settings.CAP_SCHEMA_FILE), "r") as schema_file:
      schema_string = schema_file.read()
    xml_schema = etree.XMLSchema(etree.fromstring(schema_string))
    valid = xml_schema.validate(xml_tree)
    error = xml_schema.error_log.last_error
  except xml.parsers.expat.ExpatError as e:
    error = "Malformed XML: %s" % e

  if valid:
    msg_id = str(uuid.uuid4())
    # Assign <identifier> and <sender> values.
    find_identifier = etree.XPath("//p:identifier",
                                  namespaces={"p": settings.CAP_NS})
    identifier = find_identifier(xml_tree)[0]
    identifier.text = msg_id
    find_sender = etree.XPath("//p:sender",
                              namespaces={"p": settings.CAP_NS})
    sender = find_sender(xml_tree)[0]
    sender.text = username + "@" + settings.SITE_DOMAIN

    # Sign the XML tree.
    xml_tree = SignAlert(xml_tree, username)

    # Re-serialize as string.
    signed_xml_string = etree.tostring(xml_tree, pretty_print=False)

    file_path = os.path.join(settings.ACTIVE_ALERTS_DATA_DIR, msg_id + ".xml")
    with open(file_path, "w") as alert_file:
      alert_file.write(signed_xml_string + "\n")

  return (msg_id, valid, error)

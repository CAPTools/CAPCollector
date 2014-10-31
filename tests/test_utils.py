"""CAP Collector core utils tests."""

__author__ = "arcadiy@google.com (Arkadii Yakovets)"

import datetime
import os
import re
from xml.etree import cElementTree as xml_etree

from core import models
from core import utils
from dateutil import parser
from django import test
from django.conf import settings
from django.core.urlresolvers import reverse
from lxml import etree
import mock
import pytz
from tests import UUID_RE
import xmlsec


class UtilsTests(test.TestCase):
  """Utils unit tests."""

  fixtures = ["test_alerts.json", "test_templates.json"]

  TEST_USER_NAME = "test_user"
  DRAFT_ALERT_UUID = "a453f4bb-3249-45f6-8ddc-360da19fcc03"
  VALID_ALERT_UUID = "3ff7a28e-44b7-4ca5-aa5f-06dc42e474c1"
  FEED_DATE_FORMAT_RE = re.compile(
      r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}[+-]\d{2}:\d{2}")

  @property
  def valid_alert_content(self):
    return models.Alert.objects.get(uuid=self.VALID_ALERT_UUID).content

  @property
  def partial_alert_content(self):
    return models.MessageTemplate.objects.get(id=1).content

  @property
  def draft_alert_content(self):
    return models.Alert.objects.get(uuid=self.DRAFT_ALERT_UUID).content

  @property
  def invalid_alert_content(self):
    return "<my invalid xml>LMX</xml>"

  def test_parse_valid_alert(self):
    """Tests if valid XML alert parsed correctly."""
    golden_alert_dict = {
        "circles": [],
        "sent": parser.parse("2014-08-16T00:32:11+00:00"),
        "expires": parser.parse("2014-08-16T01:32:11+00:00"),
        "alert_id": self.VALID_ALERT_UUID,
        "link": "%s%s" % (settings.SITE_URL,
                          reverse("alert", args=[self.VALID_ALERT_UUID,
                                                 "xml"])),
        "response_type": "Monitor",
        "severity": "Extreme",
        "instruction": "Instruction here.",
        "description": "And description",
        "msg_type": "Alert",
        "category": "Fire",
        "name": "sender@some-agency.gov: sender",
        "title": "Some headline.",
        "event": "Fire fire fire.",
        "area_desc": "This and that area.",
        "certainty": "Observed",
        "parameters": [{"name": "name1", "value": "val1"},
                       {"name": "name2", "value": "val2"}],
        "geocodes": [{"name": "geo_code1", "value": "geo_code_value1"}],
        "polys": [],
        "urgency": "Immediate"
    }
    alert_dict = utils.ParseAlert(self.valid_alert_content, "xml",
                                  self.VALID_ALERT_UUID)
    for key in golden_alert_dict:
      self.assertEqual(alert_dict[key], golden_alert_dict[key])

  def test_parse_invalid_alert(self):
    """Tests if invalid XML alert parsed correctly."""
    self.assertDictEqual(utils.ParseAlert(self.invalid_alert_content,
                                          "xml", "no_filename"), {})

  def test_parse_partial_alert(self):
    """Tests if partial XML alert parsed correctly."""
    file_name = "partial_template"
    golden_alert_dict = {
        "response_type": "AllClear",
        "severity": "Severe",
        "instruction": "This is an instruction",
        "description": "This is a description",
        "msg_type": "Alert",
        "category": "Env",
        "certainty": "Possible",
        "urgency": "Expected",
        "title": "Alert Message",  # Default.
        "link": "%s%s" % (settings.SITE_URL,
                          reverse("alert", args=[file_name, "xml"])),
    }
    alert_dict = utils.ParseAlert(self.partial_alert_content, "xml", file_name)
    for key in golden_alert_dict:
      if not alert_dict[key]:
        continue  # We need values present in both template and alert files.
      self.assertEqual(alert_dict[key], golden_alert_dict[key])

  def test_sign_alert_signed(self):
    """Tests alert signature creation."""
    plain_alert = etree.fromstring(self.valid_alert_content)
    signed_alert = utils.SignAlert(plain_alert, self.TEST_USER_NAME)
    cert_path = os.path.join(settings.CREDENTIALS_DIR,
                             self.TEST_USER_NAME + ".cert")
    self.assertTrue(xmlsec.verified(signed_alert, cert_path))

  def test_sign_alert_not_signed(self):
    """Tests alert signature creation with no certificate provided."""
    plain_alert = etree.fromstring(self.valid_alert_content)
    signed_alert = utils.SignAlert(plain_alert, "does not exist")
    self.assertEquals(plain_alert, signed_alert)

  def test_create_alert_created(self):
    """Tests alert created successfully."""
    alert_uuid, is_valid, error = utils.CreateAlert(self.draft_alert_content,
                                                    self.TEST_USER_NAME)
    self.assertTrue(UUID_RE.match(alert_uuid))
    self.assertTrue(is_valid)
    self.assertEquals(error, None)

    alert = models.Alert.objects.get(uuid=alert_uuid)
    alert_dict = utils.ParseAlert(alert.content, "xml", alert.uuid)
    draft_dict = utils.ParseAlert(self.draft_alert_content, "xml", alert.uuid)
    # Remove alert IDs due to their random nature.
    del alert_dict["alert_id"]
    del draft_dict["alert_id"]
    self.assertDictEqual(alert_dict, draft_dict)

  def test_create_alert_failed(self):
    """Tests alert creation failed for invalid XML tree."""
    uuid, is_valid, error = utils.CreateAlert(self.invalid_alert_content,
                                              self.TEST_USER_NAME)
    self.assertEquals(uuid, None)
    self.assertFalse(is_valid)
    self.assertTrue(error)

  @mock.patch("core.utils.GetCurrentDate",
              lambda: datetime.datetime(2014, 8, 10, 23, 55, 12, 0, pytz.utc))
  def test_generate_feed_active_alert(self):
    """Tests XML feed with date before alert expiration date.

       Expiration date is 2014-08-10T23:55:12+00:00.
    """
    uuid, _, _ = utils.CreateAlert(self.draft_alert_content,
                                   self.TEST_USER_NAME)
    self.assertFalse(uuid in utils.GenerateFeed())

  @mock.patch("core.utils.GetCurrentDate",
              lambda: datetime.datetime(2014, 8, 10, 23, 55, 13, 0, pytz.utc))
  def test_generate_feed_inactive_alert(self):
    """Tests XML feed with date after alert expiration date.

       Expiration date is 2014-08-10T23:55:12+00:00.
    """
    uuid, _, _ = utils.CreateAlert(self.draft_alert_content,
                                   self.TEST_USER_NAME)
    self.assertFalse(uuid in utils.GenerateFeed())

  @mock.patch("core.utils.GetCurrentDate",
              lambda: datetime.datetime(2014, 8, 10, 23, 55, 11, 0, pytz.utc))
  def test_generate_feed_alerts_db_query(self):
    """Tests XML feed alerts order."""
    feed = xml_etree.fromstring(utils.GenerateFeed())  # Deals with Unicode.
    entries = []
    for entry in feed.findall(".//{http://www.w3.org/2005/Atom}entry"):
      entries.append(entry)

    self.assertEqual(len(entries), 2)  # Check the feed length.

    # Make sure alerts order is correct - most recent go first.
    last_alert = entries[0]
    previous_alert = entries[1]
    last_alert_created_at = last_alert.find(
        "{http://www.w3.org/2005/Atom}updated").text.strip()
    previous_alert_created_at = previous_alert.find(
        "{http://www.w3.org/2005/Atom}updated").text.strip()
    self.assertTrue(last_alert_created_at > previous_alert_created_at)

  def test_feed_updated_date_format(self):
    """Tests XML feed <updated> field format."""
    feed = xml_etree.fromstring(utils.GenerateFeed())
    updated = feed.find("{http://www.w3.org/2005/Atom}updated").text.strip()
    self.assertEqual(len(self.FEED_DATE_FORMAT_RE.findall(updated)), 1)
    self.assertEqual(self.FEED_DATE_FORMAT_RE.findall(updated)[0], updated)

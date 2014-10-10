"""CAP Collector core utils tests."""

__author__ = "arcadiy@google.com (Arkadii Yakovets)"

import datetime
import os
import unittest

from core import utils
from dateutil import parser
from django.conf import settings
from django.core.urlresolvers import reverse
from lxml import etree
import mock
import pytz
from tests import UUID_RE
import xmlsec


class UtilsTests(unittest.TestCase):
  """Utils unit tests."""
  TEST_USER_NAME = "test_user"
  DRAFT_ALERT_UUID = "a453f4bb-3249-45f6-8ddc-360da19fcc03"
  VALID_ALERT_UUID = "3ff7a28e-44b7-4ca5-aa5f-06dc42e474c1"

  @property
  def valid_alert_content(self):
    file_path = os.path.join(settings.GOLDEN_ALERTS_DATA_DIR,
                             self.VALID_ALERT_UUID + ".xml")
    with open(file_path, "r") as golden_file:
      xml_string = golden_file.read()
    return xml_string

  @property
  def partial_alert_content(self):
    file_path = os.path.join(settings.TEMPLATES_TESTDATA_DIR,
                             "message/test_msg1.xml")
    with open(file_path, "r") as golden_file:
      xml_string = golden_file.read()
    return xml_string

  @property
  def draft_alert_content(self):
    file_path = os.path.join(settings.GOLDEN_ALERTS_DATA_DIR,
                             self.DRAFT_ALERT_UUID + ".xml")
    with open(file_path, "r") as draft_file:
      xml_string = draft_file.read()
    return xml_string

  @property
  def invalid_alert_content(self):
    return "<my invalid xml>LMX</xml>"

  def test_parse_valid_alert(self):
    """Tests if valid XML alert parsed correctly."""
    file_name = self.VALID_ALERT_UUID + ".xml"
    golden_alert_dict = {
        "circles": [],
        "updated": parser.parse("2014-08-16T00:32:11+00:00"),
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
        "title": "Some hedline.",
        "area_desc": "This and that area.",
        "certainty": "Observed",
        "polys": [],
        "urgency": "Immediate"
    }
    alert_dict = utils.ParseAlert(self.valid_alert_content, "xml", file_name)
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
        "msg_type": "Update",
        "category": "Env",
        "certainty": "Possible",
        "urgency": "Expected",
        "title": "Alert Message",  # Default.
        "link": "%s%s" % (settings.SITE_URL,
                          reverse("alert", args=[file_name, "xml"])),
    }
    alert_dict = utils.ParseAlert(self.partial_alert_content, "xml", file_name)
    for key in alert_dict:
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
    uuid, is_valid, error = utils.CreateAlert(self.draft_alert_content,
                                              self.TEST_USER_NAME)
    self.assertTrue(UUID_RE.match(uuid))
    self.assertTrue(is_valid)
    self.assertEquals(error, None)

    file_name = uuid + ".xml"
    file_path = os.path.join(settings.ACTIVE_ALERTS_DATA_DIR, file_name)
    with open(file_path, "r") as alert_file:
      xml_string = alert_file.read()
    alert_dict = utils.ParseAlert(xml_string, "xml", file_name)
    draft_dict = utils.ParseAlert(self.draft_alert_content, "xml", file_name)
    # Remove alert IDs due to their random nature.
    del alert_dict["alert_id"]
    del draft_dict["alert_id"]
    self.assertDictEqual(alert_dict, draft_dict)
    # Delete test alert.
    os.unlink(file_path)
    self.assertFalse(os.path.exists(file_path))

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
    self.assertTrue(uuid in utils.GenerateFeed())

    # Delete test alert.
    file_path = os.path.join(settings.ACTIVE_ALERTS_DATA_DIR, uuid + ".xml")
    os.unlink(file_path)
    self.assertFalse(os.path.exists(file_path))

  @mock.patch("core.utils.GetCurrentDate",
              lambda: datetime.datetime(2014, 8, 10, 23, 55, 13, 0, pytz.utc))
  def test_generate_feed_inactive_alert(self):
    """Tests XML feed with date after alert expiration date.

       Expiration date is 2014-08-10T23:55:12+00:00.
    """
    uuid, _, _ = utils.CreateAlert(self.draft_alert_content,
                                   self.TEST_USER_NAME)
    self.assertFalse(uuid in utils.GenerateFeed())

    # Delete test alert.
    file_path = os.path.join(settings.INACTIVE_ALERTS_DATA_DIR, uuid + ".xml")
    os.unlink(file_path)
    self.assertFalse(os.path.exists(file_path))

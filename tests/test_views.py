"""CAP Collector core views tests."""

__author__ = "arcadiy@google.com (Arkadii Yakovets)"

import os
import unittest

from core import utils
from django.conf import settings
from django.test import Client

from tests import CAPCollectorLiveServer
from tests import UUID_RE


class SmokeTests(unittest.TestCase):

  def setUp(self):
    self.client = Client()

  def test_feed_xml(self):
    """Tests that XML feed opens with no erorrs."""
    response = self.client.get("/feed.xml")
    self.assertEqual(response.status_code, 200)

  def test_malformed_alert_post(self):
    """Tests if error occurs on malformed alert request attempt."""
    # No xml field.
    response = self.client.post("/post/", {"uid": "john", "password": "smith"})
    self.assertEqual(response.status_code, 400)

    # No password field.
    response = self.client.post("/post/", {"uid": "john", "xml": "<some_xml>"})
    self.assertEqual(response.status_code, 400)

    # No uid field.
    response = self.client.post("/post/", {"password": "smith",
                                           "xml": "<some_xml>"})
    self.assertEqual(response.status_code, 400)


class End2EndTests(CAPCollectorLiveServer):

  contact = "web@driver.com"
  sender_name = "Mr. Web Driver"
  instruction = "Instructions: what should affected people do."

  def test_end2end_alert_creation(self):
    """Emulates alert creation process using webdriver.

       Afrer webdriver part is done it checks whether alert file has created
       in active alerts directory and deletes alert file after that.
    """

    golden_dict = {
        "category": "Geo",
        "response_type": "Avoid",
        "urgency": "Expected",
        "severity": "Moderate",
        "certainty": "Likely",
        "title": "Some really informative alert headline",
        "area_desc": "This and that area"
    }

    self.webdriver.get(self.live_server_url)
    # Alert tab.
    self.GoToAlertTab()

    self.SetCategory(golden_dict["category"])
    self.assertEqual(golden_dict["category"], self.GetCategory())

    self.SetResponseType(golden_dict["response_type"])
    self.assertEqual(golden_dict["response_type"], self.GetResponseType())

    self.SetUrgency(golden_dict["urgency"])
    self.assertEqual(golden_dict["urgency"], self.GetUrgency())

    self.SetSeverity(golden_dict["severity"])
    self.assertEqual(golden_dict["severity"], self.GetSeverity())

    self.SetCertainty(golden_dict["certainty"])
    self.assertEqual(golden_dict["certainty"], self.GetCertainty())

    # Message tab.
    self.GoToMessageTab()
    self.SetHeadline(golden_dict["title"])
    self.SetAlertSenderName(self.sender_name)
    self.SetInstruction(self.instruction)
    self.SetContact(self.contact)

    # Area tab.
    self.GoToAreaTab()
    self.SetArea(golden_dict["area_desc"])

    # Release tab.
    self.GoToReleaseTab()
    self.SetUsername(self.TEST_USER_LOGIN)
    self.SetPassword(self.TEST_USER_PASSWORD)
    self.ReleaseAlert()

    uuid = UUID_RE.findall(self.GetUuid())[0]
    golden_dict["alert_id"] = uuid
    alert_file_path = os.path.join(
        settings.ACTIVE_ALERTS_DATA_DIR, uuid + ".xml")
    self.assertTrue(os.path.exists(alert_file_path))
    self.test_alert_file_paths.append(alert_file_path)

    # Ensure that feed contains new alert.
    response = self.client.get("/feed.xml")
    self.assertContains(response, uuid)

    # Check alert XML against initial values.
    file_name = uuid + ".xml"
    file_path = os.path.join(settings.ACTIVE_ALERTS_DATA_DIR, file_name)
    with open(file_path, "r") as alert_file:
      xml_string = alert_file.read()

    alert_dict = utils.ParseAlert(xml_string, "xml", file_name)
    for key in golden_dict:
      self.assertEqual(alert_dict[key], golden_dict[key])

    self.assertEqual(alert_dict["circles"], [])  # No circles.
    self.assertEqual(alert_dict["polys"], [])  # No polys.
    self.assertEqual(alert_dict["response_type"], "Avoid")
    self.assertEqual(alert_dict["severity"], "Moderate")
    self.assertEqual(alert_dict["category"], "Geo")
    self.assertEqual(alert_dict["certainty"], "Likely")

  def test_end2end_alert_from_template(self):
    """Emulates alert from template creation process using webdriver.

       Afrer webdriver part is done it checks whether alert file has created
       in active alerts directory and deletes alert file after that.
    """

    self.webdriver.get(self.live_server_url)

    # Alert tab.
    self.GoToAlertTab()
    self.SetMessageTemplate(1)

    # Message tab.
    self.GoToMessageTab()
    self.SetAlertSenderName(self.sender_name)
    self.SetContact(self.contact)

    # Area tab.
    self.GoToAreaTab()
    self.SetAreaTemplate(1)

    # Release tab.
    self.GoToReleaseTab()
    self.SetUsername(self.TEST_USER_LOGIN)
    self.SetPassword(self.TEST_USER_PASSWORD)
    self.ReleaseAlert()

    uuid = UUID_RE.findall(self.GetUuid())[0]
    alert_file_path = os.path.join(
        settings.ACTIVE_ALERTS_DATA_DIR, uuid + ".xml")
    self.assertTrue(os.path.exists(alert_file_path))
    self.test_alert_file_paths.append(alert_file_path)

    # Ensure that feed contains new alert.
    response = self.client.get("/feed.xml")
    self.assertContains(response, uuid)

    # Check alert XML against initial values.
    file_name = uuid + ".xml"
    file_path = os.path.join(settings.ACTIVE_ALERTS_DATA_DIR, file_name)
    with open(file_path, "r") as alert_file:
      alert_xml_string = alert_file.read()

    message_template_path = os.path.join(settings.TEMPLATES_DIR,
                                         "message/test_msg1.xml")
    with open(message_template_path, "r") as template_file:
      message_template_xml_string = template_file.read()

    area_template_path = os.path.join(settings.TEMPLATES_DIR,
                                      "area/test_area1.xml")
    with open(area_template_path, "r") as template_file:
      area_template_xml_string = template_file.read()

    alert_dict = utils.ParseAlert(alert_xml_string, "xml", file_name)
    message_dict = utils.ParseAlert(message_template_xml_string, "xml",
                                    file_name)
    area_dict = utils.ParseAlert(area_template_xml_string, "xml", file_name)

    # Message template assertions.
    for key in message_dict:
      if not message_dict[key]:
        continue  # We need values present in both template and alert files.
      self.assertEqual(alert_dict[key], message_dict[key])

    # Area template assertions.
    for key in area_dict:
      if not area_dict[key]:
        continue  # We need values present in both template and alert files.
      self.assertEqual(alert_dict[key], area_dict[key])

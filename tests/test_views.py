"""CAP Collector core views tests."""

__author__ = "arcadiy@google.com (Arkadii Yakovets)"

from core import models
from core import utils
from django.conf import settings
from django.core.urlresolvers import reverse
from django.test import Client
from tests import CAPCollectorLiveServer
from tests import TestBase
from tests import UUID_RE


class SmokeTests(TestBase):
  """Basic views tests."""

  fixtures = ["test_alerts.json", "test_auth.json", "test_templates.json"]

  def setUp(self):
    super(SmokeTests, self).setUp()
    self.client = Client()

  def login(self):
    self.client.post("/login/", {"username": self.TEST_USER_LOGIN,
                                 "password": self.TEST_USER_PASSWORD})

  def test_feed_xml(self):
    """Tests that XML feed opens with no erorrs."""
    response = self.client.get("/feed.xml")
    self.assertEqual(response.status_code, 200)

  def test_malformed_alert_post(self):
    """Tests if error occurs on malformed alert request attempt."""
    self.login()
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

  def test_alert_xml_does_not_exist(self):
    """Tests proper handling for invalid alert IDs."""
    response = self.client.get("/feed/1111-12-12.xml")
    self.assertEqual(response.status_code, 404)

  def test_alert_html_does_not_exist(self):
    """Tests proper handling for invalid alert IDs."""
    response = self.client.get("/feed/1111-12-12.html")
    self.assertEqual(response.status_code, 404)

  def test_index_page_context(self):
    self.login()
    response = self.client.get("/")
    self.assertEquals(response.context['map_default_viewport'],
                      settings.MAP_DEFAULT_VIEWPORT)


class End2EndTests(CAPCollectorLiveServer):
  """End to end views tests."""

  contact = "web@driver.com"
  sender_name = "Mr. Web Driver"
  instruction = "Instructions: what should affected people do."

  def CheckValues(self, uuid, initial_dict, is_update=False):
    """Asserts that initial and parsed data is equal.

    Args:
      uuid: (string) Alert UUID, assumed to be the filename of the alert XML.
      initial_dict: (dict) Initial alert data dictionary.
      is_update: (bool) Whether to check new or updated alert values.
    Returns:
      Parsed alerts dictionary.
    """

    alert = models.Alert.objects.get(uuid=uuid)

    alert_dict = utils.ParseAlert(alert.content, "xml", uuid)
    for key in initial_dict:
      if is_update and key in ("area_desc", "title", "event",):
        continue
      self.assertEqual(alert_dict[key], initial_dict[key])
    return alert_dict

  def CreateAlert(self, golden_dict, expiration=None, skip_login=False,
                  update=False):
    """Creates alert based on passed dictionary. Supports log in when needed."""
    if not skip_login:
      self.webdriver.get(self.live_server_url)
      self.GoToAlertsTab()
      self.Login()

    if not update:
      # Alert tab.
      self.GoToAlertTab()

    self.SetCategory(golden_dict["category"])
    self.SetResponseType(golden_dict["response_type"])
    self.SetUrgency(golden_dict["urgency"])
    self.SetSeverity(golden_dict["severity"])
    self.SetCertainty(golden_dict["certainty"])
    if expiration:
      self.SetExpiration(expiration)

    # Message tab.
    self.GoToMessageTab()
    if "language" in golden_dict:
      self.SetLanguage(golden_dict["language"])
    self.SetHeadline(golden_dict["title"])
    if "event" in golden_dict:
      self.SetEvent(golden_dict["event"])
    self.SetAlertSenderName(self.sender_name)
    self.SetInstruction(self.instruction)
    self.SetContact(self.contact)
    if "web" in golden_dict:
      self.SetWeb(golden_dict["web"])

    # Area tab.
    self.GoToAreaTab()
    self.SetArea(golden_dict["area_desc"])

    # Release tab.
    self.GoToReleaseTab()
    self.SetUsername(self.TEST_USER_LOGIN)
    self.SetPassword(self.TEST_USER_PASSWORD)
    self.ReleaseAlert()

    return UUID_RE.findall(self.GetUuid())[0]

  def test_end2end_alert_create(self):
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
        "web": "http://my.custom.uri",
        "title": "Some really informative alert headline",
        "event": "And alert event",
        "language": "pt",
        "area_desc": "This and that area"
    }

    expiration_minutes = 120
    uuid = self.CreateAlert(golden_dict, expiration=expiration_minutes)

    golden_dict["alert_id"] = uuid
    self.assertTrue(models.Alert.objects.filter(uuid=uuid).exists())

    # Ensure that feed contains new alert.
    response = self.client.get("/feed.xml")
    self.assertContains(response, uuid)
    alert_dict = self.CheckValues(uuid, golden_dict)
    alert_sent_at = alert_dict["sent"]
    alert_expires_at = alert_dict["expires"]
    self.assertEqual((alert_expires_at - alert_sent_at).seconds / 60,
                     expiration_minutes)

  def test_end2end_alert_update(self):
    """Emulates existing alert update process using webdriver."""
    initial_dict = {
        "category": "Geo",
        "response_type": "Avoid",
        "urgency": "Expected",
        "severity": "Moderate",
        "certainty": "Likely",
        "title": "Alert that will be updated",
        "area_desc": "This and that area",
    }

    update_dict = {
        "category": "Geo",
        "response_type": "Evacuate",
        "urgency": "Immediate",
        "severity": "Extreme",
        "certainty": "Observed",
        "title": "Previous alert update",
        "area_desc": "Some new area",
    }

    # Create initial alert.
    uuid = self.CreateAlert(initial_dict)
    initial_dict["alert_id"] = uuid
    self.assertTrue(models.Alert.objects.filter(uuid=uuid).exists())

    # Ensure that feed contains new alert.
    response = self.client.get("/feed.xml")
    self.assertContains(response, uuid)
    initial_alert_dict = self.CheckValues(uuid, initial_dict)
    sent_at = initial_alert_dict["sent"]
    initial_alert_reference = "%s@%s,%s,%s" % (self.TEST_USER_LOGIN,
                                               settings.SITE_DOMAIN,
                                               uuid, sent_at.isoformat())
    # Create alert update.
    self.GoToAlertsTab()
    self.OpenLatestAlert()
    self.ClickUpdateAlertButton()
    uuid = self.CreateAlert(update_dict, skip_login=True, update=True)
    self.assertTrue(models.Alert.objects.filter(uuid=uuid).exists())

    updated_alert_dict = self.CheckValues(uuid, update_dict, is_update=True)
    self.assertEqual(updated_alert_dict["msg_type"], "Update")
    sent_at = updated_alert_dict["sent"]
    expires_at = updated_alert_dict["expires"]
    self.assertEqual((expires_at - sent_at).seconds / 60, 60)
    updated_alert_references = updated_alert_dict["references"]
    self.assertEqual(initial_alert_reference, updated_alert_references)
    self.assertEqual(updated_alert_dict["title"],
                     initial_alert_dict["title"] + update_dict["title"])

  def test_end2end_alert_cancel(self):
    """Emulates existing alert cancellation process using webdriver."""
    initial_dict = {
        "category": "Geo",
        "response_type": "Avoid",
        "urgency": "Expected",
        "severity": "Moderate",
        "certainty": "Likely",
        "title": "Alert that will be cancelled",
        "area_desc": "This and that area"
    }

    # Create initial alert.
    uuid = self.CreateAlert(initial_dict)
    initial_dict["alert_id"] = uuid
    self.assertTrue(models.Alert.objects.filter(uuid=uuid).exists())

    # Ensure that feed contains new alert.
    response = self.client.get("/feed.xml")
    self.assertContains(response, uuid)
    initial_alert_dict = self.CheckValues(uuid, initial_dict)
    sent_at = initial_alert_dict["sent"]
    initial_alert_reference = "%s@%s,%s,%s" % (self.TEST_USER_LOGIN,
                                               settings.SITE_DOMAIN,
                                               uuid, sent_at.isoformat())
    # Create alert update.
    self.GoToAlertsTab()
    self.OpenLatestAlert()
    self.ClickCancelAlertButton()
    self.GoToMessageTab()
    self.GoToAreaTab()
    self.GoToReleaseTab()
    self.SetUsername(self.TEST_USER_LOGIN)
    self.SetPassword(self.TEST_USER_PASSWORD)
    self.ReleaseAlert()
    uuid = UUID_RE.findall(self.GetUuid())[0]

    initial_dict["alert_id"] = uuid
    self.assertTrue(models.Alert.objects.filter(uuid=uuid).exists())

    # TODO(arcadiy): make sure the workflow is correct.
    del initial_dict["title"]  # Currently title is omitted.
    canceled_alert_dict = self.CheckValues(uuid, initial_dict)
    self.assertEqual(canceled_alert_dict["msg_type"], "Cancel")
    sent_at = canceled_alert_dict["sent"]
    expires_at = canceled_alert_dict["expires"]
    self.assertEqual((expires_at - sent_at).seconds / 60, 60)
    canceled_alert_references = canceled_alert_dict["references"]
    self.assertEqual(initial_alert_reference, canceled_alert_references)

  def test_end2end_alert_create_from_template(self):
    """Emulates alert from template creation process using webdriver.

       Afrer webdriver part is done it checks whether alert file has created
       in active alerts directory and deletes alert file after that.
    """

    self.GoToAlertsTab()
    self.Login()

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

    alert_uuid = UUID_RE.findall(self.GetUuid())[0]
    self.assertTrue(models.Alert.objects.filter(uuid=alert_uuid).exists())

    # Ensure that feed contains new alert.
    response = self.client.get("/feed.xml")
    self.assertContains(response, alert_uuid)

    # Check alert XML against initial values.
    alert = models.Alert.objects.get(uuid=alert_uuid)
    message_template_xml = models.MessageTemplate.objects.get(id=1).content
    area_template_xml = models.AreaTemplate.objects.get(id=1).content
    alert_dict = utils.ParseAlert(alert.content, "xml", alert_uuid)
    message_dict = utils.ParseAlert(message_template_xml, "xml", alert_uuid)
    area_dict = utils.ParseAlert(area_template_xml, "xml", alert_uuid)

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

    # Check web field is set to default.
    alert_default_web = "%s%s" % (settings.SITE_URL,
                                  reverse("alert", args=[alert_uuid, "html"]))
    self.assertEqual(alert_dict["web"], alert_default_web)

  def test_ui_language_change(self):
    """Emulates UI language change process using webdriver."""

    self.GoToAlertsTab()
    self.Login()

    self.GoToAlertTab()
    self.GoToMessageTab()
    language = settings.LANGUAGES[1]  # Hindi.
    self.SetUserLanguage(language[0])
    self.assertEquals(self.GetLanguage(), language[1])

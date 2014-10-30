"""CAP Collector tests base classes."""

__author__ = "arcadiy@google.com (Arkadii Yakovets)"

import os
import re

from django.conf import settings
from django.contrib.auth.models import Group
from django.contrib.auth.models import User
from django.test import Client
from django.test import LiveServerTestCase
from django.test import TestCase
from selenium.webdriver.firefox.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait


UUID_RE = re.compile(
    r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}")


class TestBase(TestCase):
  """Base class for other tests."""

  TEST_USER_EMAIL = "mr.web@driver.com"
  TEST_USER_LOGIN = "web_driver"
  TEST_USER_PASSWORD = "test_password"

  def setUp(self):
    self.test_user = User.objects.get(username=self.TEST_USER_LOGIN)


class CAPCollectorLiveServer(TestBase, LiveServerTestCase):
  """Base class for live server tests."""
  fixtures = ["test_alerts.json", "test_auth.json", "test_templates.json"]

  LATEST_ALERT_XPATH = "//*[@id='current_alerts_span']/a"
  UPDATE_ALERT_BUTTON_XPATH = "//*[@id='update_button']"
  CANCEL_ALERT_BUTTON_XPATH = "//*[@id='cancel_button']"

  ISSUE_NEW_ALERT_BUTTON_XPATH = "//*[@id='current-next-button']/span"
  ADD_ALERT_DETAILS_BUTTON_XPATH = "//*[@id='alert-next-button']/span"
  TARGET_AREA_BUTTON_XPATH = "//*[@id='info-next-button']/span"
  RELEASE_BUTTON_XPATH = "//*[@id='area-next-button']/span"
  RELEASE_ALERT_BUTTON_XPATH = "//*[@id='release']/div[2]/a/span"

  MESSAGE_TEMPLATE_ELEMENT = "//*[@id='select-message-template']"
  MESSAGE_TEMPLATE_ITEMS_XPATH = "//*[@id='select-message-template']/option[%s]"

  CATEGORY_SELECT_ELEMENT = "//*[@id='select-categories']"
  CATEGORY_KEYS = ("geo", "met", "safety", "security", "rescue", "fire",
                   "health", "env", "transport", "infra", "cbrne", "other")
  CATEGORY_XPATHS = {
      key: "//*[@id='select-categories']/option[%s]" % (index + 2)
      for index, key in enumerate(CATEGORY_KEYS)}

  RESPONSE_TYPE_SELECT_ELEMENT = "//*[@id='select-responseTypes']"
  RESPONSE_TYPE_KEYS = ("shelter", "evacuate", "prepare", "execute", "avoid",
                        "monitor", "assess", "allclear", "none")
  RESPONSE_TYPE_XPATHS = {
      key: "//*[@id='select-responseTypes']/option[%s]" % (index + 2)
      for index, key in enumerate(RESPONSE_TYPE_KEYS)}

  URGENCY_SELECT_ELEMENT = "//*[@id='select-urgency']"
  URGENCY_KEYS = ("immediate", "expected", "future", "past", "unknown")
  URGENCY_XPATHS = {
      key: "//*[@id='select-urgency']/option[%s]" % (index + 2)
      for index, key in enumerate(URGENCY_KEYS)}

  SEVERITY_SELECT_ELEMENT = "//*[@id='select-severity']"
  SEVERITY_KEYS = ("extreme", "severe", "moderate", "minor", "unknown")
  SEVERITY_XPATHS = {
      key: "//*[@id='select-severity']/option[%s]" % (index + 2)
      for index, key in enumerate(SEVERITY_KEYS)}

  CERTAINTY_SELECT_ELEMENT = "//*[@id='select-certainty']"
  CERTAINTY_KEYS = ("observed", "likely", "possible", "unlikely", "unknown")
  CERTAINTY_XPATHS = {
      key: "//*[@id='select-certainty']/option[%s]" % (index + 2)
      for index, key in enumerate(CERTAINTY_KEYS)}

  EXPIRATION_SELECT_ELEMENT = "//*[@id='select-expires-min']"
  EXPIRATION_XPATHS = {
      120: "//*[@id='select-expires-min']/option[6]",
  }

  # Message tab.
  ALERT_LANGUAGE_ELEMENT = ("//*[@id='info']/div[2]/div[1]/div/div/span/"
                            "span[1]/span")
  ALERT_LANGUAGE_XPATHS = {
      language_tuple[0]: "//*[@id='select-language']/option[%s]" % (index + 1)
      for index, language_tuple in enumerate(settings.LANGUAGES)
  }
  ALERT_SENDER_ELEMENT_NAME = "text-senderName"
  HEADLINE_ELEMENT_NAME = "text-headline"
  EVENT_ELEMENT_NAME = "text-event"
  DESCRIPTION_ELEMENT_NAME = "textarea-description"
  INSTRUCTION_ELEMENT_NAME = "textarea-instruction"
  CONTACT_ELEMENT_NAME = "text-contact"
  WEB_ELEMENT_NAME = "text-web"

  # Area tab.
  AREA_TEMPLATE_ELEMENT = "//*[@id='select-area-template']"
  AREA_TEMPLATE_ITEMS_XPATH = "//*[@id='select-area-template']/option[%s]"
  AREA_ELEMENT_NAME = "textarea-areaDesc"
  AREA_GEOCODE_ADD_BUTTON_XPATH = "//*[@id='geocode_div']/a"
  AREA_GEOCODE_NAME_XPATH = "//*[@id='geocode_div']/div/div[1]/div[2]/input"
  AREA_GEOCODE_VALUE_XPATH = "//*[@id='geocode_div']/div/div[2]/div[2]/input"

  # Release tab.
  USERNAME_ELEMENT_XPATH = "//*[@id='text-uid']"
  PASSWORD_ELEMENT_XPATH = "//*[@id='text-pwd']"
  UUID_ELEMENT_XPATH = "//*[@id='response_uuid']"
  AUTH_USERNAME_ELEMENT_NAME = "username"
  AUTH_PASSWORD_ELEMENT_NAME = "password"
  AUTH_BUTTON_XPATH = "/html/body/form/div/input[3]"

  USER_LANGUAGE_ELEMENT = "//*[@id='info']/div[1]/div/div/div"
  USER_LANGUAGE_XPATHS = {
      language_tuple[0]: "//*[@id='ui-language']/option[%s]" % (index + 1)
      for index, language_tuple in enumerate(settings.LANGUAGES)
  }

  ALERT_TAB_REQUIRED_PLACEHOLDER_XPATH = "//*[@id='alert']/div[2]/span"

  MESSAGE_TAB_REQUIRED_PLACEHOLDER_XPATH = "//*[@id='info']/div[2]/div[11]"
  AREA_TAB_REQUIRED_PLACEHOLDER_XPATH = "//*[@id='area']/div[2]/div[8]"

  MESSAGE_TAB_INVALID_PLACEHOLDER_XPATH = (
      "//*[@id='info']/div[2]/div[12]")
  AREA_TAB_INVALID_PLACEHOLDER_XPATH = "//*[@id='area']/div[2]/div[9]"
  AREA_TAB_REQUIRED_COMBINED_PLACEHOLDER_XPATH = (
      "//*[@id='area']/div[2]/div[10]")
  AREA_TAB_MAP_VISIBLE_ELEMENT_ID = "OpenLayers_Control_MaximizeDiv_innerImage"

  @classmethod
  def setUpClass(cls):
    cls.client = Client()
    cls.webdriver = WebDriver()
    super(CAPCollectorLiveServer, cls).setUpClass()

  @classmethod
  def tearDownClass(cls):
    cls.webdriver.quit()
    super(CAPCollectorLiveServer, cls).tearDownClass()

  def WaitUntilVisible(self, xpath, by=By.XPATH, timeout=5):
    return WebDriverWait(self.webdriver, timeout).until(
        ec.visibility_of_element_located((by, xpath)))

  def Clear(self, element):
    return element.clear()

  def WaitUntilMapVisible(self):
    self.WaitUntilVisible(self.AREA_TAB_MAP_VISIBLE_ELEMENT_ID, by=By.ID)

  @property
  def latest_alert_link(self):
    return self.WaitUntilVisible(self.LATEST_ALERT_XPATH)

  @property
  def update_alert_button(self):
    return self.WaitUntilVisible(self.UPDATE_ALERT_BUTTON_XPATH)

  @property
  def cancel_alert_button(self):
    return self.WaitUntilVisible(self.CANCEL_ALERT_BUTTON_XPATH)

  @property
  def issue_new_alert_button(self):
    return self.WaitUntilVisible(self.ISSUE_NEW_ALERT_BUTTON_XPATH)

  @property
  def add_alert_details_button(self):
    return self.WaitUntilVisible(self.ADD_ALERT_DETAILS_BUTTON_XPATH)

  @property
  def target_area_button(self):
    return self.WaitUntilVisible(self.TARGET_AREA_BUTTON_XPATH)

  @property
  def release_button(self):
    return self.WaitUntilVisible(self.RELEASE_BUTTON_XPATH)

  @property
  def release_alert_button(self):
    return self.WaitUntilVisible(self.RELEASE_ALERT_BUTTON_XPATH)

  @property
  def alert_tab_required_placeholder(self):
    return self.webdriver.find_element_by_xpath(
        self.ALERT_TAB_REQUIRED_PLACEHOLDER_XPATH)

  @property
  def message_tab_required_placeholder(self):
    return self.webdriver.find_element_by_xpath(
        self.MESSAGE_TAB_REQUIRED_PLACEHOLDER_XPATH)

  @property
  def message_tab_invalid_placeholder(self):
    return self.webdriver.find_element_by_xpath(
        self.MESSAGE_TAB_INVALID_PLACEHOLDER_XPATH)

  @property
  def area_tab_required_placeholder(self):
    return self.webdriver.find_element_by_xpath(
        self.AREA_TAB_REQUIRED_PLACEHOLDER_XPATH)

  @property
  def area_tab_invalid_placeholder(self):
    return self.webdriver.find_element_by_xpath(
        self.AREA_TAB_INVALID_PLACEHOLDER_XPATH)

  @property
  def area_tab_required_combined_placeholder(self):
    return self.webdriver.find_element_by_xpath(
        self.AREA_TAB_REQUIRED_COMBINED_PLACEHOLDER_XPATH)

  @property
  def area_geocode_add_button(self):
    return self.webdriver.find_element_by_xpath(
        self.AREA_GEOCODE_ADD_BUTTON_XPATH)

  @property
  def area_geocode_name_element(self):
    return self.webdriver.find_element_by_xpath(self.AREA_GEOCODE_NAME_XPATH)

  @property
  def area_geocode_value_element(self):
    return self.webdriver.find_element_by_xpath(self.AREA_GEOCODE_VALUE_XPATH)

  @property
  def message_template_select(self):
    return self.WaitUntilVisible(self.MESSAGE_TEMPLATE_ELEMENT)

  @property
  def category_select(self):
    return self.find_element_by_xpath(self.CATEGORY_SELECT_ELEMENT)

  @property
  def response_type_select(self):
    return self.webdriver.find_element_by_xpath(
        self.RESPONSE_TYPE_SELECT_ELEMENT)

  @property
  def urgency_select(self):
    return self.webdriver.find_element_by_xpath(self.URGENCY_SELECT_ELEMENT)

  @property
  def severity_select(self):
    return self.webdriver.find_element_by_xpath(self.SEVERITY_SELECT_ELEMENT)

  @property
  def certainty_select(self):
    return self.webdriver.find_element_by_xpath(self.CERTAINTY_SELECT_ELEMENT)

  @property
  def expiration_select(self):
    return self.webdriver.find_element_by_xpath(self.EXPIRATION_SELECT_ELEMENT)

  @property
  def language_select(self):
    return self.WaitUntilVisible(self.ALERT_LANGUAGE_ELEMENT)

  @property
  def sender_element(self):
    return self.WaitUntilVisible(self.ALERT_SENDER_ELEMENT_NAME, by=By.NAME)

  @property
  def headline_element(self):
    return self.WaitUntilVisible(self.HEADLINE_ELEMENT_NAME, by=By.NAME)

  @property
  def event_element(self):
    return self.WaitUntilVisible(self.EVENT_ELEMENT_NAME, by=By.NAME)

  @property
  def description_element(self):
    return self.webdriver.find_element_by_name(self.DESCRIPTION_ELEMENT_NAME)

  @property
  def instruction_element(self):
    return self.webdriver.find_element_by_name(self.INSTRUCTION_ELEMENT_NAME)

  @property
  def contact_element(self):
    return self.webdriver.find_element_by_name(self.CONTACT_ELEMENT_NAME)

  @property
  def web_element(self):
    return self.webdriver.find_element_by_name(self.WEB_ELEMENT_NAME)

  @property
  def area_template_select(self):
    return self.WaitUntilVisible(self.AREA_TEMPLATE_ELEMENT)

  @property
  def area_element(self):
    return self.WaitUntilVisible(self.AREA_ELEMENT_NAME, by=By.NAME)

  @property
  def username_element(self):
    return self.WaitUntilVisible(self.USERNAME_ELEMENT_XPATH)

  @property
  def password_element(self):
    return self.webdriver.find_element_by_xpath(self.PASSWORD_ELEMENT_XPATH)

  @property
  def uuid_element(self):
    return self.WaitUntilVisible(self.UUID_ELEMENT_XPATH)

  @property
  def auth_username_element(self):
    return self.webdriver.find_element_by_name(self.AUTH_USERNAME_ELEMENT_NAME)

  @property
  def auth_password_element(self):
    return self.webdriver.find_element_by_name(self.AUTH_PASSWORD_ELEMENT_NAME)

  @property
  def user_language_select(self):
    return self.WaitUntilVisible(self.USER_LANGUAGE_ELEMENT)

  def GoToAlertsTab(self):
    self.webdriver.get(self.live_server_url)

  def GoToAlertTab(self):
    self.issue_new_alert_button.click()

  def GoToMessageTab(self):
    self.add_alert_details_button.click()

  def GoToAreaTab(self):
    self.target_area_button.click()

  def GoToReleaseTab(self):
    self.release_button.click()

  def OpenLatestAlert(self):
    self.latest_alert_link.click()

  def ClickUpdateAlertButton(self):
    self.update_alert_button.click()

  def ClickCancelAlertButton(self):
    self.cancel_alert_button.click()

  def ReleaseAlert(self):
    self.release_alert_button.click()

  def SetMessageTemplate(self, template_item_number):
    message_template_xpath = (self.MESSAGE_TEMPLATE_ITEMS_XPATH %
                              (template_item_number + 1))
    menu_item = self.WaitUntilVisible(message_template_xpath)
    menu_item.click()

  def GetMessageTemplate(self):
    return self.message_template_select.get_attribute("value")

  def SetCategory(self, category):
    category_xpath = self.CATEGORY_XPATHS.get(category.lower())
    menu_item = self.WaitUntilVisible(category_xpath)
    menu_item.click()

  def GetCategory(self):
    return self.category_select.get_attribute("value")

  def SetResponseType(self, response_type):
    response_type_xpath = self.RESPONSE_TYPE_XPATHS.get(response_type.lower())
    menu_item = self.WaitUntilVisible(response_type_xpath)
    menu_item.click()

  def GetResponseType(self):
    return self.response_type_select.get_attribute("value")

  def SetUrgency(self, urgency):
    urgency_xpath = self.URGENCY_XPATHS.get(urgency.lower())
    self.webdriver.find_element_by_xpath(urgency_xpath).click()

  def GetUrgency(self):
    return self.urgency_select.get_attribute("value")

  def SetSeverity(self, severity):
    severity_xpath = self.SEVERITY_XPATHS.get(severity.lower())
    self.webdriver.find_element_by_xpath(severity_xpath).click()

  def GetExcipration(self):
    return self.expiration_select.get_attribute("value")

  def SetExpiration(self, expiration):
    expiration_xpath = self.EXPIRATION_XPATHS.get(expiration)
    if expiration_xpath:
      self.webdriver.find_element_by_xpath(expiration_xpath).click()

  def GetSeverity(self):
    return self.severity_select.get_attribute("value")

  def SetCertainty(self, certainty):
    certainty_xpath = self.CERTAINTY_XPATHS.get(certainty.lower())
    if certainty_xpath:
      self.webdriver.find_element_by_xpath(certainty_xpath).click()

  def GetCertainty(self):
    return self.certainty_select.get_attribute("value")

  def SetAreaTemplate(self, template_item_number):
    self.WaitUntilMapVisible()
    area_template_xpath = (self.AREA_TEMPLATE_ITEMS_XPATH %
                           (template_item_number + 1))
    menu_item = self.WaitUntilVisible(area_template_xpath)
    menu_item.click()

  def GetAreaTemplate(self):
    return self.area_template_select.get_attribute("value")

  def GetUuid(self):
    return self.uuid_element.text

  def GetLanguage(self):
    return self.language_select.text

  def SetLanguage(self, language):
    language_xpath = self.ALERT_LANGUAGE_XPATHS.get(language.lower())
    self.language_select.click()
    menu_item = self.WaitUntilVisible(language_xpath)
    menu_item.click()

  def SetAlertSenderName(self, sender_name):
    self.sender_element.send_keys(sender_name)

  def SetHeadline(self, head_line):
    self.Clear(self.headline_element)
    self.headline_element.send_keys(head_line)

  def ClearEvent(self):
    self.Clear(self.event_element)

  def SetEvent(self, event):
    self.event_element.send_keys(event)

  def ClearDescription(self):
    self.Clear(self.description_element)

  def SetDescription(self, description):
    self.description_element.send_keys(description)

  def ClearInstruction(self):
    self.Clear(self.instruction_element)

  def SetInstruction(self, instruction):
    self.instruction_element.send_keys(instruction)

  def SetContact(self, contact):
    self.contact_element.send_keys(contact)

  def SetWeb(self, url):
    self.web_element.send_keys(url)

  def ClearArea(self):
    self.Clear(self.area_element)

  def SetArea(self, area):
    self.WaitUntilMapVisible()
    self.Clear(self.area_element)
    self.area_element.send_keys(area)

  def SetGeocode(self, name, value):
    """Sets geocode. Supports only one geocode item."""
    self.WaitUntilMapVisible()
    self.area_geocode_add_button.click()
    self.area_geocode_name_element.send_keys(name)
    self.area_geocode_value_element.send_keys(value)

  def SetUsername(self, username):
    self.username_element.send_keys(username)

  def SetPassword(self, password):
    self.password_element.send_keys(password)

  def Login(self):
    self.auth_username_element.send_keys(self.TEST_USER_LOGIN)
    self.auth_password_element.send_keys(self.TEST_USER_PASSWORD)
    self.webdriver.find_element_by_xpath(self.AUTH_BUTTON_XPATH).click()

  def SetUserLanguage(self, language):
    self.user_language_select.click()
    language_xpath = self.ALERT_LANGUAGE_XPATHS.get(language)
    self.webdriver.find_element_by_xpath(language_xpath).click()

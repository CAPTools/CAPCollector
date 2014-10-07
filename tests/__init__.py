"""CAP Collector tests base classes."""

__author__ = "arcadiy@google.com (Arkadii Yakovets)"

import re

from django.contrib.auth.models import User
from django.test import Client
from django.test import LiveServerTestCase
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait


UUID_RE = re.compile(
    r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}")


class CAPCollectorLiveServer(LiveServerTestCase):
  """Base class for live server tests."""

  TEST_USER_EMAIL = "mr.web@driver.com"
  TEST_USER_LOGIN = "web_driver"
  TEST_USER_PASSWORD = "test_password"

  ISSUE_NEW_ALERT_BUTTON_XPATH = "//*[@id='current']/div[2]/a[1]/span"
  ADD_ALERT_DETAILS_BUTTON_XPATH = "//*[@id='alert']/div[2]/a/span"
  TARGET_AREA_BUTTON_XPATH = "//*[@id='info']/div[2]/a/span"
  RELEASE_BUTTON_XPATH = "//*[@id='area']/div[2]/a/span"
  RELEASE_ALERT_BUTTON_XPATH = "//*[@id='release_div']/div/a/span"

  CATEGORY_MENU_XPATH = "//*[@id='select-categories-button']/span"
  CATEGORY_SELECT_ELEMENT = "//*[@id='select-categories']"
  CATEGORY_KEYS = ("geo", "met", "safety", "security", "rescue", "fire",
                   "health", "env", "transport", "infra", "cbrne", "other")
  CATEGORY_XPATHS = {
      key: "//*[@id='select-categories-menu']/li[%s]/div/div/a" % (index + 2)
      for index, key in enumerate(CATEGORY_KEYS)}

  RESPONSE_TYPE_MENU_XPATH = "//*[@id='select-responseTypes-button']/span"
  RESPONSE_TYPE_SELECT_ELEMENT = "//*[@id='select-responseTypes']"
  RESPONSE_TYPE_KEYS = ("shelter", "evacuate", "prepare", "execute", "avoid",
                        "monitor", "assess", "allclear", "none")
  RESPONSE_TYPE_XPATHS = {
      key: "//*[@id='select-responseTypes-menu']/li[%s]/div/div/a" % (index + 2)
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

  # Message tab.
  ALERT_SENDER_ELEMENT_NAME = "text-senderName"
  HEADLINE_ELEMENT_NAME = "text-headline"
  DESCRIPTION_ELEMENT_NAME = "textarea-description"
  INSTRUCTION_ELEMENT_NAME = "textarea-instruction"
  CONTACT_ELEMENT_NAME = "text-contact"

  # Area tab.
  AREA_ELEMENT_NAME = "textarea-areaDesc"

  # Release tab.
  USERNAME_ELEMENT_XPATH = "//*[@id='text-uid']"
  PASSWORD_ELEMENT_XPATH = "//*[@id='text-pwd']"
  UUID_ELEMENT_XPATH = "//*[@id='response_uuid']"

  @classmethod
  def setUpClass(cls):
    cls.client = Client()
    cls.webdriver = WebDriver()
    super(CAPCollectorLiveServer, cls).setUpClass()

    User.objects.create_user(email=cls.TEST_USER_EMAIL,
                             username=cls.TEST_USER_LOGIN,
                             password=cls.TEST_USER_PASSWORD)

  @classmethod
  def tearDownClass(cls):
    cls.webdriver.quit()
    super(CAPCollectorLiveServer, cls).tearDownClass()

  @property
  def issue_new_alert_button(self):
    return self.webdriver.find_element_by_xpath(
        self.ISSUE_NEW_ALERT_BUTTON_XPATH)

  @property
  def add_alert_details_button(self):
    return self.webdriver.find_element_by_xpath(
        self.ADD_ALERT_DETAILS_BUTTON_XPATH)

  @property
  def target_area_button(self):
    return self.webdriver.find_element_by_xpath(
        self.TARGET_AREA_BUTTON_XPATH)

  @property
  def release_button(self):
    return WebDriverWait(self.webdriver, 5).until(
        ec.visibility_of_element_located(
            (By.XPATH, self.RELEASE_BUTTON_XPATH)))

  @property
  def release_alert_button(self):
    return WebDriverWait(self.webdriver, 5).until(
        ec.visibility_of_element_located(
            (By.XPATH, self.RELEASE_ALERT_BUTTON_XPATH)))

  @property
  def category_menu(self):
    return WebDriverWait(self.webdriver, 5).until(
        ec.visibility_of_element_located(
            (By.XPATH, self.CATEGORY_MENU_XPATH)))

  @property
  def category_selected(self):
    return self.webdriver.find_element_by_xpath(
        self.CATEGORY_SELECT_ELEMENT)

  @property
  def response_type_menu(self):
    return WebDriverWait(self.webdriver, 5).until(
        ec.visibility_of_element_located(
            (By.XPATH, self.RESPONSE_TYPE_MENU_XPATH)))

  @property
  def response_type_selected(self):
    return self.webdriver.find_element_by_xpath(
        self.RESPONSE_TYPE_SELECT_ELEMENT)

  @property
  def urgency_selected(self):
    return self.webdriver.find_element_by_xpath(self.URGENCY_SELECT_ELEMENT)

  @property
  def severity_selected(self):
    return self.webdriver.find_element_by_xpath(self.SEVERITY_SELECT_ELEMENT)

  @property
  def certainty_selected(self):
    return self.webdriver.find_element_by_xpath(self.CERTAINTY_SELECT_ELEMENT)

  @property
  def sender_element(self):
    return self.webdriver.find_element_by_name(self.ALERT_SENDER_ELEMENT_NAME)

  @property
  def headline_element(self):
    return self.webdriver.find_element_by_name(self.HEADLINE_ELEMENT_NAME)

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
  def area_element(self):
    return WebDriverWait(self.webdriver, 5).until(
        ec.visibility_of_element_located((By.NAME, self.AREA_ELEMENT_NAME)))

  @property
  def username_element(self):
    return WebDriverWait(self.webdriver, 5).until(
        ec.visibility_of_element_located(
            (By.XPATH, self.USERNAME_ELEMENT_XPATH)))

  @property
  def password_element(self):
    return self.webdriver.find_element_by_xpath(self.PASSWORD_ELEMENT_XPATH)

  @property
  def uuid_element(self):
    return WebDriverWait(self.webdriver, 5).until(
        ec.visibility_of_element_located((By.XPATH, self.UUID_ELEMENT_XPATH)))

  def GoToAlertTab(self):
    self.issue_new_alert_button.click()

  def GoToMessageTab(self):
    self.add_alert_details_button.click()

  def GoToAreaTab(self):
    self.target_area_button.click()

  def GoToReleaseTab(self):
    self.release_button.click()

  def ReleaseAlert(self):
    self.release_alert_button.click()

  def SetCategory(self, category):
    self.category_menu.click()
    category_xpath = self.CATEGORY_XPATHS.get(category.lower())
    menu_item = WebDriverWait(self.webdriver, 5).until(
        ec.visibility_of_element_located((By.XPATH, category_xpath)))
    menu_item.click()

  def GetCategory(self):
    return self.category_selected.get_attribute("value")

  def SetResponseType(self, response_type):
    self.response_type_menu.click()
    response_type_xpath = self.RESPONSE_TYPE_XPATHS.get(response_type.lower())
    menu_item = WebDriverWait(self.webdriver, 5).until(
        ec.visibility_of_element_located((By.XPATH, response_type_xpath)))
    menu_item.click()

  def GetResponseType(self):
    return self.response_type_selected.get_attribute("value")

  def SetUrgency(self, urgency):
    urgency_xpath = self.URGENCY_XPATHS.get(urgency.lower())
    self.webdriver.find_element_by_xpath(urgency_xpath).click()

  def GetUrgency(self):
    return self.urgency_selected.get_attribute("value")

  def SetSeverity(self, severity):
    severity_xpath = self.SEVERITY_XPATHS.get(severity.lower())
    self.webdriver.find_element_by_xpath(severity_xpath).click()

  def GetSeverity(self):
    return self.severity_selected.get_attribute("value")

  def SetCertainty(self, certainty):
    certainty_xpath = self.CERTAINTY_XPATHS.get(certainty.lower())
    if certainty_xpath:
      self.webdriver.find_element_by_xpath(certainty_xpath).click()

  def GetCertainty(self):
    return self.certainty_selected.get_attribute("value")

  def GetUuid(self):
    return self.uuid_element.text

  def SetAlertSenderName(self, sender_name):
    self.sender_element.send_keys(sender_name)

  def SetHeadline(self, head_line):
    self.headline_element.send_keys(head_line)

  def SetDescription(self, description):
    self.description_element.send_keys(description)

  def SetInstruction(self, instruction):
    self.instruction_element.send_keys(instruction)

  def SetContact(self, contact):
    self.contact_element.send_keys(contact)

  def SetArea(self, area):
    self.area_element.send_keys(area)

  def SetUsername(self, username):
    self.username_element.send_keys(username)

  def SetPassword(self, password):
    self.password_element.send_keys(password)


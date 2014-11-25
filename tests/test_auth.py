"""CAP Collector auth tests."""

__author__ = "shakusa@google.com (Steve Hakusa)"

from django import test
from django.forms import ValidationError

from CAPCollector import auth


class AuthTests(test.TestCase):
  """Auth unit tests."""

  def test_validate_strong_password(self):
    """Tests if password validation works correctly."""
    def assert_error(password):
      try:
        auth.validate_strong_password(password)
        self.fail("Expected a ValidationError")
      except ValidationError:
        pass  # expected

    assert_error(None)
    assert_error("")
    assert_error("foo")
    assert_error("123456789")
    assert_error("1234abcd")
    assert_error("1234ABCD")

    auth.validate_strong_password("1234ABcd")

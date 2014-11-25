"""Stronger password auth for CAP Collector."""

__author__ = "shakusa@google.com (Steve Hakusa)"

import re

from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.forms import SetPasswordForm
from django.forms import ValidationError
from django.utils.translation import ugettext as _


def validate_strong_password(password):
  """Validates that the given password is sufficiently strong.

  Args:
    password: A string, the candidate password.
  Returns:
    The input password if it is strong enough
  Raises:
    ValidationError if the password is weak.
  """
  password = password or ""
  error_message = None
  if len(password) < 8:
    error_message = _("Password is too short.")
  elif re.match(r"^[0-9]*$", password):
    error_message = _("Password contains only numbers.")
  elif re.match(r"^[a-z0-9]*$", password):
    error_message = _("Password contains no uppercase letters.")
  elif re.match(r"^[A-Z0-9]*$", password):
    error_message = _("Password contains no lowercase letters.")

  if error_message:
    instructions = _("Password must be at least 8 characters long and contain "
                     "a mixture of lowercase and uppercase letters, numbers, "
                     "punctuation, and special characters (such as ^ or %). "
                     "Avoid using words more than 4 characters long.")
    raise ValidationError("\n".join([error_message, instructions]))
  return password


class ValidatingSetPasswordForm(SetPasswordForm):

  def clean_new_password1(self):
    password = self.cleaned_data["new_password1"]
    return validate_strong_password(password)


class ValidatingPasswordChangeForm(PasswordChangeForm):

  def clean_new_password1(self):
    password = self.cleaned_data["new_password1"]
    return validate_strong_password(password)

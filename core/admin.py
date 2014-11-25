"""CAP Collector models admin."""

__author__ = "arcadiy@google.com (Arkadii Yakovets)"

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import AdminPasswordChangeForm
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from CAPCollector import auth
from core import models


class ValidatingUserCreationForm(UserCreationForm):

  def clean_password1(self):
    password = self.cleaned_data["password1"]
    return auth.validate_strong_password(password)


class ValidatingAdminPasswordChangeForm(AdminPasswordChangeForm):

  def clean_password1(self):
    password = self.cleaned_data["password1"]
    return auth.validate_strong_password(password)


class ValidatingUserAdmin(UserAdmin):

  add_form = ValidatingUserCreationForm
  change_password_form = ValidatingAdminPasswordChangeForm


admin.site.unregister(User)
admin.site.register(User, ValidatingUserAdmin)
admin.site.register(models.Alert)
admin.site.register(models.AreaTemplate)
admin.site.register(models.MessageTemplate)

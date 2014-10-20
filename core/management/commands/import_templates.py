"""Area/message template importer for CAPCollector project.

Imports area/messages template files to corresponding SQL tables.
File names must end with .xml.
An area template is a single CAP <area> block.
A message template is a single CAP <alert> block with a single <info> block;
<area> blocks are ignored.

Run
$ python manage.py import_templates area /home/user/path/to/templates/
to import area templates or
$ python manage.py import_templates message /home/user/path/to/templates/
to import message templates.

For more information on this file, see
https://docs.djangoproject.com/en/dev/howto/custom-management-commands/
"""

__author__ = "arcadiy@google.com (Arkadii Yakovets)"


import os
import uuid

from core import models
from core import utils
from django.core.management.base import BaseCommand
from django.core.management.base import CommandError


class Command(BaseCommand):
  """Template importer command implementation."""

  args = "<templates_type templates_path>"
  help = "Imports existing area or message template files to SQL tables."

  def handle(self, *args, **options):
    if len(args) != 2:
      raise CommandError(
          "Wrong arguments number! Please use python manage.py import_templates"
          " template_type template_path (e.g. python manage.py import_templates"
          " area /home/user/path/to/templates/ or python manage.py"
          " import_templates message /home/user/path/to/templates/")

    templates_type = args[0]
    templates_path = args[1]

    template_objects = []
    for file_name in os.listdir(templates_path):
      if not file_name.endswith(".xml"):
        print "Ignored file: %s" % file_name
        continue

      file_path = os.path.join(templates_path, file_name)
      with open(file_path, "r") as template_file:
        template_content = template_file.read()
      template_dict = utils.ParseAlert(template_content, "xml", uuid.uuid4())
      if templates_type == "area":
        template_model = models.AreaTemplate
      elif templates_type == "message":
        template_model = models.MessageTemplate

      template_obj = template_model()
      template_obj.title = file_name.rstrip(".xml").strip()
      template_obj.content = template_content
      template_objects.append(template_obj)

    # Save to DB.
    template_model.objects.bulk_create(template_objects)

"""Geocode preview polygon importer for CAPCollector project.

Imports GeocodePreviewPolygons to the corresponding SQL table.
Expected input is a either a GeoJSON file

{
  "type": "FeatureCollection",
  "features": [
    {
      "type": "Feature",
      "properties": {
        "STATE": "Maharashtra",
        "name": "Bhandara",
        "namestate": "Bhandara__Maharashtra"
      },
      "geometry": {
        "type": "Polygon",
          "coordinates": [
            [[lng_1, lat_1], ..., [lng_n-1, lat_n-1], [lng_1, lat_1]]
          ]
      }
    }
    ...
  ]
}

or a KML file with a "geocode_key" in ExtendedData:

<Document><Folder><name>districts</name>
  <Placemark>
    <name>DISTRICT_NAME</name>
    <ExtendedData><SchemaData schemaUrl="#districts">
    <SimpleData name="State">STATE_NAME</SimpleData>
    <SimpleData name="geocode_key">DISTRICT_NAME__STATE_NAME</SimpleData>
    </SchemaData></ExtendedData>
    <Polygon><outerBoundaryIs><LinearRing><coordinates>
      lng_1,lat_1 lng_2,lat_2 ... lng_n-1,lat_n-1, lng_1, lat_1
    </coordinates></LinearRing></outerBoundaryIs></Polygon>
  </Placemark>
  ...
</Document>

Multipolygon is supported, innerBoundaryIs (holes) are not.

Run like
$ python manage.py import_geocodepreviewpolygon /home/user/path/to/file.[json|kml]

For more information on this file, see
https://docs.djangoproject.com/en/dev/howto/custom-management-commands/
"""

__author__ = "shakusa@google.com (Steve Hakusa)"

import json

from core import models
from django.core.management.base import BaseCommand
from django.core.management.base import CommandError
import lxml
from lxml import etree


GEOCODE_VALUE_NAME = "IN_IMD_DISTRICTS"
BATCH_SIZE = 100


class KmlFile(object):
  """Handles extracting preview polygons from KML."""
  KML_NS = "http://www.opengis.net/kml/2.2"

  def __init__(self, filename):
    self.filename = filename
    with open(filename, "r") as input_file:
      self.xml_tree = lxml.etree.fromstring(input_file.read())

  def xpath(self, element_tag):
    return ".//{%s}%s" % (KmlFile.KML_NS, element_tag)

  def get_features(self):
    return self.xml_tree.findall(self.xpath("Placemark"))

  def get_geocode_key(self, placemark):
    simple_data = placemark.find(self.xpath("SimpleData[@name='geocode_key']"))
    return simple_data.text

  def get_polygons(self, placemark):
    return placemark.findall(self.xpath("outerBoundaryIs"))

  def get_ring(self, boundary):
    return boundary.find(self.xpath("coordinates"))

  def get_points(self, coordinates):
    return [point.split(",") for point in coordinates.text.split(" ")]


class GeoJsonFile(object):
  """Handles extracting preview polygons from GeoJson."""

  def __init__(self, filename):
    self.filename = filename
    with open(filename, "r") as input_file:
      self.data = json.loads(input_file.read())

  def get_features(self):
    return self.data["features"]

  def get_geocode_key(self, feature):
    return feature["properties"]["namestate"]

  def get_polygons(self, feature):
    if feature["geometry"]["type"] == "Polygon":
      return [feature["geometry"]["coordinates"]]
    return feature["geometry"]["coordinates"]

  def get_ring(self, polygon):
    return polygon[0]

  def get_points(self, coordinates):
    return coordinates


class Command(BaseCommand):
  """geocodepreviewpolygon importer command implementation."""

  args = "<preview_polygons_kml>"
  help = "Imports GeocodePreviewPolygons to the corresponding SQL table."

  def handle(self, *args, **options):
    if len(args) != 1:
      raise CommandError(
          "Wrong arguments number! Please use python manage.py "
          "import_geocodepreviewpolygon /home/user/path/to/file.[json|kml]")

    fn = args[0]
    data = fn.endswith("kml") and KmlFile(fn) or GeoJsonFile(fn)

    done = 0
    preview_polygon_objs = []
    for feature in data.get_features():
      geocode_key = data.get_geocode_key(feature).replace(" ", "_")
      polygons = []
      for polygon in data.get_polygons(feature):
        ring = data.get_ring(polygon)
        lng_lat_points = data.get_points(ring)
        lat_lng_points = ["%s,%s" % (lat, lng) for lng, lat in lng_lat_points]
        polygons.append("<polygon>%s</polygon>" % " ".join(lat_lng_points))

      obj = models.GeocodePreviewPolygon()
      obj.id = models.GeocodePreviewPolygon.make_key(GEOCODE_VALUE_NAME,
                                                     geocode_key)
      obj.content = "\n".join(polygons)
      preview_polygon_objs.append(obj)
      print obj.id
      done += 1
      if done % BATCH_SIZE == 0:
        print "Finished %d" % done
        models.GeocodePreviewPolygon.objects.bulk_create(preview_polygon_objs)
        preview_polygon_objs = []

    models.GeocodePreviewPolygon.objects.bulk_create(preview_polygon_objs)
    print "All done, saved %d" % done

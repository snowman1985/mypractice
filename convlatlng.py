import os,sys
sys.path.insert(0, os.path.join("/root","workspace","ywbserver"))
from django.core.management import *
from ywbserver import settings
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ywbserver.settings")
from shop.models import *
from utils.baidumap import *
from django.contrib.gis.geos import fromstr
import psycopg2

count = 0
for shop in Shop.objects.all():
  print("count:", count)
  count += 1
  lat = shop.latitude
  lng = shop.longitude
  point = fromstr("POINT(%s %s)" % (lng, lat))
  shop.point = point
  shop.save()
  

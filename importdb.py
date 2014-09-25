import os,sys
sys.path.insert(0, os.path.join("/root","workspace","ywbserver"))
from django.core.management import *
from ywbserver import settings
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ywbserver.settings")
from shop.models import *
from utils.baidumap import *
from django.contrib.gis.geos import fromstr
import psycopg2

dbaddr = settings.DATABASES['default']['HOST']
dbport = settings.DATABASES['default']['PORT']
dbname = 'wjbb_data'
dbuser = settings.DATABASES['default']['USER']
dbpassword = settings.DATABASES['default']['PASSWORD']

conn = psycopg2.connect(host=dbaddr, port=dbport, database=dbname, user=dbuser, password=dbpassword)
cur = conn.cursor()

cur.execute("""SELECT * from shangjias""")

rowcount = 0
for row in cur:
  rowcount += 1
  if rowcount < 487:
    continue
  print(rowcount)
  try:
    name = row[2]
    address = row[3]
    abstract = ""
    description = ""
    url = row[1]
    addrjson = get_baidu_location(address)
    print(addrjson)
    lat = addrjson['result']['location']['lat']
    lng = addrjson['result']['location']['lng']
    city = get_baidu_address(lat, lng, False)
    print("city:",city)
    point = fromstr("POINT(%s %s)" % (lng, lat))
    shop = Shop(name=name,city=city,address=address,abstract=abstract,description=description,url=url,longitude=lng, latitude=lat,point=point)
    shop.save()
  except:
    pass
  #if rowcount == 1:
  #  break
print("rowcount:", rowcount)




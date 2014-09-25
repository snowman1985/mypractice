from bayesian import classify, classify_file
from cutword import cutword
import sqlite3
from collections import defaultdict

conn = sqlite3.connect("w.sqlite3")
c=conn.cursor()

marktitle = open("marktitle.txt", "w")
def toy(n):
  if n[-1] == 'y' or n[-1] == 'm':
    return n
  else:
    print "len:", len(n)
    print "n:",n
    if len(n) == 3:
      print n[0], n[1], n[2]
    print n[-1]
  return str(int(float(n) / 365)) + "y"

count = 1
agerangeset = set()
ageclass = defaultdict(list)

#for i in c.execute("select * from knowledge_detail where mark <> \"\""):
for i in c.execute("select * from knowledge_detail where mark=\"shengeng\" or mark=\"xueyu\" or mark=\"hujun\" or mark=\"xuezhenghua\""):
#  print(count,":",i[1], "\n")
  print i[1], i[6], i[7]
  marktitle.write(i[1].encode("utf-8"))
  marktitle.write(" ")
  minstr = toy(i[6]).encode("utf-8")
  marktitle.write(minstr)
  marktitle.write(" ")
  maxstr = toy(i[7]).encode("utf-8")
  marktitle.write(maxstr)
  marktitle.write(" ")
  marktitle.write(i[10].encode("utf-8"))
  marktitle.write("\n")
  if minstr.find('m') >= 0 or maxstr.find('m') >= 0 :
    minstr = "0y"
    maxstr = "1y"
  rangestr = minstr + "*" + maxstr
  agerangeset.add(rangestr)
  ageclass[rangestr].append(i[1])
  count += 1
 
print("age range size:", len(agerangeset)) 
for i in list(agerangeset):
  print(i)
print("age class size:")
for k, v in ageclass.items():
  print(k, ":", len(v))

print("begin classify")
rescol = []
count1 = 1
for i in c.execute("select * from knowledge_detail where mark = \"program\" limit 3000"):
#for i in c.execute("select * from knowledge_detail where serial = 1909"):
  print(count1)
  count1 += 1
  print(i[0]) 
  print(i[1])
  curclass = classify(i[1], ageclass, extractor=cutword)
  print curclass
  (curmin, curmax) = curclass.split('*')
  print("curmin:", curmin)
  print("curmax:", curmax)
  rescol.append([i[0], curmin, curmax])
  #c.execute("update knowledge_detail set min=?, max=? where serial=?", (curmin, curmax, i[0]))

for r in rescol:
  c.execute("update knowledge_detail set min=?, max=?, mark=\"programa\" where serial=?", (r[1], r[2], r[0]))

#for i in idcol:
#  print("update mark")
#  c.execute("update knowledge_detail set mark=\"program\" where serial=?", (i))
conn.commit()  
conn.close()

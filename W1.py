# -*- coding: utf-8 -*-
#!/usr/bin/env python

import jpype
classpath = ".:ikjar/IKAnalyzer2012_u6.jar"
jpype.startJVM(jpype.getDefaultJVMPath(), "-Djava.class.path=%s" % classpath)

w=jpype.JClass("W1")
a=w(u"你好啊嘿嘿好")

b=a.CutWord()
print type(b)
print b.size()

for i in b:
  print i

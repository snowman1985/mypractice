# -*- coding: utf-8 -*-
import jpype
import os

classpath = ".:./IKAnalyzer2012_u6.jar"
jpype.startJVM(jpype.getDefaultJVMPath(), "-ea", "-Djava.class.path=%s" % classpath)
def cutword(content):
  
  print(os.getcwd())
  checkclass = jpype.JClass("Segmenter")

  #contentcol = Commercial.objects.all()
  print("content:", content)
  checkobj = checkclass(content)
  #for item in checkobj.CutWord():
  l= checkobj.CutWord()
  #jpype.shutdownJVM()
  return l

if __name__ == "__main__":
  content = u"是薛宇啊吃饭吗"
  a=cutword(content)
  for i in a:
    print i


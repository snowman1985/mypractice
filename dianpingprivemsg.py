# -*- coding: utf-8 -*-
from PAM30 import PAMIE
import time
from datetime import datetime

now = datetime.now()
contentstr = "今天的测试" + str(now)

ie = PAMIE()
time.sleep(3)
ie.navigate("http://www.dianping.com/login")
time.sleep(3)
ie.setTextBox("username", "snowman1985")
ie.setTextBox("password", "")
validatecode = raw_input("please enter validate code:")
ie.setTextBox("validate", validatecode)
validelem = ie.findElement("input", "name", "login")
ie.clickElement(validelem)
time.sleep(1)
raw_input("wait for login enabled")
ie.clickButton("login")
time.sleep(2)
print "#### after login"
ie.navigate("http://www.dianping.com/msg/send")
time.sleep(3)
ie.setTextBox("targetName", "山水之间的雪人")
ie.setTextArea("content", contentstr)
sendbut = ie.findElement("input", "type", "submit")
ie.clickElement(sendbut)


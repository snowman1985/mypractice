# -*- coding: utf-8 -*-
from bayesian import classify, classify_file
from cutword import cutword

spams = [u"什么", u"哦 好的", u"是嘛 这样啊  你好啊"] # etc
genuines = [u"明天看电影", u"想吃饭了"]
message = u"看电影能吃饭吗"
# Classify as "genuine" because of the words "remember" and "tomorrow".
print classify(message, {'spam': spams, 'genuine': genuines}, extractor=cutword)

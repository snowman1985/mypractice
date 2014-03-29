#!/usr/bin/env python

import sys
import psycopg2
import time
from pymongo import MongoClient
from bson import Binary, Code
from bson.json_util import dumps, loads
from datetime import datetime
from bson.son import SON
from saverestodb import savetotopicdb
import time
import ConfigParser

if len(sys.argv) < 4:
  print "use: saverestofile.py config_file begin_time end_time"
  sys.exit(-1)

config_file = sys.argv[1]
print "load config from: %s" % config_file
config = ConfigParser.ConfigParser()
config.readfp(open(config_file, "rb"))

arglen = len(sys.argv)
print sys.argv
mongoaddr = config.get("mongo", "host")
mongoport = int(config.get("mongo", "port"))
topicdbuser = config.get("mongo", "topicdb_user")
topicdbpwd = config.get("mongo", "topicdb_pwd")
impdbuser = config.get("mongo", "imdb_user")
impdbpwd = config.get("mongo", "imdb_pwd")

dbaddr = config.get("stat", "host")
dbport = int(config.get("stat", "port"))
dbuser = config.get("stat", "user")
dbpassword = config.get("stat", "pwd")
dbname = config.get("stat", "db")
begin_datetime = datetime.strptime(sys.argv[2], "%Y-%m-%d-%H-%M-%S")
end_datetime = datetime.strptime(sys.argv[3], "%Y-%m-%d-%H-%M-%S")
result_path = config.get("globle", "result_path")

dayallfilename = result_path + "/day_all.txt"
day24filename = result_path + "/day_24.txt"
day241filename = result_path + "/day_241.txt"
impfilename = result_path + "/imp.txt"
commentfilename = result_path + "/comment.txt"



dayallfile = open(dayallfilename, 'w')
day24file = open(day24filename, 'w')
day241file = open(day241filename, 'w')
commentfile = open(commentfilename, 'w')
#likeallfile = open("like_all.txt", 'w')
#like24file = open("like_24.txt", 'w')
#like241file = open("like_241.txt", 'w')
impfile = open(impfilename, 'w')

#if arglen >=4:
#  mongoaddr = sys.argv[1]
#  mongoport = int(sys.argv[2])
#  dbaddr = sys.argv[3]
#  dbport = int(sys.argv[4])

client = MongoClient(mongoaddr, mongoport)
topicdb = client.topicdb
impdb = client.impdb

topicdb.authenticate(topicdbuser, topicdbpwd)
impdb.authenticate(impdbuser, impdbpwd)

collection_day_all = topicdb.account_day_all
collection_day_team24 = topicdb.account_day_24
collection_day_team241 = topicdb.account_day_241
collection_comment = topicdb.account_comment
#collection_like_all = topicdb.like_day_count_all
#collection_like_team24 = topicdb.like_day_count_24
#collection_like_team241 = topicdb.like_day_count_241
collection_imp = impdb.imp_day_count

topic_mapper_str='''
function() {
    var timeTopic = new Date(this.createtime);
    //var timeTopic = new Date(this.updatetime);
    //var dateTopic = new Date(Date.UTC(timeTopic.getYear(),
        //timeTopic.getMonth(), timeTopic.getDate(), timeTopic.getHours()));
    var hourTopic = new Date(timeTopic)
    hourTopic.setMinutes(0)
    hourTopic.setSeconds(0)
    hourTopic.setMilliseconds(0)
    var topicCount = 1;
    var androidCount = (this.devicetype.toLowerCase() == 'android') ? 1 : 0;
    var iphoneCount = (this.devicetype.toLowerCase() == 'iphone') ? 1 : 0;
    var webCount = (this.devicetype.toLowerCase() == 'web') ? 1 : 0;
    var textCount = (this.imageList.length === 0) ? 1 : 0;
    var imageCount = (this.imageList.length !== 0) ? 1 : 0;

    var commentCount = this.commentList.length;
    var likeCount = this.likeCount;

    emit(hourTopic, {
        'topicCount': topicCount,
        'androidCount': androidCount,
        'iphoneCount': iphoneCount,
        'webCount': webCount,
        'textCount': textCount,
        'imageCount': imageCount,
        'commentCount': commentCount,
        'commentDayCount': 0,
        'likea': likeCount,
    });

    /*for (var item in this.commentList) {
        var timeComment = new Date(this.commentList[item].createtime);
        var hourComment = new Date(timeComment);
        hourComment.setMinutes(0)
        hourComment.setSeconds(0)
        hourComment.setMilliseconds(0)
        emit(hourComment, {
            'topicCount': 0,
            'androidCount': 0,
            'iphoneCount': 0,
            'webCount': 0,
            'textCount': 0,
            'imageCount': 0,
            'commentCount': 0,
            'commentDayCount': 1,
            'likea':0,
        });
    }*/
};'''

comment_mapper_str = ''' function() {
    for (var item in this.commentList) {
        if (this.commentList[item].createtime < begintime || this.commentList[item].createtime >= endtime) continue;
	var timeComment = new Date(this.commentList[item].createtime);
	var hourComment = new Date(timeComment);
	hourComment.setMinutes(0)
	hourComment.setSeconds(0)
	hourComment.setMilliseconds(0)
	emit(hourComment, {
		'commentDayCount': 1,			
	    });
	}
};'''

comment_reducer_str = '''function(key, emits) {
    var commentDayCount = 0;
    for (var i in emits) {
        commentDayCount += emits[i].commentDayCount;
    }
    return {
        'commentDayCount': commentDayCount,
    }
};'''

topic_reducer_str = '''function(key, emits) {
    var topicCount = 0;
    var androidCount = 0;
    var iphoneCount = 0;
    var webCount = 0;
    var textCount = 0;
    var imageCount = 0;
    var commentCount = 0;
    var commentDayCount = 0;
    var likeCount = 0;
    for (var i in emits) {
        topicCount += emits[i].topicCount;
        androidCount += emits[i].androidCount;
        iphoneCount += emits[i].iphoneCount;
        webCount += emits[i].webCount;
        textCount += emits[i].textCount;
        imageCount += emits[i].imageCount;
        commentCount += emits[i].commentCount;
        commentDayCount += emits[i].commentDayCount;
        likeCount += emits[i].likea;
    }
    return {
        'topicCount': topicCount,
        'androidCount': androidCount,
        'iphoneCount': iphoneCount,
        'webCount': webCount,
        'textCount': textCount,
        'imageCount': imageCount,
        'commentCount': commentCount,
        'commentDayCount': commentDayCount,
        'likea': likeCount,
    };
};'''

imp_mapper_str = '''
function() {
  for (var i in this.msgList) {
    var curitem = this.msgList[i];
    var cttime = new Date(curitem.createTime);
    var hourImp = new Date(cttime)
    hourImp.setMinutes(0)
    hourImp.setSeconds(0)
    hourImp.setMilliseconds(0)
    var contentstr = (typeof curitem.content === 'string');
    var imageCount = (contentstr && curitem.content.indexOf('<x xmlns="jabber:x:image">') != -1) ? 1 : 0;
    var audioCount = (contentstr && curitem.content.indexOf('<x xmlns="jabber:x:audio">') != -1) ? 1 : 0;
    var textCount = (contentstr && (imageCount + audioCount === 0)) ? 1 : 0;
    var androidCount = 0;
    var iphoneCount = 0;
    var webCount = 0;
    var from = "";
    var androidFrom = {};
    var iphoneFrom = {};
    var webFrom = {};
    var fromd = {};
    if (contentstr) {
      var reg=/from=\"(.*?)\"/;
      var match = reg.exec(curitem.content);
      if (match !== null) {
        from = match[1];
        androidCount = (from.indexOf("APH") != -1) ? 1 : 0;
        iphoneCount = (from.indexOf("IPN") != -1) ? 1 : 0;
        webCount = (androidCount + iphoneCount === 0) ? 1 : 0;
        if (from.indexOf("APH") != -1) {
          androidFrom[from]=1;
        } else if (from.indexOf("IPN") != -1) {
          iphoneFrom[from]=1;
        } else {
          webFrom[from]=1;
        }
        fromd[from] = 1;
      }
    };
    emit(hourImp, {
      'textCount': textCount,
      'imageCount': imageCount,
      'audioCount': audioCount,
      'androidCount': androidCount,
      'iphoneCount': iphoneCount,
      'webCount': webCount,
      'androidFrom': androidFrom,
      'iphoneFrom': iphoneFrom,
      'webFrom': webFrom,
      'from': fromd,
    });
  };
};
'''

imp_reducer_str = '''function(key, emits) {
    var textCount = 0;
    var imageCount = 0;
    var audioCount = 0;
    var androidCount = 0;
    var iphoneCount = 0;
    var webCount = 0;
    var androidFrom = {};
    var iphoneFrom = {};
    var webFrom = {};
    var from = {};
    for (var i in emits) {
      textCount += emits[i].textCount;
      imageCount += emits[i].imageCount;
      audioCount += emits[i].audioCount;
      androidCount += emits[i].androidCount;
      iphoneCount += emits[i].iphoneCount;
      webCount += emits[i].webCount;

      Object.keys(emits[i].androidFrom).forEach(function(x) { androidFrom[x] = 1 });
      Object.keys(emits[i].iphoneFrom).forEach(function(x) { iphoneFrom[x] = 1 });
      Object.keys(emits[i].webFrom).forEach(function(x) { webFrom[x] = 1});
      Object.keys(emits[i].from).forEach(function(x) { from[x] = 1});
    }

    return {
      'textCount': textCount,
      'imageCount': imageCount,
      'audioCount': audioCount,
      'androidCount': androidCount,
      'iphoneCount': iphoneCount,
      'webCount': webCount,
      'androidFrom': androidFrom,
      'iphoneFrom': iphoneFrom,
      'webFrom': webFrom,   
      'from': from, 
    };
};
'''
imp_finalizer_str = '''
function(key, reducedValue) {
  var androidFromNum = Object.keys(reducedValue.androidFrom).length;
  var iphoneFromNum = Object.keys(reducedValue.iphoneFrom).length;
  var webFromNum = Object.keys(reducedValue.webFrom).length;
  var fromNum = Object.keys(reducedValue.from).length;
  reducedValue.androidFrom = androidFromNum;
  reducedValue.iphoneFrom = iphoneFromNum;
  reducedValue.webFrom = webFromNum;
  reducedValue.from = fromNum;
  return reducedValue;
}
'''

begin_time = (int)(time.mktime(begin_datetime.timetuple())) * 1000
end_time = (int)(time.mktime(end_datetime.timetuple())) * 1000
print "begin_time:", begin_time
print "end_time:", end_time


topic_mapper = Code(topic_mapper_str)
topic_reducer = Code(topic_reducer_str)
comment_mapper = Code(comment_mapper_str, {"begintime":begin_time, "endtime":end_time})
comment_reducer = Code(comment_reducer_str)
imp_mapper = Code(imp_mapper_str)
imp_reducer = Code(imp_reducer_str)
imp_finalizer = Code(imp_finalizer_str)
#begin_time = (int)(time.mktime(datetime(2014,03,01,0,0,0).timetuple())) * 1000
#begin_time = (int)(time.mktime(datetime(2014,03,01,0,0,0).timetuple())) * 1000
#r1=topicdb.topic.map_reduce(topic_mapper, topic_reducer, 'account_day_all', query={'updatetime':{'$gte':begin_time,'$lte':end_time}} )
r1=topicdb.topic.map_reduce(topic_mapper, topic_reducer, out=SON([("replace", "account_day_all")] ) , query={'createtime':{'$gte':begin_time,'$lte':end_time}})
r2=topicdb.topic.map_reduce(topic_mapper, topic_reducer, out=SON([("replace", "account_day_24")] ) , query={'createtime':{'$gte':begin_time,'$lte':end_time}, 'teamid':24})
r3=topicdb.topic.map_reduce(topic_mapper, topic_reducer, out=SON([("replace", "account_day_241")] ) , query={'createtime':{'$gte':begin_time,'$lte':end_time}, 'teamid':241})
r4=impdb.historyOneToOne.map_reduce(imp_mapper, imp_reducer,  out=SON([("replace", "imp_day_count")]), query={'msgList.updateTime':{'$gte':begin_time,'$lte':end_time}}, finalize=imp_finalizer)
r5=topicdb.topic.map_reduce(comment_mapper, comment_reducer, out=SON([("replace", "account_comment")]), query={'commentList.createtime':{'$gte':begin_time,'$lte':end_time}})
#r4=impdb.historyOneToOne.map_reduce(imp_mapper, imp_reducer,  out=SON([("replace", "imp_day_count")]))


#print r1

def writerestofile(coll, f):
  for i in coll.find():
    f.write(dumps(i))
    f.write("\n")

writerestofile(collection_day_all, dayallfile)
writerestofile(collection_day_team24, day24file)
writerestofile(collection_day_team241, day241file)
#writerestofile(collection_like_all, likeallfile)
#writerestofile(collection_like_team24, like24file)
#writerestofile(collection_like_team241, like241file)
writerestofile(collection_imp, impfile)
writerestofile(collection_comment, commentfile)

dayallfile.close()
day24file.close()
day241file.close()
#likeallfile.close()
#like24file.close()
#like241file.close()
impfile.close()
commentfile.close()

conn = psycopg2.connect(host=dbaddr, port=dbport, database=dbname, user=dbuser, password=dbpassword)
cur = conn.cursor()

savetotopicdb(dayallfilename, "posts_statistics", cur)
savetotopicdb(commentfilename, "circle_comment_statistics", cur)
savetotopicdb(dayallfilename, "post_praise_statistics", cur)
savetotopicdb(day24filename, "angel_user_circle_statistics", cur)
savetotopicdb(impfilename, "im_message_statistics", cur)
savetotopicdb(day241filename, "feedback_circle_statistics", cur)
savetotopicdb(impfilename, "user_login_times_statistics", cur)

conn.commit()
cur.close()
conn.close()

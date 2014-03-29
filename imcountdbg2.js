var mapFunc = function() {
  for (var i in this.msgList) {
    var curitem = this.msgList[i];
    var cttime = new Date(curitem.createTime);
    //var datekey = new Date(Date.UTC(cttime.getYear(), cttime.getMonth(),cttime.getDate(),cttime.getHours()));
    var datekey = new Date(cttime)
    datekey.setHours(0)
    datekey.setMinutes(0)
    datekey.setSeconds(0)
    datekey.setMilliseconds(0)
    var contentstr = (typeof curitem.content === 'string');
    var imageCount = (contentstr && curitem.content.indexOf("<x xmlns=\"jabber:x:image\">") != -1) ? 1 : 0;
    var audioCount = (contentstr && curitem.content.indexOf("<x xmlns=\"jabber:x:audio\">") != -1) ? 1 : 0;
    var textCount = (contentstr && (imageCount + audioCount === 0)) ? 1 : 0;
    var androidCount = 0;
    var iphoneCount = 0;
    var webCount = 0;
    var androidFrom = {};
    var iphoneFrom = {};
    var webFrom = {};
    var from = "";
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
    printjson("begin map")
    printjson(from);
    printjson(androidFrom);
    printjson(iphoneFrom);
    printjson(webFrom);
    printjson("over map");
    emit(datekey, {
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

var reduceFunc = function(key, emits) {
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
    printjson("key");
    printjson(key);
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

      print("begin one reduce item");
      printjson(emits[i].from);
      printjson(emits[i].androidFrom);
      printjson(emits[i].iphoneFrom);
      printjson(emits[i].webFrom);
      print("over one item");
    }

    return {
      'textCount': textCount,
      'imageCount': imageCount,
      'audioCount': audioCount,
      'androidCount': androidCount,
      'iphoneCount': iphoneCount,
      'webCount': webCount,
      //'androidFrom': Object.keys(androidFrom).length,
      'androidFrom': androidFrom,
      'iphoneFrom': iphoneFrom,
      'webFrom': webFrom,
      'from': from,
    }; 
};

/*var finalFunc = function(key, reducedValue) {
  var androidFromNum = Object.keys(reducedValue['androidFrom']).length;
  var iphoneFromNum = Object.keys(reducedValue['iphoneFrom']).length;
  var webFromNum = Object.keys(reducedValue['webFrom']).length;
  reducedValue['androidFrom'] = androidFromNum;
  reducedValue['iphoneFrom'] = iphoneFromNum;
  reducedValue['webFrom'] = webFromNum;
  return reducedValue;
}*/

var finalFunc = function(key, reducedValue) {
  var androidFromNum = Object.keys(reducedValue.androidFrom).length;
  var iphoneFromNum = Object.keys(reducedValue.iphoneFrom).length;
  var webFromNum = Object.keys(reducedValue.webFrom).length;
  var fromNum = Object.keys(reducedValue.from).length;
  reducedValue.androidFrom = androidFromNum;
  reducedValue.iphoneFrom = iphoneFromNum;
  reducedValue.webFrom = webFromNum;
  reducedValue.from = fromNum;
  printjson("final func begin");
  printjson(reducedValue);
  printjson("final func end");
  return reducedValue;
}


//db.runCommand({
/*db.runCommand({
    'mapreduce': 'historyOneToOne',
    'map': mapFunc,
    'reduce': reduceFunc,
    'out': {replace: "imp_day_count"}
});
*/
//db.historyOneToOne.mapReduce(mapFunc, reduceFunc, {out: {replace: "imp_day_count_try"}, query:{'msgList.updateTime':{$gte:1393603200000, $lt: 1393689600000}}});
db.historyOneToOne.mapReduce(mapFunc, reduceFunc, {out: {replace: "imp_day_count_try"}, finalize:finalFunc});
//db.historyOneToOne.mapReduce(mapFunc, reduceFunc, {out: {replace: "imp_day_count_try"}});
//res=db.historyOneToOne.mapReduce(mapFunc, reduceFunc, {out: {inline:1}});
//printjson(res);


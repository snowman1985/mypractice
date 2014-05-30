echo begin:`date +"%Y-%m-%d %H:%M:%S"` >> /opt/LogAnalysis/timelog.txt
today=`date +%Y-%m-%d`
nginxpath=/user/flume/kuaijijiayuan/nginx/$today
cd /opt/LogAnalysis/
sbt "run $nginxpath" 
echo end:`date +"%Y-%m-%d %H:%M:%S"` >> /opt/LogAnalysis/timelog.txt

package cn.com.chanjet.spark

import org.apache.spark.SparkContext._
import org.apache.spark.SparkContext
import org.apache.spark.SparkConf
import org.apache.log4j.PropertyConfigurator
import java.text.SimpleDateFormat
import java.util.Locale
import scala.slick.driver.PostgresDriver.simple._
import java.sql.{Timestamp, Time, Date}
import java.text.SimpleDateFormat
import java.util.Locale
import com.typesafe.config.ConfigFactory
import org.apache.hadoop.conf.Configuration
import org.apache.hadoop.fs.FileStatus
import org.apache.hadoop.fs.FileSystem
import org.apache.hadoop.fs.Path
import java.net.URI

object LogAnalysis {
 //获取日志中的日期
  def getLogDate(line:String):Timestamp={
     val result=line.split(" ")
     val originalDateString=result(3).substring(1,result(3).length()-5)+"00:00"
     val fmt =new SimpleDateFormat("dd/MMM/yyyy:HH:mm:ss",Locale.US);
     val date=fmt.parse(originalDateString)
     new Timestamp(date.getTime())
  }

//日期转换
def translateDate(line:String):(String,Int)={
     val result=line.split(" ")
     val originalDateString=result(3).substring(1,result(3).length()-5)+"00:00"
     val fmt =new SimpleDateFormat("dd/MMM/yyyy:HH:mm:ss",Locale.US);
     val date=fmt.parse(originalDateString)
     val sdm=new SimpleDateFormat("yyyy-MM-dd HH:mm:ss")
     (sdm.format(date),1)
  }

def uvmapfunc(line:String):(String, String)={
    val result=line.split(" ")
    val originalDateString=result(3).substring(1,result(3).length()-5)+"00:00"
    val fmt =new SimpleDateFormat("dd/MMM/yyyy:HH:mm:ss",Locale.US);
    val date=fmt.parse(originalDateString)
    val sdm=new SimpleDateFormat("yyyy-MM-dd HH:mm:ss")
    (sdm.format(date), result(0))
  }

case class PVElement(id:Int, time:Timestamp, pvcount:Int)
class PVTable(tag:Tag) extends Table[PVElement](tag, "pv") {
  def id = column[Int]("id", O.PrimaryKey, O.AutoInc)
  def time = column[Timestamp]("statistics_date")
  def pvcount = column[Int]("pvcount")

  def * = (id, time, pvcount) <> (PVElement.tupled,PVElement.unapply)
}

def InsertPVToDB(result:Int, db:slick.driver.PostgresDriver.backend.DatabaseDef, time:Timestamp):Unit = {
    val insertSql = TableQuery[PVTable]
    db withSession { implicit session:Session=>
      insertSql forceInsertAll(PVElement(-1, time, result))
    }
  }

//uv的统计
case class UVElement(id:Int, time:Timestamp, uvcount:Int)
class UVTable(tag:Tag) extends Table[UVElement](tag, "uv") {
  def id = column[Int]("id", O.PrimaryKey, O.AutoInc)
  def time = column[Timestamp]("statistics_date")
  def uvcount = column[Int]("uvcount")

  def * = (id, time, uvcount) <> (UVElement.tupled, UVElement.unapply)
}
def InsertUVToDB(result: Int, db:slick.driver.PostgresDriver.backend.DatabaseDef, time:Timestamp):Unit = {
    val insertSql = TableQuery[UVTable]
    db withSession { implicit session:Session=>
      insertSql forceInsertAll(UVElement(-1, time, result))
    }
  }

//urlcount top20的统计
case class UrlCountElement(id:Int, time:Timestamp, url:String, urlcount:Int)
class UrlCountTable(tag:Tag) extends Table[UrlCountElement](tag, "urlcount") {
  def id = column[Int]("id", O.PrimaryKey, O.AutoInc)
  def time = column[Timestamp]("statistics_date")
  def url = column[String]("url")
  def urlcount = column[Int]("count")

  def * = (id, time, url, urlcount) <> (UrlCountElement.tupled, UrlCountElement.unapply)
}

  def InsertUrlCountToDB(result: (String,Int), db:slick.driver.PostgresDriver.backend.DatabaseDef, time:Timestamp):Unit = {
    val insertSql = TableQuery[UrlCountTable]
    db withSession { implicit session:Session=>
      insertSql forceInsertAll(UrlCountElement(-1, time, result._1, result._2))
    }
  }

//二级域名pv, uv
case class SdPVElement(id:Int, time:Timestamp, domain:String, pvcount:Int)
class SdPVTable(tag:Tag) extends Table[SdPVElement](tag, "sdpv") {
  def id = column[Int]("id", O.PrimaryKey, O.AutoInc)
  def time = column[Timestamp]("statistics_date")
  def domain = column[String]("domain")
  def pvcount = column[Int]("pvcount")

  def * = (id, time, domain, pvcount) <> (SdPVElement.tupled,SdPVElement.unapply)
}

def InsertSdPVToDB(result:(String, Int), db:slick.driver.PostgresDriver.backend.DatabaseDef, time:Timestamp):Unit = {
    val insertSql = TableQuery[SdPVTable]
    db withSession { implicit session:Session=>
      insertSql forceInsertAll(SdPVElement(-1, time, result._1, result._2))
    }
  }

case class SdUVElement(id:Int, time:Timestamp, domain:String, uvcount:Int)
class SdUVTable(tag:Tag) extends Table[SdUVElement](tag, "sduv") {
  def id = column[Int]("id", O.PrimaryKey, O.AutoInc)
  def time = column[Timestamp]("statistics_date")
  def domain = column[String]("domain")
  def uvcount = column[Int]("uvcount")

  def * = (id, time, domain, uvcount) <> (SdUVElement.tupled, SdUVElement.unapply)
}
def InsertSdUVToDB(result:(String,Int), db:slick.driver.PostgresDriver.backend.DatabaseDef,  time:Timestamp):Unit = {
    val insertSql = TableQuery[SdUVTable]
    db withSession { implicit session:Session=>
      insertSql forceInsertAll(SdUVElement(-1, time, result._1, result._2))
    }
  }



def UnionRDDFromHdfs(sc:SparkContext,conf:Configuration,filepath:String)={
    val fs=FileSystem.get(URI.create("hdfs://10.17.4.203:9000"),conf)
    val path=new Path(filepath)
    val filelist=fs.listStatus(path).map(_.getPath.toString)
    filelist.filter(!_.contains("tmp")).map(filename=>sc.textFile(filename)).reduce(_.union(_))
}

  def main(args: Array[String]): Unit = {
     PropertyConfigurator.configure("log4j.properties")
     System.setProperty("spark.executor.memory","1024m")
     System.setProperty("worker_max_heapsize","256m")
     //加载配置文件
     val conf = ConfigFactory.load("sparkstat.conf")
     val ipaddr = conf.getString("statistic.pgdb.ipaddr")
     val port = conf.getInt("statistic.pgdb.port")
     val username = conf.getString("statistic.pgdb.username")
     val password = conf.getString("statistic.pgdb.password")
     val dbname = conf.getString("statistic.pgdb.dbname")
     val dburl = "jdbc:postgresql://" + ipaddr + ":" + port + "/" + dbname + "?user=" + username + "&password=" + password
     val db = Database.forURL(url = dburl, driver = "org.postgresql.Driver")
    // val db = Database.forURL(url = "jdbc:postgresql://172.18.4.244:5433/loganalysisdb?user=postgres&password=pgpassword", driver = "org.postgresql.Driver")
     val sparkurl=conf.getString("statistic.sparkapp.sparkurl")
     val jarpath=conf.getString("statistic.sparkapp.jarpath")
     val sc=new SparkContext(sparkurl,"LogAnalysis",System.getenv("SPARK_HOME"),List(jarpath))

     //val dataSet=sc.textFile("hdfs://172.18.8.239:9000/user/test/logAnalysis/access.log")
     val dataSet=sc.textFile(args(0))
     val hadoopConf = new Configuration()
     //val dataSet=UnionRDDFromHdfs(sc,hadoopConf,args(0))
 
     val logDate=getLogDate(dataSet.first())
     //统计pv
     val pvgroupByTime=dataSet.map(translateDate).groupByKey()
     val pvresult=pvgroupByTime.map(r=>(r._1,r._2.length)).sortByKey(true).collect()
     for(result <- pvresult){
        try{
           InsertPVToDB(result._2.toInt,db,Timestamp.valueOf(result._1))      
        }catch{
           case ex:org.postgresql.util.PSQLException => println(ex)
        }
     }

     //统计uv
     //val uvresult=dataSet.filter(_.contains("login,")).map(line=>(line.substring(0,14)+"00:00",1)).groupByKey().map(r=>(r._1,r._2.length)).sortByKey(true).collect()
     val uvresult=dataSet.map(uvmapfunc).distinct().groupByKey().map(r=>(r._1,r._2.length)).sortByKey(true).collect()
     for(result <- uvresult){
        try{
          InsertUVToDB(result._2,db,Timestamp.valueOf(result._1))
        }catch{
          case ex:org.postgresql.util.PSQLException => println(ex)
        }
     }

     //统计top20 url
     val urlcount=dataSet.map(line=>(line.split(" ")(6),1)).reduceByKey(_+_).map{case(key, value)=>(value, key)}.sortByKey(false).top(20)
     for(result <- urlcount){
       try{
         InsertUrlCountToDB((result._2, result._1),db,logDate)
       }catch{
         case ex:org.postgresql.util.PSQLException => println(ex)
       }
         
     }

     //统计二级域名
     //val secondDomains=List("Hall.uu.com.cn", "ask.uu.com.cn", "ask.mykuaiji.com", "service.uu.com.cn", "service.mykuaiji.com", "uu.com")
     val secondDomains=List("Hall.uu.com.cn", "ask.uu.com.cn", "ask.mykuaiji.com", "service.uu.com.cn", "service.mykuaiji.com", "uu.com", "gongzuoquan.com")
     def domainfilter(line:String):Boolean = {
       val linefield = line.split(" ")
       for(domain <- secondDomains) {
         if (linefield(10).contains(domain)) {
           var resourceurl=linefield(6)
           //println(resourceurl)
           if (resourceurl.contains("?")) {
             resourceurl=resourceurl.substring(0,resourceurl.indexOf("?"))
           }
           if (resourceurl.contains(".html") || (!resourceurl.contains(".") && !resourceurl.startsWith("/api/v1"))) {
             return true
           }
         }
       }
       if (linefield(10).startsWith("http://weibo.uu.com.cn") && linefield(6)=="/api/v1/depend/data") {
         return true
       }
       return false
     }
     def domainmap(line:String):(String, String) = {
       val linefield = line.split(" ")
       for (domain <- secondDomains) {
         if (linefield(10).contains(domain)) {
           //return (domain, line)
           return (domain, linefield(0))
         }
       }
       return ("weibo.uu.com.cn", line)
     }
     val sdDataSet=dataSet.filter(domainfilter).map(domainmap)
     val sdpv=sdDataSet.groupByKey().map(r=>(r._1, r._2.length)).collect()
     val sduv=sdDataSet.distinct().groupByKey().map(r=>(r._1, r._2.length)).collect()
     for (result <- sdpv) {
       try{
         InsertSdPVToDB((result._1, result._2),db,logDate)
       }catch{
         case ex:org.postgresql.util.PSQLException => println(ex)
       }
     }
     for (result <- sduv) {
       try{
         InsertSdUVToDB((result._1, result._2),db,logDate)
       }catch{
         case ex:org.postgresql.util.PSQLException => println(ex)
       }
     }
     //sdpv.saveAsTextFile("/home/test/xueyu/sdpv")
     //sduv.saveAsTextFile("/home/test/xueyu/sduv")

     sc.stop()
}
  }

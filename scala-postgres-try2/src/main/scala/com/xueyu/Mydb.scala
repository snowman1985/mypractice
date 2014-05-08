package com.xueyu
import scala.slick.driver.PostgresDriver.simple._
import java.sql.{Timestamp, Time, Date}
import java.text.SimpleDateFormat

case class TestCase(name: String, count: Int, time: Timestamp)
class TestTable(tag:Tag) extends Table[TestCase](tag, "mytestscaladb1") {
  def name = column[String]("name", O.PrimaryKey)
  def count = column[Int]("count")
  def time = column[Timestamp]("time")
  def * = (name, count, time) <> (TestCase.tupled, TestCase.unapply)
}

object mydbtest  {
  def main(args: Array[String]) {
    val db = Database.forURL(url = "jdbc:postgresql://172.18.4.244:5433/scaladb?user=postgres&password=pgpassword", driver = "org.postgresql.Driver")
    val tsFormat = new SimpleDateFormat("yyyy-MM-dd HH:mm:ss")
    def ts(str: String) = new Timestamp(tsFormat.parse(str).getTime)
 
    val MyTests = TableQuery[TestTable]

    db withSession { implicit session: Session =>
      MyTests forceInsertAll(TestCase("xueyu", 37, ts("2013-12-01 11:00:00")))
      MyTests += TestCase("wo de ceshi", 101, ts("2014-02-28 23:02:02")) 
      MyTests += TestCase("datetime test", 121, ts("2014-04-09 10:02:27"))
     
      println("mytestscaladb:")
      MyTests foreach { case TestCase(name, count, time) =>
        println("  " + name + "\t" + count + "\t" + time)
      }

      val q1 = (for {
          c <- MyTests
        } yield (c.count))

      q1 foreach { case (count) =>
        println("q1 query:" + count)
      }
 
    }
  }
} 

package com.xueyu
import MyPostgresDriver.simple._

case class TestCase(name: String, count: Int)
class TestTable(tag:Tag) extends Table[TestCase](tag, "mytestscaladb") {
  def name = column[String]("name", O.PrimaryKey)
  def count = column[Int]("count")
  def * = (name, count) <> (TestCase.tupled, TestCase.unapply)
}

object mydbtest  {
  def main(args: Array[String]) {
  val db = Database.forURL(url = "jdbc:postgresql://172.18.4.244:5433/scaladb?user=postgres&password=pgpassword", driver = "org.postgresql.Driver")

 
  val MyTests = TableQuery[TestTable]

  db withSession { implicit session: Session =>
    MyTests forceInsertAll(TestCase("xueyu", 37))
  }
  }
} 

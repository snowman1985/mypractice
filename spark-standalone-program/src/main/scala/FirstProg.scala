import org.apache.spark.SparkContext
import org.apache.spark.SparkContext._

object SimpleApp {
  def main(args: Array[String]) {
    //val logFile = "$YOUR_SPARK_HOME/README.md" // Should be some file on your system
    val logFile = "/home/mongodbtest/kexueguairen.txt" // Should be some file on your system
    val sc = new SparkContext("spark://mydea01:7077", "Simple App", "/mongodb/largedata/spark/spark-0.9.0-incubating-bin-hadoop2",
      List("file:///mongodb/xueyu/test/first/target/scala-2.10/simple-project_2.10-1.0.jar"))
    val logData = sc.textFile(logFile, 2).cache()
    val numAs = logData.filter(line => line.contains("a")).count()
    val numBs = logData.filter(line => line.contains("b")).count()
    val numThes = logData.filter(line => line.contains("the")).count()
    println("#####Lines with a: %s, Lines with b: %s".format(numAs, numBs))
    println("!!!!!Lines with the: %s".format(numThes))
  }
}

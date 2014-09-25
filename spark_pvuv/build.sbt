name := "KjjyLogAnalysis"

version := "1.0"

scalaVersion := "2.10.4"

libraryDependencies ++= List(
  "com.typesafe.slick" %% "slick" % "2.0.2-RC1",
  "org.slf4j" % "slf4j-nop" % "1.6.4",
  "org.skife.com.typesafe.config" % "typesafe-config" % "0.3.0",
  "org.apache.hadoop" % "hadoop-client" % "2.2.0",
  "org.apache.spark" %% "spark-core" % "0.9.1"
)

resolvers += "Akka Repository" at "http://repo.akka.io/releases/"


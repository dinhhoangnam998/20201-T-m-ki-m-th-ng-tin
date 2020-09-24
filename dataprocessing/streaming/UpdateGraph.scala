import org.apache.log4j.{Level, Logger}
import org.apache.spark.sql.SparkSession
import org.apache.spark.sql.types.{LongType, StringType, StructField, StructType}

object UpdateGraph {

  case class Doc(time: String, content: String, link: String)

  def main(args: Array[String]): Unit = {
    Logger.getLogger("org").setLevel(Level.OFF)
    Logger.getLogger("akka").setLevel(Level.OFF)
    val spark = SparkSession
      .builder()
      .appName("Spark SQL basic example")
      .master("local")
      .config("spark.some.config.option", "some-value")
      .getOrCreate()

    import spark.implicits._

    val schema = StructType(
      StructField("time", StringType, nullable = true) ::
        StructField("content", StringType, nullable = true) ::
        StructField("link", StringType, nullable = true) ::
        Nil)

    val doc = spark.readStream
      .format("json")
      .schema(schema)
      .load("data/json").as[Doc]

    val result = doc.map(t => RestAPI.posDoc(t.time, t.content, t.link)).groupBy("value").count()

    val q2 = result
      .writeStream
      .outputMode("complete")
      .format("console")
      .start()
    q2.awaitTermination()
  }
}

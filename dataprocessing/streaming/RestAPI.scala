import scalaj.http.{Http, HttpOptions}

object RestAPI {

  def post(data: String): String = {
    val result = Http("http://localhost:8081/updateGraph").postData(data)
      .header("Content-Type", "application/json")
      .header("Charset", "UTF-8")
      .option(HttpOptions.readTimeout(10000)).asString
    result.body
  }

  def postName(name: String): String = {
    val data = s"""{"name":"$name"}"""
    post(data)
  }

  def posDoc(time: String, content: String, link: String) = {
    val data =
      s"""
         |{
         | "time": "$time",
         | "content":"$content",
         |  "link":"$link"
         |}""".stripMargin
    post(data)
  }
}

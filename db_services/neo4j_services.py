import inspect
import json

from py2neo import Graph, walk
from ER.Relationship import Relationship
from ER.Entity import Entity
from ER.Patient import Patient
from config.config import Neo4jConfig
from nlp.ERextractor import ER_extractor

graph = Graph(Neo4jConfig.bolt, auth=(Neo4jConfig.username, Neo4jConfig.password))


def mergeP(p):
    match = graph.run("match (p :" + p.label + " {name:$name}) return p ", name=p.name).data()
    if match:
        return match[0]["p"]
    create = graph.run("merge (p:" + p.label + " { name:$name }) "
                                               "set p.age=$age,"
                                               "p.gender=$gender,"
                                               "p.country=$country,"
                                               "p.home_town=$home_town "
                                               "return p",
                       name=p.name,
                       age=p.age,
                       gender=p.gender,
                       country=p.country,
                       home_town=p.home_town).data()
    return create[0]["p"]


def mergeEntity(e):
    merge = graph.run("merge (e :"
                      + e.label +
                      " {name: $name}) return e ", name=e.name).data()

    return merge[0]["e"]


def mergeER(p, r, e):
    mergeP(p),
    mergeEntity(e)

    merge = graph.run("match (p:" + p.label + " {name: $p_name }),(e:"
                      + e.label +
                      " {name:$e_name})"
                      " MERGE (p)-[r:" + r.label + " { time:$r_time, link:$r_link }]->(e) return p,r,e",
                      p_name=p.name,
                      e_name=e.name,

                      r_time=r.time,
                      r_link=r.link).data()
    return merge


def update_graph(doc, time, link):
    BN_list, triplets = ER_extractor(doc, time)

    for bn in BN_list:
        p = Patient()
        p.name = bn[0]
        p.age = bn[1]
        p.gender = bn[2]
        p.home_town = bn[3]
        p.country = bn[4]
        mergeP(p)

    for triplet in triplets:
        p = Patient()
        e = Entity()
        r = Relationship()

        p.name = triplet[0][0]
        r.label = triplet[1][0].replace(" ", "_")
        r.link = link
        if triplet[3] != None:
            r.time = triplet[3][0]
        e.name = triplet[2][0]
        e.label = triplet[2][1]
        mergeEntity(e)
        mergeER(p, r, e)


def matchPRE(p, r, e):
    match = graph.run("match (p:" + p.label + " )-"
                                              "[r:" + r.label + " ]->(e:"
                      + e.label +
                      " )"
                      " where toLower(p.name) = toLower($p_name) and toLower(e.name) = toLower($e_name) "
                      " return p,r,e",
                      p_name=p.name,
                      e_name=e.name).data()
    return match


def matchPR(p, r):
    match = graph.run("match (p:"
                      + p.label + " )-"
                                  "[r:" + r.label + " ]->(e)"
                                                    " where toLower(p.name) = toLower($p_name)"
                                                    " return p,r,e",
                      p_name=p.name).data()
    return match


# return properties of patient
def matchP(p):
    match = graph.run("match (p:BN ) where toLower(p.name) = toLower($p_name) return p",
                      p_name=p.name,
                      ).evaluate()
    if match is None:
        return None
    return dict(match)


# p = Patient()
# p.name= 'BN248'
# print( matchP(p)['name'])

def matchRE(r, e):
    match = graph.run("match (p)-"
                      "[r:" + r.label + " ]->(e:"
                      + e.label +
                      " )"
                      " where toLower(e.name) = toLower($e_name)"
                      " return p,r,e",
                      e_name=e.name).data()
    return match


def matchPE(p, e):
    match = graph.run("match (p:" + p.label + " )"
                                              ",(e:"
                      + e.label +
                      " )"
                      " where toLower(e.name) = toLower($e_name) and toLower(p.name) = toLower($p_name)"
                      " return p,e",
                      p_name=p.name,
                      e_name=e.name,
                      ).data()
    return match


def matchAll_d3format():
    match = graph.run("MATCH (n)-[r]-(m) RETURN n,r, m").to_subgraph()
    nodes = []
    relastionships = []
    for node in match.nodes:
        node_fm = {
            "id": hash(node),
            "labels": [str(node.labels)[1:]],
            "properties": dict(node)
        }
        nodes.append(node_fm)
    for relationship in match.relationships:
        # print(dict(relationship))
        s, r, e = walk(relationship)

        relationship_fm = {
            "id": hash(relationship),
            "type": type(relationship).__name__,
            "startNode": hash(s),
            "endNode": hash(e),
            "properties": dict(relationship),
            "source": hash(s),
            "target": hash(e),
            "linknum": 1
        }
        relastionships.append(relationship_fm)
    d3format = {
        "nodes": nodes,
        "relationships": relastionships
    }
    return d3format


def match_neo4jformat(query="MATCH (n:BN)-[r]-(m) RETURN n,r, m limit 200"):
    match = graph.run(query).to_subgraph()
    nodes = []
    relastionships = []
    # print(match)
    if not match:
        return None
    for node in match.nodes:
        node_fm = {
            "id": str(hash(node)),
            "labels": [str(node.labels)[1:]],
            "properties": dict(node)
        }
        nodes.append(node_fm)

    for relationship in match.relationships:
        # print(dict(relationship))
        s, r, e = walk(relationship)

        relationship_fm = {
            "id": str(hash(relationship)),
            "type": type(relationship).__name__,
            "startNode": str(hash(s)),
            "endNode": str(hash(e)),
            "properties": dict(relationship)
        }
        relastionships.append(relationship_fm)
    neo4jformat = {
        "results": [
            {
                "columns": ["n", "r", "m"],
                "data": [
                    {
                        "graph": {
                            "nodes": nodes,
                            "relationships": relastionships
                        }
                    }
                ]
            }
        ],
        "errors": []
    }
    return neo4jformat

print(match_neo4jformat("MATCH (n:BN)-[r]-(m {name:'Mỹ'}) RETURN n,r, m"))

def involve_info(ps, rs, es):
    where = ""
    if ps:
        where = "Where " + generateOrName(ps, "ps")
        if es:
            where += " or " + generateOrName(es, "es")
    else:
        if es:
            where = "Where " + generateOrName(es, "es")
        else:
            return None
    cypher = "MATCH (ps)-[rs]-(es) " \
             + where + \
             " RETURN ps,rs, es"

    return match_neo4jformat(cypher)


def generateOrName(es, name_e):
    s = ''
    if not es:
        return None
    name = "toLower(" + name_e + ".name) = toLower('"
    for i in es:
        s += name + i.name + "') or "

    return "(" + s[:-3] + ") "


# ex:
# p1 = Patient()
# p1.name="thanh"
# p2 = Patient()
# p2.name ="fsdaf"
#
# print(generateOrName([], "p"))

doc = """THÔNG BÁO VỀ CA BỆNH 223-227: BN223: nữ, 29 tuổi, địa chỉ: Hải Hậu, Nam Định, 
chăm sóc người thân tại Khoa Phục hồi chức năng, Bệnh viện Bạch Mai từ 11/3. 
Từ 11/3-24/3 bệnh nhân thường xuyên đi ăn uống và mua đồ tạp hoá ở căng tin, 
có tiếp xúc với đội cung cấp nước sôi của Công ty Trường Sinh; BN224: nam, 39 tuổi, 
quốc tịch Brazil, có địa chỉ tại phường Thảo Điền, Q.2, TP Hồ Chí Minh. Bệnh nhân có thời 
gian sống cùng phòng với BN158 tại chung cư Masteri, không có triệu chứng lâm sàng; BN225: 
nam, 35 tuổi, quê An Đông, An Dương, Hải Phòng, làm việc ở Matxcova Nga 10 năm nay, về nước trên 
chuyến bay SU290 ghế 50D ngày 25/3/2020 và được cách ly tại Đại học FPT- Hòa Lạc, Thạch Thất; 
BN226: nam, 22 tuổi, về nước cùng chuyến bay với BN 212 ngày 27/3 và được cách ly tại Trường Văn 
hóa Nghệ thuật Vĩnh Phúc; BN227: nam, 31 tuổi, là con của BN209, có tiếp xúc gần tại gia đình trong 
khoảng thời gian từ 16-25/3."""
doc2 = "Bệnh viện Việt Nam - Thuỵ Điển Uông Bí Quảng Ninh cho hay, tính đến 16h ngày 09/02/2020, Bệnh viện có tiếp nhận 9 trường hợp người bệnh nghi ngờ nhiễm nCoV. Trong đó 8/9 ca đã có kết quả âm tính, 1 trường hợp có yếu tố nghi ngờ đã được cách ly theo dõi."
doc3 = "THÔNG BÁO VỀ CÁC CA BỆNH 50, 51, 52, 53: Bệnh nhân thứ 50 (BN50 là nam, 50 tuổi, địa chỉ phố Núi Trúc, Ba Đình, Hà Nội. Bệnh nhân đi công tác tại Paris và về nước ngày 9/3, hiện đang được cách ly tại Bệnh viện Bệnh nhiệt đới trung ương cơ sở Đông Anh, cơ sở Đông Anh, tình trạng sức khoẻ ổn định; Bệnh nhân thứ 51 (BN51) là nữ, 22 tuổi, địa chỉ Xuân Đỉnh, Bắc Từ Liêm, Hà Nội, là du học sinh ở châu Âu, từ ngày 23/02/2020– 12/3/2020 có đi qua nhiều nước, ngày 13/3 bay về Nội Bài trên chuyến bay QR968, hiện đang được cách ly tại Bệnh viện Bệnh nhiệt đới trung ương cơ sở Đông Anh, tình trạng sức khoẻ ổn định; Bệnh nhân thứ 52 (BN52) là nữ, 24 tuổi, địa chỉ Khu 4B, phường Hồng Hải, Hạ Long, Quảng Ninh. Bệnh nhân là hành khách trên chuyến bay ngày từ London về Việt Nam ngày 9/3 và bắt taxi thẳng về nhà tại Hạ Long. Hiện bệnh nhân đang được cách ly tại bệnh viện dã chiến cơ sở số 2 tại tỉnh Quảng Ninh, tình trạng sức khoẻ ổn định; Bệnh nhân thứ 53 (BN53) là nam, 53 tuổi, quốc tịch Cộng hoà Czech, tiền sử chưa ghi nhận bất thường, có tiếp xúc với người Ý. Ngày 10/3/2020, nhập cảnh vào Cảng hàng không quốc tế Tân Sơn Nhất trên chuyến bay QR970, quá cảnh tại sân bay Doha (Quatar). Sau khi vào Việt Nam, bệnh nhân lưu trú tại Quận 1, TP.HCM."
# p13 = "THÔNG BÁO VỀ CA BỆNH 124-134: BN124: nam, 52 tuổi, quốc tịch Brazil, trú tại Quận 2, TP. Hồ Chí Minh. Ngày 14/3/2020, bệnh nhân có đến quán Bar Buddha; BN125: nữ, quốc tịch Nam Phi, 22 tuổi, trú tại Quận 7, TPHCM, đã từng từng đến quán Bar Buddha từ 21h30 ngày 14/3/2020 đến 03h00 ngày 15/3/2020; BN126: nam, quốc tịch Nam Phi, 28 tuổi, trú tại Quận 7, TP Hồ Chí Minh, là bạn với BN125; BN127: nam, 23 tuổi, trú tại Quận Tân Phú, TP. Hồ Chí Minh, là nhân viên phục vụ bàn (theo ca 21h00 - 04h00) tại quán Bar Buddha - Quận 2; BN128: nam, 20 tuổi ở Lê Chân, TP. Hải Phòng, là du học sinh tại Anh, nhập cảnh về Nội Bài ngày 20/03/2020 trên chuyến bay VN0054.  BN129: nam, 20 tuổi ở Nghĩa Tân, Hà Nội, là du học sinh tại Anh, nhập cảnh về Nội Bài ngày 20/03/2020 trên chuyến bay VN0054; BN130: nam, 30 tuổi, địa chỉ ở Quận Bình Chánh, TP. Hồ Chí Minh, là du khách từ Tây Ban Nha, quá cảnh tại Nga và về Nội Bài ngày 22/03/2020 trên chuyến bay SU290; BN131: nam, 23 tuổi, địa chỉ ở Quận Bình Chánh, TP. Hồ Chí Minh, là du khách từ Tây Ban Nha, quá cảnh tại Nga và về Nội Bài ngày 22/03/2020 trên chuyến bay SU290; BN132: nữ, 25 tuổi, địa chỉ ở Quận Long Biên, Hà Nội, là du khách từ Tây Ban Nha, quá cảnh tại Nga và về Nội Bài ngày 22/03/2020 trên chuyến bay SU290; BN133: nữ, 66 tuổi ở Tân Phong, Lai Châu, trong tháng 3/2020 có đến Bệnh viện Bạch Mai điều trị bệnh và 22/03/2020 trở về nhà tại tỉnh Lai Châu; BN134: nam, 10 tuổi ở Thạch Thất, Hà Nội, là du khách từ nước ngoài, nhập cảnh về Nội Bài ngày 18/03/2020 trên chuyến bay SU290."
# p14 = "THÔNG BÁO VỀ CA BỆNH 124-134: BN124: nam, 52 tuổi, quốc tịch Brazil, trú tại Quận 2, TP. Hồ Chí Minh. Ngày 14/3/2020, bệnh nhân có đến quán Bar Buddha; BN125: nữ, quốc tịch Nam Phi, 22 tuổi, trú tại Quận 7, TPHCM, đã từng từng đến quán Bar Buddha từ 21h30 ngày 14/3/2020 đến 03h00 ngày 15/3/2020; BN126: nam, quốc tịch Nam Phi, 28 tuổi, trú tại Quận 7, TP Hồ Chí Minh, là bạn với BN125; BN127: nam, 23 tuổi, trú tại Quận Tân Phú, TP. Hồ Chí Minh, là nhân viên phục vụ bàn (theo ca 21h00 - 04h00) tại quán Bar Buddha - Quận 2; BN128: nam, 20 tuổi ở Lê Chân, TP. Hải Phòng, là du học sinh tại Anh, nhập cảnh về Nội Bài ngày 20/03/2020 trên chuyến bay VN0054.  BN129: nam, 20 tuổi ở Nghĩa Tân, Hà Nội, là du học sinh tại Anh, nhập cảnh về Nội Bài ngày 20/03/2020 trên chuyến bay VN0054; BN130: nam, 30 tuổi, địa chỉ ở Quận Bình Chánh, TP. Hồ Chí Minh, là du khách từ Tây Ban Nha, quá cảnh tại Nga và về Nội Bài ngày 22/03/2020 trên chuyến bay SU290; BN131: nam, 23 tuổi, địa chỉ ở Quận Bình Chánh, TP. Hồ Chí Minh, là du khách từ Tây Ban Nha, quá cảnh tại Nga và về Nội Bài ngày 22/03/2020 trên chuyến bay SU290; BN132: nữ, 25 tuổi, địa chỉ ở Quận Long Biên, Hà Nội, là du khách từ Tây Ban Nha, quá cảnh tại Nga và về Nội Bài ngày 22/03/2020 trên chuyến bay SU290; BN133: nữ, 66 tuổi ở Tân Phong, Lai Châu, trong tháng 3/2020 có đến Bệnh viện Bạch Mai điều trị bệnh và 22/03/2020 trở về nhà tại tỉnh Lai Châu; BN134: nam, 10 tuổi ở Thạch Thất, Hà Nội, là du khách từ nước ngoài, nhập cảnh về Nội Bài ngày 18/03/2020 trên chuyến bay SU290."
# update_graph(doc=p14,time="25/3/2020",link="https://ncov.moh.gov.vn/web/guest/dong-thoi-gian")
# update_graph(doc,"http://google.com")
# p = Patient()
# p.name = "BN221"
# e = Entity()
# e.label = "Location"
# e.name = "HCM"
# r = Relationship()
# r.name = "đến"

# print(matchPR(p, r)[1])
# data = matchAll_neo4jformat()
# print(data)
# print(json.dumps(data))

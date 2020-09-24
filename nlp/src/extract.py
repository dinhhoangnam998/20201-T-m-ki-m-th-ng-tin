# -*- coding: utf8 -*-

import underthesea
import re

from nlp.src.predict import ner_sent, load_model, ner_sent2
from nlp.src.preprocess_raw import preprocess_raw
from config.config import NLPConfig

my_config = NLPConfig()
model_dir = my_config.model_path
data_dir = my_config.data_path

re_cur_time = r'hiện(\s{1,3}(tại|nay)|)'
flags = re.I | re.U


def extract_info(paragraph=None, time_public=None, model=None):
    if not model:
        model = load_model(model_dir + 'covid_ner.job')

    entity_list = ['HOS', 'LOC', 'FLIGHT', 'BN']
    BN_list = list()
    triplets = list()
    tmp_BNid = None
    BNid_set = set()
    BNS_bool = False

    paragraph = preprocess_raw(raw_text=paragraph)
    for sent in underthesea.sent_tokenize(paragraph):
        relation_list = list()
        cur_time = None

        my_ner_sent = ner_sent2(sent, model)

        idx = -1
        for it in my_ner_sent:
            idx += 1
            if it[1] == 'BN' and it[0] == 'BN':
                pass
            elif it[1] == 'BN' and 'BN' in it[0] and len(relation_list) == 0:
                tmp_BNid = it[0]
                if it[0] not in BNid_set:
                    # print('new ' + str(tmp_BNid))
                    # create and add BN to list
                    BNid_set.add(it[0])
                    myBN = [None] * 5
                    myBN[0] = tmp_BNid
                    BN_list.append(myBN)
            elif it[1] == 'BNS' and 'BN' in it[0]:
                BNS_bool = True
            elif it[1] == 'SEX':
                for bn in BN_list:
                    if bn[0] == tmp_BNid:
                        if bn[2] is None:
                            bn[2] = it[0]
                        break
            elif it[1] == 'AGE':
                for bn in BN_list:
                    if bn[0] == tmp_BNid:
                        if bn[1] is None:
                            bn[1] = it[0]
                        break
            elif it[1] == 'ADD':
                for bn in BN_list:
                    if bn[0] == tmp_BNid:
                        if bn[3] is None:
                            bn[3] = it[0]
                        break
            elif it[1] == 'NAT':
                for bn in BN_list:
                    if bn[0] == tmp_BNid:
                        if bn[4] is None: bn[4] = it[0]
                        break
            elif it[1] == 'TIME':
                cur_time = it
            elif it[1] == 'STATUS':
                time_x = None
                if cur_time:
                    time_x = cur_time
                else:  # find next time
                    for idx1 in range(idx + 1, len(my_ner_sent)):
                        it1 = my_ner_sent[idx1]
                        if it1[1] == 'TIME':
                            time_x = it1
                            break

                #  hien tai, hien nay, hien -> time_public
                if time_x and re.search(pattern=re_cur_time, string=time_x[0], flags=flags) and time_public:
                    time_x = (str(time_public), 'TIME')

                if BNS_bool:
                    for id in BNid_set:
                        triplets.append([(id, 'BN'), (it[0], 'R'), ('SARS-CoV-2', 'E'), time_x])
                elif tmp_BNid:
                    triplets.append([(tmp_BNid, 'BN'), (it[0], 'R'), ('SARS-CoV-2', 'E'), time_x])

            elif it[1] == 'R':
                relation_list.append(it)

            elif it[1] in entity_list:
                time_x = None
                if cur_time:
                    time_x = cur_time
                else:  # find next time
                    for idx1 in range(idx + 1, len(my_ner_sent)):
                        it1 = my_ner_sent[idx1]
                        if it1[1] == 'TIME':
                            time_x = it1
                            break

                #  hien tai, hien nay, hien -> time_public
                if time_x and re.search(pattern=re_cur_time, string=time_x[0], flags=flags) and time_public:
                    time_x = (str(time_public), 'TIME')

                if BNS_bool:
                    if len(relation_list) == 0:
                        tmp_relation = ('trên chuyến bay', 'R') if it[1] == 'FLIGHT' else ('liên quan đến', 'R')
                        for id in BNid_set:
                            triplets.append([(id, 'BN'), tmp_relation, it, time_x])
                    else:
                        for id in BNid_set:
                            for relation in relation_list:
                                triplets.append([(id, 'BN'), relation, it, time_x])

                elif tmp_BNid:
                    if len(relation_list) == 0:
                        tmp_relation = ('trên chuyến bay', 'R') if it[1] == 'FLIGHT' else ('liên quan đến', 'R')
                        triplets.append([(tmp_BNid, 'BN'), tmp_relation, it, time_x])
                    else:
                        for relation in relation_list:
                            triplets.append([(tmp_BNid, 'BN'), relation, it, time_x])
                relation_list.clear()

    return BN_list, triplets


if __name__ == "__main__":

    p1 = """THÔNG BÁO VỀ CA BỆNH 335 (BN335): Bệnh nhân nam, 24 tuổi, có địa chỉ tại xã Khôi Kỳ, 
    huyện Đại Từ, tỉnh Thái Nguyên, sống và làm việc tại Kuwait 2 năm. Ngày 16/6 bệnh nhân từ Kuwait 
    (quá cảnh Quatar) về sân bay Tân Sơn Nhất trên chuyến bay H9092 của Bamboo Airways, được cách ly ngay, 
    lấy mẫu xét nghiệm tại Bệnh viện Bệnh nhiệt đới TP.HCM. Kết quả xét nghiệm ngày 16/6 dương tính với SARS-CoV-2. 
    Hiện bệnh nhân được cách ly, điều trị tại Bệnh viện Bệnh nhiệt đới TP.HCM. Như vậy, tính đến 6h ngày 17/6, Việt Nam 
    có tổng cộng 195 ca nhiễm nhập cảnh được cách ly ngay, không có nguy cơ lây ra cộng đồng, đồng thời 
    ghi nhận 62 ngày liên tiếp không có ca nhiễm trong cộng đồng"""

    p3 = """THÔNG BÁO VỀ 2 BN336 - BN342 : 
    BN336: bệnh nhân nam, 29 tuổi, có địa chỉ tại Nghi Lộc, Nghệ An; 
    BN337: bệnh nhân nam, 25 tuổi, có địa chỉ tại Hoằng Hoá, Thanh Hoá; 
    BN338: bệnh nhân nam, 38 tuổi, có địa chỉ tại Lạng Giang, Bắc Giang; 
    BN339: bệnh nhân nam, 37 tuổi, có địa chỉ tại Diễn Châu, Nghệ An; 
    BN340: bệnh nhân nam, 33 tuổi, có địa chỉ tại Yên Thành, Nghệ An; 
    BN341: bệnh nhân nam, 35 tuổi, có địa chỉ tại Tứ Kỳ, Hải Dương; 
    BN342: bệnh nhân nam, 41 tuổi, có địa chỉ tại Hương Khê, Hà Tĩnh. 
    Ngày 16/6 các bệnh nhân này từ Kuwait (quá cảnh Quatar) về sân bay Tân 
    Sơn Nhất, TP. Hồ Chí Minh trên chuyến bay QH9092 và được cách ly ngay tại 
    khu cách ly thị xã Phú Mỹ, tỉnh Bà Rịa-Vũng Tàu. Ngày 17/6, các bệnh nhân 
    được lấy mẫu xét nghiệm. Kết quả xét nghiệm ngày 17/6 là dương tính với SARS-CoV-2. 
    Hiện 7 bệnh nhân được cách ly, điều trị tại Bệnh viện Bà Rịa."""

    p7 = """THÔNG BÁO VỀ CA BỆNH 223-227: BN223: nữ, 29 tuổi, địa chỉ: Hải Hậu, Nam Định, 
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

    p9 = """THÔNG BÁO VỀ 4 CA BỆNH 246 - 249: BN246 - nam, 33 tuổi, ở huyện Yên Thành, Nghệ An, 
    làm đầu bếp tại Moscow (Nga), ngày 24/3 từ Nga trở về Việt Nam trên chuyến bay SU290 (ghế 49F), 
    nhập cảnh Nội Bài ngày 25/3; BN247 - nam, 28 tuổi, ở phường 1, quận Bình Thạnh, TP.HCM, 
    là đồng nghiệp, có tiếp xúc gần với BN124 và BN151; BN248 - nam, 20 tuổi, quốc tịch Việt Nam, 
    từ Mỹ quá cảnh Nhật Bản về Việt Nam trên chuyến bay JL079 ngày 23/3 nhập cảnh tại Tân Sơn Nhất; 
    BN249 - nam, 55 tuổi, quốc tịch Việt Nam, từ Mỹ quá cảnh tại Hồng Kông, nhập cảnh ngày 22/3, 
    khởi phát bệnh tại Mỹ."""

    p10 = """THÔNG BÁO VỀ CA BỆNH 124-134: BN124: nam, 52 tuổi, quốc tịch Brazil, trú tại Quận 2, TP. Hồ Chí Minh. 
    Ngày 14/3/2020, bệnh nhân có đến quán Bar Buddha; BN125: nữ, quốc tịch Nam Phi, 22 tuổi, trú tại Quận 7, TPHCM, 
    đã từng từng đến quán Bar Buddha từ 21h30 ngày 14/3/2020 đến 03h00 ngày 15/3/2020; BN126: nam, quốc tịch Nam Phi, 
    28 tuổi, trú tại Quận 7, TP Hồ Chí Minh, là bạn với BN125; BN127: nam, 23 tuổi, trú tại Quận Tân Phú, 
    TP. Hồ Chí Minh, là nhân viên phục vụ bàn (theo ca 21h00 - 04h00) tại quán Bar Buddha - Quận 2; BN128: 
    nam, 20 tuổi ở Lê Chân, TP. Hải Phòng, là du học sinh tại Anh, nhập cảnh về Nội Bài ngày 20/03/2020 trên 
    chuyến bay VN0054. BN129: nam, 20 tuổi ở Nghĩa Tân, Hà Nội, là du học sinh tại Anh, nhập cảnh về Nội Bài 
    ngày 20/03/2020 trên chuyến bay VN0054; BN130: nam, 30 tuổi, địa chỉ ở Quận Bình Chánh, TP. Hồ Chí Minh, 
    là du khách từ Tây Ban Nha, quá cảnh tại Nga và về Nội Bài ngày 22/03/2020 trên chuyến bay SU290; 
    BN131: nam, 23 tuổi, địa chỉ ở Quận Bình Chánh, TP. Hồ Chí Minh, là du khách từ Tây Ban Nha, quá cảnh tại Nga 
    và về Nội Bài ngày 22/03/2020 trên chuyến bay SU290; BN132: nữ, 25 tuổi, địa chỉ ở Quận Long Biên, Hà Nội, 
    là du khách từ Tây Ban Nha, quá cảnh tại Nga và về Nội Bài ngày 22/03/2020 trên chuyến bay SU290; 
    BN133: nữ, 66 tuổi ở Tân Phong, Lai Châu, trong tháng 3/2020 có đến Bệnh viện Bạch Mai điều trị bệnh và 
    22/03/2020 trở về nhà tại tỉnh Lai Châu; BN134: nam, 10 tuổi ở Thạch Thất, Hà Nội, là du khách từ nước ngoài, 
    nhập cảnh về Nội Bài ngày 18/03/2020 trên chuyến bay SU290."""

    p11 = """bệnh nhân 23 ở Pháp ngày 20/12"""

    model = load_model(model_dir + 'covid_ner_8764w.job')
    BN_list, triplets = extract_info(paragraph=p11, time_public='3/3/2020', model=model)
    print('patient_list')
    for bn in BN_list:
        print(bn)
    print('\ntriplets + time')
    for triplet in triplets:
        print(triplet)

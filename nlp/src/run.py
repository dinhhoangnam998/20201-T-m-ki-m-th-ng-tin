from nlp.src.predict import ner_sent, load_model, ner_sent2
from nlp.src.preprocess_raw import preprocess_raw
from nlp.src.extract import extract_info
from config.config import NLPConfig

my_config = NLPConfig()
model_dir = my_config.model_path
data_dir = my_config.data_path

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

p10 = """THỦ TƯỚNG CHỈ ĐẠO XỬ LÝ VI PHẠM TRONG SỬ DỤNG KINH PHÍ PHÒNG, CHỐNG DỊCH COVID-19: 
Xét đề nghị của Bộ Công an về tình hình vi phạm trong việc sử dụng kinh phí chống dịch COVID-19 tại một số địa phương, 
Thủ tướng Chính phủ Nguyễn Xuân Phúc chỉ đạo Bộ Y tế, Ủy ban nhân dân các tỉnh, thành phố trực thuộc Trung ương khẩn 
trương rà soát, chấn chỉnh, thẩm định lại và thanh tra việc thực hiện các gói thầu mua sắm trang thiết bị y tế, vật 
tư tiêu hao, thuốc chữa bệnh… phục vụ công tác phòng, chống dịch COVID-19, nhất là các gói thầu mua sắm hệ thống máy 
xét nghiệm sinh hóa, máy thở, khẩu trang y tế, hóa chất vật tư tiêu hao; nếu có dấu hiệu vi phạm pháp luật thì chuyển 
hồ sơ, tài liệu cho cơ quan điều tra để điều tra làm rõ, xử lý nghiêm theo quy định của pháp luật."""

p11 = """THÔNG BÁO VỀ 3 CA BỆNH MỚI (BN350 - BN352): 3 ca dương tính này được cách ly ngay sau khi nhập cảnh, không lây 
ra cộng đồng. BN350: nam, 36 tuổi, có địa chỉ tại huyện Hưng Hà, Thái Bình. Đây là hành khách trên chuyến bay QH9092 từ 
Kuwait (quá cảnh Qatar) nhập cảnh Sân bay Tân Sơn Nhất ngày 16/6/2020 (trước đó đã ghi nhận 8 trường hợp bệnh COVID-19 
trên chuyến bay này). Hành khách này được cách ly tập trung, lấy mẫu xét nghiệm tại thị xã Phú Mỹ, Bà Rịa - Vũng Tàu; 
BN351: nữ, 46 tuổi, có địa chỉ tại huyện Như Xuân, Thanh Hoá; BN352: nữ, 30 tuổi, có địa chỉ tại huyện Cẩm Thuỷ, Thanh Hoá. 
BN351, 352 từ Kuwait về sân bay Nội Bài trên chuyến bay KU1513 và được cách ly tập trung tại tỉnh Hưng Yên ngay sau khi 
nhập cảnh. Hiện 2 bệnh nhân đang được cách ly, điều trị tại Bệnh viện Bệnh Nhiệt đới Trung ương cơ sở 2."""
p12="THÔNG BÁO VỀ CÁC CA BỆNH 50, 51, 52, 53: Bệnh nhân thứ 50 (BN50 là nam, 50 tuổi, địa chỉ phố Núi Trúc, Ba Đình, Hà Nội. Bệnh nhân đi công tác tại Paris và về nước ngày 9/3, hiện đang được cách ly tại Bệnh viện Bệnh nhiệt đới trung ương cơ sở Đông Anh, cơ sở Đông Anh, tình trạng sức khoẻ ổn định; Bệnh nhân thứ 51 (BN51) là nữ, 22 tuổi, địa chỉ Xuân Đỉnh, Bắc Từ Liêm, Hà Nội, là du học sinh ở châu Âu, từ ngày 23/02/2020– 12/3/2020 có đi qua nhiều nước, ngày 13/3 bay về Nội Bài trên chuyến bay QR968, hiện đang được cách ly tại Bệnh viện Bệnh nhiệt đới trung ương cơ sở Đông Anh, tình trạng sức khoẻ ổn định; Bệnh nhân thứ 52 (BN52) là nữ, 24 tuổi, địa chỉ Khu 4B, phường Hồng Hải, Hạ Long, Quảng Ninh. Bệnh nhân là hành khách trên chuyến bay ngày từ London về Việt Nam ngày 9/3 và bắt taxi thẳng về nhà tại Hạ Long. Hiện bệnh nhân đang được cách ly tại bệnh viện dã chiến cơ sở số 2 tại tỉnh Quảng Ninh, tình trạng sức khoẻ ổn định; Bệnh nhân thứ 53 (BN53) là nam, 53 tuổi, quốc tịch Cộng hoà Czech, tiền sử chưa ghi nhận bất thường, có tiếp xúc với người Ý. Ngày 10/3/2020, nhập cảnh vào Cảng hàng không quốc tế Tân Sơn Nhất trên chuyến bay QR970, quá cảnh tại sân bay Doha (Quatar). Sau khi vào Việt Nam, bệnh nhân lưu trú tại Quận 1, TP.HCM."
p13= "THÔNG BÁO VỀ CA BỆNH 124-134: BN124: nam, 52 tuổi, quốc tịch Brazil, trú tại Quận 2, TP. Hồ Chí Minh. Ngày 14/3/2020, bệnh nhân có đến quán Bar Buddha; BN125: nữ, quốc tịch Nam Phi, 22 tuổi, trú tại Quận 7, TPHCM, đã từng từng đến quán Bar Buddha từ 21h30 ngày 14/3/2020 đến 03h00 ngày 15/3/2020; BN126: nam, quốc tịch Nam Phi, 28 tuổi, trú tại Quận 7, TP Hồ Chí Minh, là bạn với BN125; BN127: nam, 23 tuổi, trú tại Quận Tân Phú, TP. Hồ Chí Minh, là nhân viên phục vụ bàn (theo ca 21h00 - 04h00) tại quán Bar Buddha - Quận 2; BN128: nam, 20 tuổi ở Lê Chân, TP. Hải Phòng, là du học sinh tại Anh, nhập cảnh về Nội Bài ngày 20/03/2020 trên chuyến bay VN0054.  BN129: nam, 20 tuổi ở Nghĩa Tân, Hà Nội, là du học sinh tại Anh, nhập cảnh về Nội Bài ngày 20/03/2020 trên chuyến bay VN0054; BN130: nam, 30 tuổi, địa chỉ ở Quận Bình Chánh, TP. Hồ Chí Minh, là du khách từ Tây Ban Nha, quá cảnh tại Nga và về Nội Bài ngày 22/03/2020 trên chuyến bay SU290; BN131: nam, 23 tuổi, địa chỉ ở Quận Bình Chánh, TP. Hồ Chí Minh, là du khách từ Tây Ban Nha, quá cảnh tại Nga và về Nội Bài ngày 22/03/2020 trên chuyến bay SU290; BN132: nữ, 25 tuổi, địa chỉ ở Quận Long Biên, Hà Nội, là du khách từ Tây Ban Nha, quá cảnh tại Nga và về Nội Bài ngày 22/03/2020 trên chuyến bay SU290; BN133: nữ, 66 tuổi ở Tân Phong, Lai Châu, trong tháng 3/2020 có đến Bệnh viện Bạch Mai điều trị bệnh và 22/03/2020 trở về nhà tại tỉnh Lai Châu; BN134: nam, 10 tuổi ở Thạch Thất, Hà Nội, là du khách từ nước ngoài, nhập cảnh về Nội Bài ngày 18/03/2020 trên chuyến bay SU290."
model = load_model(model_dir + 'covid_ner_8764w.job')
BN_list, triplets = extract_info(paragraph=p13, model=model,time_public="25/3/2020")
print('patient_list')
for bn in BN_list:
    print(bn)
print('\ntriplets + time')
for triplet in triplets:
    print(triplet)


# -*- coding: utf8 -*-

import re
import codecs
from config.config import NLPConfig

my_config = NLPConfig()
model_dir = my_config.model_path
data_dir = my_config.data_path


def preprocess_raw(raw_file=None, raw_text=None, save_to=None):
    flags = re.I | re.U
    text = ''
    if raw_file:
        with codecs.open(raw_file, 'r', encoding='utf-8', errors='ignore') as fdata:
            lines = fdata.readlines()
            for line in lines:
                text += line
    else:
        text = raw_text

    BNx_y = r'(CA\s{0,2}BỆNH|BỆNH\s{0,2}NHÂN)((\s{0,2}(SỐ|THỨ)\s{0,2})|\s{0,2}|)(([0-9]{1,4})(\s{0,3}-\s{0,3})([0-9]{1,4}))'
    BNx = r'(CA\s{0,2}BỆNH|BỆNH\s{0,2}NHÂN)((\s{0,2}(SỐ|THỨ)\s{0,2})|\s{0,2}|)([0-9]{1,4})'
    BN = r'bệnh\s{1,3}nhân'
    BN_x = r'(BN\s{1,3})([0-9]{1,4})'

    # Ca benh 23 - 24 -> BN23, BN24
    text = re.sub(pattern=BNx_y, repl=r'BN\6, BN\8', string=text, flags=flags)

    # Ca benh thu, ca benh so, benh nhan thu, benh nhan so, benh nhan 34 -> BN34
    text = re.sub(pattern=BNx, repl=r'BN\5', string=text, flags=flags)

    # Benh nhan, benh nhan, BENH NHAN -> BN
    text = re.sub(pattern=BN, repl='BN', string=text, flags=flags)

    # BN 23 -> BN23
    text = re.sub(pattern=BN_x, repl=r'BN\2', string=text, flags=flags)

    #  ; -> .
    text = text.replace(';', '.')

    if save_to:
        with codecs.open(save_to, 'w', encoding='utf-8', errors='ignore') as save_file:
            save_file.write(text)
            print('save data to: ' + str(save_to))

    return text


if __name__ == "__main__":
    p1 = """THÔNG BÁO VỀ 2 CA BỆNH 259 - 260: BN259 - nữ, 41 tuổi, ở xóm Bàng, thôn Hạ Lôi, 
    xã Mê Linh, huyện Mê Linh, Hà  Nội, là vợ BN254, bệnh nhân thỉnh thoảng có đi giao hoa tại thôn 
    Liễu Trì, xã Mê Linh và một số nơi khác khi có đơn hàng, thường xuyên mua hàng tại 
    nhà BN250 (lần cuối ngày 25/3). Từ ngày 03/4-06/4, có đi sang xóm, thôn khác gồm xóm Chùa, 
    xóm Ao Sen, thôn Liễu Trì để giao hoa và mua đồ, có tiếp xúc nhiều người. Lần cuối tiếp xúc 
    chồng là BN254 vào 8/4, trước khi BN254 lên chạy thận ở BV Thận Hà Nội; BN260 - nữ, 35 tuổi, 
    quốc tịch Việt Nam, địa chỉ ở xóm Đường, thôn Hạ Lôi, làm nghề trồng hoa, không đi đâu xa BỆNH NHÂN
    trong vòng 2 tuần gần đây. Hàng ngày thường đi chợ sau đó ra đồng chăm hoa rồi về nhà. Có thói quen 
    mua thịt tại nhà Bảy Huấn (tại xóm Đường) cũng là nơi BN259 hay tới mua thịt. Ngày 6/4, 
    có tiếp xúc gần với 2 người F1 của BN243 khi đi giao hoa. 
    CA BỆNH SỐ 5. CA BỆNH THỨ 5, BỆNH NHÂN SỐ 29, BỆNH NHÂN 23, 
    BỆNH NHÂN65, bệnh nhân đi qua Pháp"""

    p2 = """THÔNG BÁO VỀ CA BỆNH 267: BN267 là nam giới, 46 tuổi, xóm Hội, Hạ Lôi, Mê Linh, Hà Nội, 
    là bố của BN 257, chồng của BN 258, có tiếp xúc gần với BN243 tại nhà ngày 20/3. Ngày 8/4, 
    được cách ly tập trung tại Hà Nội. Ngày 13/4 bệnh nhân khởi phát với triệu chứng sốt nhẹ, mệt mỏi, 
    đau rát họng, đau người, được lấy mẫu bệnh phẩm. Xét nghiệm ngày 14/4 cho kết quả dương tính với 
    SARS-CoV-2. Hiện bệnh nhân được cách ly, điều trị tại Bệnh viện Bệnh Nhiệt đới 
    Trung ương cơ sở 2."""

    # data_dir = 'c:/Users/T470/OneDrive - Hanoi University of Science and Technology/Documents/ai/practice_code/covid19/data/'
    # txt = preprocess_raw(raw_file=data_dir + 'test_pre.txt', save_to=data_dir + 'test_pred_save.txt')

    txt = preprocess_raw(raw_text=p2)
    print(txt)

# -*- coding: utf8 -*-

from joblib import load
from underthesea import ner

from nlp.src.train_CRF import sent2features
from nlp.src.preprocess_raw import preprocess_raw
from config.config import NLPConfig

my_config = NLPConfig()
model_dir = my_config.model_path
data_dir = my_config.data_path


def load_model(file):
    model = load(file)
    return model


def ner_sent(sent, crf):
    # mysent = preprocess_raw(raw_text=sent)
    mysent = sent
    mysent = ner(mysent) #list of tuple - list of words

    # convert mysent: list of tuple -> tmp_list list of list
    tmp_list = list()
    tmp_list = [list(word) for word in mysent]

    # remove CHUNK tag
    [word.pop(2) for word in tmp_list]

    #predict
    pred = crf.predict([sent2features(tmp_list)])
    pred = pred[0]

    #list of tuple(word, tag)
    mylist = list()
    for i in range(len(mysent)):
        mylist.append(tuple([mysent[i][0], pred[i]]))

    return mylist


def ner_sent2(sent, crf):
    tmp_list = list()
    return_list = list()
    my_ner_sent = ner_sent(sent, crf)
    for i in range(len(my_ner_sent)-1):
        it = my_ner_sent[i]
        it_next = my_ner_sent[i+1]
        tmp_list.append(it[0])

        if it[1][-1] != it_next[1][-1]:
            return_list.append(tuple([' '.join(tmp_list), it[1] if len(it[1]) == 1 else it[1][2:]]))
            tmp_list.clear()
   
    last_it = my_ner_sent[-1]
    tmp_list.append(last_it[0])
    return_list.append(tuple([' '.join(tmp_list), last_it[1] if len(last_it[1]) == 1 else last_it[1][2:]]))

    return return_list


if __name__ == "__main__":
    from underthesea import sent_tokenize

    model_dir = model_dir
    model = load_model(model_dir + 'covid_ner.job')
    p1 = """THÔNG BÁO VỀ 3 CA BỆNH 263 - 265: BN263 - nữ, 45 tuổi, trú tại Hạ Lôi, Mê Linh, Hà Nội. 
    Ngày 25/3, bệnh nhân có biểu hiện sốt rét, đau rát họng, ho khan, mệt, di chuyển trên chuyến bay VN673;                                                                          
    Bệnh nhân thuộc diện sàng lọc và được lấy mẫu xét nghiệm ngày 11/4, được kết 
    luận dương tính với SARS-CoV-2 vào ngày 13/4, hiện đang được cách ly, điều trị tại 
    BV Bệnh nhiệt đới Trung ương cơ sở 2; 
    BN264 - nữ, 24 tuổi, trú tại Hạ Lôi, thuộc diện sàng lọc và được lấy mẫu xét nghiệm ngày 11/4, 
    có kết quả xét nghiệm dương tính với SARS-CoV-2 vào ngày 13/4, hiện đang được cách ly, 
    điều trị tại BV Bệnh nhiệt đới Trung ương cơ sở 2; 
    BN265 - nam, 26 tuổi, trú tại Hà Tĩnh, ngày 23/3 từ Thái Lan nhập cảnh về Việt Nam 
    qua cửa khẩu Cha Lo, Quảng Bình, hiện đang được cách ly, điều trị tại Bệnh viện Cầu Treo, Hà Tĩnh."""
    p1 = preprocess_raw(raw_text=p1)
    for sent in sent_tokenize(p1):
        for it in ner_sent2(sent, model):
            print(it)

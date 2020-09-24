# -*- coding: utf8 -*-

import underthesea
import pandas as pd
import codecs


def create_data(file=None, save_to=None):
    """
    text file to csv file: columns=['SENT#', 'WORD', 'POS', 'CHUNK', 'NER']
    """
    text = ''
    with codecs.open(file, 'r', encoding='utf-8', errors='ignore') as fdata:
            lines = fdata.readlines()
            for line in lines:
                text += line 

    df = pd.DataFrame(columns=['SENT#', 'WORD', 'POS', 'CHUNK', 'NER'])
    i = 0
    for sent in underthesea.sent_tokenize(text):
        tdf = pd.DataFrame(underthesea.ner(sent), columns=['WORD', 'POS', 'CHUNK', 'NER'])
        tdf.insert(loc=0, column='SENT#', value=[i]*len(tdf))
        df = df.append(tdf, ignore_index=True)
        i += 1

    df = df.drop(columns=['CHUNK'])
    df.to_csv(save_to, index=False)
    print('saved to ' + save_to);


if __name__ == "__main__":
    from config.config import NLPConfig
    my_config = NLPConfig()
    model_dir = my_config.model_path
    data_dir = my_config.data_path

    create_data(data_dir + 'test_pre.txt', data_dir + 'test1.csv')
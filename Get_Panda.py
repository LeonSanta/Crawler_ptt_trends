import pathlib
from typing import re

import pandas
import jieba


emotion_file_path = str(pathlib.Path(__file__).parent.absolute())
emotion_table = pandas.read_excel(emotion_file_path + '/panda_dictionary/情感词典修改版.xlsx')
emotion_table.drop(['Unnamed: 10', 'Unnamed: 11'], inplace=True, axis=1)
pos_table = pandas.read_excel(emotion_file_path + '/panda_dictionary/情感词典修改版.xlsx', sheet_name='Sheet2')
neg_table = pandas.read_excel(emotion_file_path + '/panda_dictionary/情感词典修改版.xlsx', sheet_name='Sheet3')

pos_dict = dict(zip(list(pos_table.posword), list(pos_table.score)))
neg_dict = dict(zip(list(neg_table.negword), map(lambda a: a * (0 - 1), list(neg_table.score))))
emotion_dict = {**pos_dict, **neg_dict}
print(emotion_dict)
stop_file = open(emotion_file_path + "/jieba_dictionary/stop.txt", 'r', encoding="utf-8")
stop_words = stop_file.read().strip().replace("\n", "").split(",")
stop_file.close()

for w in emotion_dict.keys():
    jieba.suggest_freq(w, True)


def sent2word(sentence, stop_word=stop_words):
    words = jieba.cut(sentence, HMM=False)
    words = [w for w in words if w not in stop_word]
    return words


def get_emotion(sent):
    tokens = sent2word(sent)
    score = 0
    word_count = 0
    for w in tokens:
        if w in emotion_dict.keys():
            score += emotion_dict[w]
            word_count += 1
    if word_count != 0:
        return score / word_count
    else:
        return 0

from __future__ import print_function
import json
import os
import six
import paddlehub as hub


def main(text_array):
    # 載入senta模型
    senta = hub.Module(name="senta_bilstm")

    # 指定模型輸入
    input_dict = {"text": text_array}

    # 把資料餵給senta模型的文字分類函式
    results = senta.sentiment_classify(data=input_dict)

    # 遍歷分析每個短文字
    for index, text in enumerate(text_array):
        results[index]["text"] = text

    return results

    #for index, result in enumerate(results):
            #print('text: {},    predict: {}, positive_probs:{}'.format(results[index]['text'], results[index]['sentiment_key'], results[index]['positive_probs']))

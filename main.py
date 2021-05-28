import os
from os import listdir
from os.path import isfile, join

import Get_Index
import pathlib
import Get_jieba
import Get_Content
import Get_Emotion

from datetime import datetime

board = "car"
start_date = "2021/05/12"
end_date = "2021/05/12"
execute_time = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
file_path = str(pathlib.Path(__file__).parent.absolute()) + "/file/" + board + "/" + execute_time + "/"
# file_path = str(pathlib.Path(__file__).parent.absolute()) + "/file/" + board + "/2021_05_16_13_40_00/"
filename = file_path + "Full_Data, Board-" + board + ", From-" + start_date.replace("/", "_") + "~" + \
           end_date.replace("/", "_") + ", AT-" + execute_time + ".txt"


def get_trends():
    top_n = 20
    idf_file_name = "jieba_dictionary/idf_Car_Type.txt," \
                    "jieba_dictionary/idf_Car_Component.txt"
    stop_file_name = "jieba_dictionary/stop.txt"
    alias_name_file_name = "jieba_dictionary/alias_name.txt"
    dictionary_file_name = "jieba_dictionary/Car_Type.txt," \
                           "jieba_dictionary/Car_Component.txt"
    # 取得所有生成的文章、推文的檔案
    for j in range(0, len(dictionary_file_name.split(","))):
        all_file_name = [f for f in listdir(file_path) if isfile(join(file_path, f))]
        total_trends_list = {}
        for i in range(1, len(all_file_name)):

            # 這篇文章的關鍵字斷詞排名
            post_trends_list = {}

            # 這篇文章下方推文的關鍵字斷詞排名
            reply_trends_list = {}

            # 如果是文章內容，取得文章前N個加權斷詞
            if all_file_name[i].find("Content") > -1:
                post_trends_list = Get_jieba.main(file_path + all_file_name[i]
                                                  , idf_file_name.split(",")[j], stop_file_name,
                                                  dictionary_file_name.split(",")[j], top_n, alias_name_file_name)

                # 取得這篇文章所有推文數量，沒有推文只算一

                if os.path.isfile(file_path + all_file_name[i].replace("Content", "Reply")):
                    push_count = len(open(file_path + all_file_name[i].replace("Content", "Reply"), 'r',
                                          encoding="utf-8").readlines())
                    reply_trends_list = Get_jieba.main(file_path + all_file_name[i].replace("Content", "Reply")
                                                       , idf_file_name.split(",")[j], stop_file_name
                                                       , dictionary_file_name.split(",")[j], top_n,
                                                       alias_name_file_name)
                else:
                    push_count = 1

                # 依據這篇文章算出來的前N斷詞權重，在乘上推文數量(包含推和噓和箭頭)
                for trends_word in post_trends_list:
                    post_trends_list[trends_word] *= push_count

                    # 算好後加到total_trends_list，因為是key vlaue list，所以相同的斷詞，加權後的權重是要加上去
                    if trends_word in total_trends_list.keys():
                        total_trends_list[trends_word] += post_trends_list[trends_word]
                    else:
                        total_trends_list[trends_word] = post_trends_list[trends_word]

                # 依據這篇文章下方推文算出來的前N斷詞權重，在乘上推文數量(包含推和噓和箭頭)
                for trends_word in reply_trends_list:
                    reply_trends_list[trends_word] *= push_count

                    # 算好後加到total_trends_list，因為是key vlaue list，所以相同的斷詞，加權後的權重是要加上去
                    if trends_word in total_trends_list.keys():
                        total_trends_list[trends_word] += + reply_trends_list[trends_word]
                    else:
                        total_trends_list[trends_word] = reply_trends_list[trends_word]

        # 將每篇文章的斷詞 加權後的權重(包含推文)，排序前N個，取得看板在這段起訖時間內，發文聲量最高的前N名
        total_post_trends_list = list(total_trends_list.items())
        total_post_trends_list.sort(key=lambda x: x[1], reverse=True)
        post_file_name = file_path + dictionary_file_name.split(",")[j] \
            .replace("jieba_dictionary/", "") + "_Top_" + str(top_n) + ".txt"

        for i in range(0, top_n):
            # Get_Content.print_to_file(total_post_trends_list[i][0])
            Get_Content.print_to_file(post_file_name, str(i + 1) + " : " + total_post_trends_list[i][0])
            print(str(i + 1) + ":" + total_post_trends_list[i][0], total_post_trends_list[i][1])


def get_emotion():
    all_file_name = [f for f in listdir(file_path) if isfile(join(file_path, f))]
    total_trends_list = {}
    for i in range(1, len(all_file_name)):

        # 這篇文章的關鍵字斷詞排名
        post_trends_list = {}

        # 這篇文章下方推文的關鍵字斷詞排名
        reply_trends_list = []

        # 如果是文章內容，取得文章前N個加權斷詞
        if all_file_name[i].find("Content") > -1:
            post_trends_list = Get_jieba.main(file_path + all_file_name[i]
                                              , "jieba_dictionary/idf_Car.txt", "jieba_dictionary/stop.txt",
                                              "jieba_dictionary/Car.txt", 5, "jieba_dictionary/alias_name.txt")
            if os.path.isfile(file_path + all_file_name[i].replace("Content", "Reply")):
                file = open(file_path + all_file_name[i].replace("Content", "Reply"), "r", encoding="utf-8")
                text = file.readlines()
                for j in range(0, len(text)):
                    reply_trends_list.append(text[j].strip())

            if len(reply_trends_list) > 0:
                Get_Content.print_to_file(file_path + all_file_name[i].replace("Content", "Reply_Emotion"), post_trends_list)
                emotion = Get_Emotion.main(reply_trends_list)

                for index, result in enumerate(emotion):
                    Get_Content.print_to_file(file_path + all_file_name[i].replace("Content", "Reply_Emotion"),
                                              'text: {},    predict: {}, positive_probs:{}'.format(emotion[index]['text']
                                                                                    , emotion[index]['sentiment_key']
                                                                                    , emotion[index]['positive_probs']))


if __name__ == "__main__":
    # 取得起始、結束index
    start_index_array_string, end_index_array_string = Get_Index.main(board, start_date, end_date)

    # 依據file_name製作文章檔案，每一篇文章和留言都切成一個檔案
    Get_Content.main(board, start_index_array_string, end_index_array_string, start_date, end_date, filename,execute_time)

    # 依據上面寫入的檔案，取得前N斷詞
    get_trends()

    # 依據上面寫入的檔案，取得每一篇文章前五個斷詞，和下方推文的情緒
    get_emotion()

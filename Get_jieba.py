import jieba.analyse
from collections import Counter


def main(file_name, idf_file_name, stop_file_name, dictionary_file_name, top_n, alias_name_file_name):

    # 製作同意詞
    alias_name_text = open(alias_name_file_name, 'r', encoding="utf-8")
    alias_name_text_array = alias_name_text.read().strip().replace("\n", "").split(",")
    alias_name_text.close()

    # 回傳list
    return_list = {}

    # 製作權重KEY VALUE
    weight_file = open(idf_file_name, 'r', encoding="utf-8")
    weight_line = weight_file.readlines()
    weight_file.close()
    weight_list = {}
    for line in weight_line:
        weight_list[line[:line.find(" ")]] = int(line[line.find(" ") + 1:])

    # 取得中斷字
    word_stop_file = open(stop_file_name, 'r', encoding="utf-8")
    word_stop_content = word_stop_file.read().split(",")
    word_stop_file.close()

    # 取得文章然後將其斷詞
    content_file = open(file_name, 'r', encoding="utf-8")
    jieba.load_userdict(dictionary_file_name)
    content_file_text = content_file.read()

    # 將文章內容的同義詞替換
    for i in range(0,len(alias_name_text_array)):
        alias_name = alias_name_text_array[i][:alias_name_text_array[i].find("=") - 1]
        alias_text = alias_name_text_array[i][alias_name_text_array[i].find("=") + 2:]
        content_file_text = content_file_text.replace(alias_name, alias_text)

    # 斷詞
    words = jieba.lcut(content_file_text)

    # 取得字頻
    word_list = Counter(words)

    # 關閉檔案
    content_file.close()

    # 刪除不要的斷詞，一個字的斷詞，中斷字裡面的斷詞
    keys = list(word_list.keys())
    for key in keys:
        if len(key) == 1:
            del word_list[key]
        elif key in word_stop_content:
            del word_list[key]

    # 算出權重值
    for key in list(word_list.keys()):
        weight = 1
        if key in weight_list:
            weight = weight_list[key]
        word_list[key] *= weight

    # 依據加權值排序，回傳前N個
    items = list(word_list.items())
    items.sort(key=lambda x: x[1], reverse=True)
    for i in range(0, top_n if len(items) >= top_n else len(items)):
        return_list[items[i][0]] = items[i][1]

    return return_list


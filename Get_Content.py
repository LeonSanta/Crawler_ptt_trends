import errno
import os
import pathlib

import requests
import Get_jieba
from bs4 import BeautifulSoup
from datetime import datetime


def check_file_exist(file_name):
    if not os.path.exists(os.path.dirname(file_name)):
        try:
            os.makedirs(os.path.dirname(file_name), exist_ok=False)
        except OSError as exc:  # Guard against race condition
            if exc.errno != errno.EEXIST:
                raise


def print_to_file(filename, output):
    check_file_exist(filename)
    file = open(filename, "a", encoding="utf-8")
    file.write(output.upper())
    file.write("\n")
    # if filename.find("Trends_Content_Push") > -1:
    # print(output)


def print_bar_to_file(filename, bar_type):
    check_file_exist(filename)
    file = open(filename, "a", encoding="utf-8")

    for i in range(0, 80):
        file.write(bar_type)
        # print(bar_type, end='')

    file.write("\n")


def main(board_array_string, start_index_array_string, end_index_array_string
         , start_date_string, end_date_string
         , filename, execute_time):
    board_array = board_array_string.split(",")
    end_date = datetime.strptime(end_date_string, "%Y/%m/%d")
    start_date = datetime.strptime(start_date_string, "%Y/%m/%d")
    start_index_array = start_index_array_string.split(",")
    end_index_array = end_index_array_string.split(",")

    full_data = filename
    each_post_file_name = str(pathlib.Path(__file__).parent.absolute()) + \
                          "/file/" + board_array_string + "/" + execute_time + "/Post_index.txt"

    each_post_reply_file_name = str(pathlib.Path(__file__).parent.absolute()) + \
                                "/file/" + board_array_string + "/" + execute_time + "/Post_reply_index.txt"

    # trends_content_data = filename.replace("Full_Data", "Trends_Content_Push")

    # 計算本次爬的第幾篇有效文章
    post_count = 0
    for i in range(0, len(board_array)):
        print_bar_to_file(full_data, "-")
        print_to_file(full_data, " PPT看版： " + board_array[i] +
                      " Start Index: " + start_index_array[i] +
                      " End Index: " + end_index_array[i])
        print_bar_to_file(full_data, "-")

        # 這一看板的起迄index
        start_index = int(start_index_array[i])
        end_index = int(end_index_array[i])
        now_index = int(start_index_array[i])
        while True & (now_index <= end_index):
            get_file_percentage = round((now_index - start_index) / (end_index - start_index) * 100, 4)
            print("Board :　" + board_array[i] + " Getting file : " + str(get_file_percentage) + "%")
            url = "https://www.ptt.cc/bbs/" + board_array[i] + "/index" + str(now_index) + ".html"
            my_headers = {'cookie': 'over18=1;'}
            response = requests.get(url, headers=my_headers)
            html_text = response.text
            page_soup = BeautifulSoup(html_text, 'html.parser')
            now_index += 1
            page_trends = page_soup.find_all("div", class_="r-ent")

            # 開始抓每一個文章

            for j in range(0, len(page_trends)):
                # 標題不能同時包含已被、刪除
                if (page_trends[j].find("div", class_="title").text.find("已被") > -1) & \
                        (page_trends[j].find("div", class_="title").text.find("刪除") > -1):
                    continue

                trends_url = requests.get("https://www.ptt.cc" + page_trends[j].find("a")["href"], headers = my_headers)
                trends_html_text = trends_url.text
                trends_soup = BeautifulSoup(trends_html_text, 'html.parser')

                # 取得文章日期字串，找不到就不做了
                trends_date = trends_soup.find_all("span", class_="article-meta-value")

                if len(trends_date) >= 4:
                    trends_date_string = trends_date[3].text[:24]
                elif len(trends_date) == 3:
                    trends_date_string = trends_date[2].text[:24]
                elif len(trends_date) == 0:
                    continue

                trends_datetime = datetime.strptime(trends_date_string, "%a %b %d %H:%M:%S %Y")

                # 確認發文時間後，取得貼文內資訊
                if ((end_date - trends_datetime).days < -1) | ((trends_datetime - start_date).days < 0):
                    continue
                # 整理推文數
                if page_trends[j].find("div", class_="nrec").find("span") is None:
                    trends_push_count = "0"
                else:
                    trends_push_count = page_trends[j].find("div", class_="nrec").find("span").text

                # 整理標題和分類
                trends_total_title = page_trends[j].find("a").text
                if (trends_total_title.find("[") > -1) & (trends_total_title.find("]") > -1):
                    trends_category = trends_total_title[trends_total_title.find("["): trends_total_title.find("]") + 1]
                else:
                    trends_category = ""
                trends_title = trends_total_title.replace(trends_category, "").strip()

                # 是否有要排除的分類
                # if "[新聞]".find(trends_category.strip()) > -1:
                # continue

                print_bar_to_file(full_data, "=")

                print_to_file(full_data, "推數：" + trends_push_count)
                print_to_file(full_data, "分類：" + trends_category)
                print_to_file(full_data, "標題：" + trends_title)
                print_to_file(full_data, "文章網址：https://www.ptt.cc" + page_trends[j].find("a")["href"])
                print_to_file(full_data, "時間：" + trends_datetime.strftime("%Y/%m/%d %H:%M:%S"))

                trends_content = trends_soup.find("div", id="main-content")

                # 只保留文章內容本身，去除作者、標題、看板、時間、引述、簽名檔，作者回復推文
                trends_push = trends_content.find_all("div", class_="push")
                trends_info_1 = trends_content.find_all("div", class_="article-metaline")
                trends_info_2 = trends_content.find_all("div", class_="article-metaline-right")
                trends_info_3 = trends_content.find_all("span", class_="f2")
                trends_quote = trends_content.find_all("span", class_="f6")
                trends_quote_title = ""

                push_count = 0

                # 文章內容移除推文，如果推文內容不齊全(<4是指，推文類別、作者、內容、標題)，或是包含連結就刪除
                while push_count < len(trends_push):
                    trends_push[push_count].extract()
                    if len(trends_push[push_count].find_all("span")) < 4:
                        del trends_push[push_count]
                    elif len(trends_push[push_count].find_all("a")) > 0:
                        del trends_push[push_count]
                    else:
                        push_count += 1

                # 文章內容移除作者、標題、時間
                for k in range(0, len(trends_info_1)):
                    trends_info_1[k].extract()

                # 文章內容移除看板
                for k in range(0, len(trends_info_2)):
                    trends_info_2[k].extract()

                # 文章內容移除系統自帶資訊，另外保留引述那句話
                for k in range(0, len(trends_info_3)):
                    if trends_info_3[k].text.find("※ 引述《") == 0:
                        trends_info_3[k].extract()
                        trends_quote_title = trends_info_3[k].text
                    elif trends_info_3[k].text.find("※ ") == 0:
                        trends_info_3[k].extract()

                # 文章內容移除引述
                for k in range(0, len(trends_quote)):
                    if trends_quote[k].text.find(": ") == 0:
                        trends_quote[k].extract()

                # 文章內容
                trends_content_text = trends_content.text.strip()

                # 文章簽名檔
                if trends_content_text.find("--") > -1:
                    bar_index = trends_content_text.index("--")
                    trends_poster_signature = trends_content_text[bar_index:bar_index + 2].strip()
                else:
                    trends_poster_signature = ""

                # 文章作者回復推文內容
                if trends_content_text.find("--") > -1:
                    trends_poster_reply = trends_content_text[trends_content_text.rindex("--"):].strip()
                else:
                    trends_poster_reply = ""

                # 文章內容移除簽名檔、推文內容
                trends_content_text = trends_content_text.strip() \
                    .replace(trends_poster_signature, "") \
                    .replace(trends_poster_reply, "") \
                    .replace("＊轉錄新聞/情報，必須附上原文及網址連結及心得或意見30字(不含標點符號)＊", "")

                # 文章內容多移除一個連結文字
                trends_link = trends_content.find_all("a")
                for k in range(0, len(trends_link)):
                    trends_link[k].extract()
                trends_content_no_link = trends_content.text.strip().replace(trends_poster_signature, "") \
                    .replace(trends_poster_reply, "")

                # 開始寫入檔案
                post_count += 1
                print_to_file(full_data, "文章：" + "\n" + trends_content_text)
                post_file_name = "Post_" + str(post_count) + "_Content"
                post_path_name = each_post_file_name.replace("Post_index", post_file_name)
                print_to_file(post_path_name, trends_content_no_link.strip().replace("\n", "") + trends_title.strip())

                if trends_poster_signature != "--":
                    print_to_file(full_data, "簽名檔：" + "\n" + trends_poster_signature)

                if trends_poster_reply != "--":
                    print_to_file(full_data, "作者回復推文：" + "\n" + trends_poster_reply)

                # 取得引述的標題
                if len(trends_quote) > 0:
                    print_to_file(full_data, trends_quote_title.strip())

                # 取得引述的內容
                for k in range(0, len(trends_quote)):
                    if trends_quote[k].text.find(": ") == 0:
                        print_to_file(full_data, trends_quote[k].text.strip())

                # 這裡取得推文內容，功能是把相同id的同一句話，寫在一起，因為PTT有限制推文字數
                push_count = 0
                while push_count < len(trends_push):

                    push_type = trends_push[push_count].find("span", class_="push-tag").text
                    push_userid = trends_push[push_count].find("span", class_="push-userid").text
                    push_content = trends_push[push_count].find("span", class_="push-content").text.replace(": ", "")
                    total_push_content = push_content

                    # 當此流言不是最後一個留言、下一個留言的ID和這個留言ID是一樣的，留言內容暫存，值到下一個ID和這個ID布一樣才寫入檔案
                    while ((push_count + 1) < len(trends_push)) & \
                            ((trends_push[push_count + 1].find("span", class_="push-userid").text if
                            (push_count + 1) < len(trends_push) else "") == push_userid):
                        push_count += 1
                        push_content = trends_push[push_count].find("span", class_="push-content").text \
                            .replace(": ", "")
                        total_push_content += push_content

                    push_count += 1
                    print_to_file(full_data, push_type + " " + push_userid + "：" + total_push_content)
                    print_to_file(post_path_name.replace("Content", "Reply"), total_push_content.strip().replace("\n", ""))

        print_to_file(full_data, "-")
        usage_sec = int((datetime.now() - datetime.strptime(execute_time, "%Y_%m_%d_%H_%M_%S")).total_seconds())

    print_to_file(full_data, "爬蟲結束 總耗用時間: " + str(usage_sec) + "秒")

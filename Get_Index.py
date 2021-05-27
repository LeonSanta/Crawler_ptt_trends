from selenium import webdriver
from datetime import datetime
import time


def main(board_array_string, start_date, end_date):
    # 接收傳來的版名稱、起始日期、結束日期
    board_array = board_array_string.split(",")
    start_index_array_string = ""
    end_index_array_string = ""
    start_datetime = datetime.strptime(start_date, "%Y/%m/%d")
    end_datetime = datetime.strptime(end_date, "%Y/%m/%d")
    now_datetime = datetime.today()
    driver = webdriver.Firefox()

    # 開始取得每個版的index值
    for i in range(0, len(board_array)):
        driver.get("https://www.ptt.cc/bbs/" + board_array[i] + "/index.html")
        if board_array[i].upper() == "GOSSIPING":
            driver.find_element_by_class_name("over18-button-container").find_element_by_class_name("btn-big").click()
        element = driver.find_element_by_id("action-bar-container").find_element_by_class_name("btn-group-paging") \
            .find_element_by_link_text("‹ 上頁").get_property("href")
        board_latest_index = int(element[element.rindex("index") + 5:element.rindex(".")]) + 1
        board_start_date_index = board_latest_index
        board_end_date_index = board_latest_index
        is_beyond = False
        trends_month = 0

        # 找到起始日期的index
        while True:
            # 找到此index的所有文章日期
            driver.get("https://www.ptt.cc/bbs/" + board_array[i] + "/index" + str(board_start_date_index) + ".html")
            date_array = driver.find_elements_by_class_name("date")

            # 發現至頂文章會影響計算，判斷第一頁的前五個文章不計入index計算，設定最新文章的年份是今年
            if (board_start_date_index == board_latest_index) & (len(date_array) >= 5):
                del date_array[len(date_array) - 5]
                del date_array[len(date_array) - 4]
                del date_array[len(date_array) - 3]
                del date_array[len(date_array) - 2]
                del date_array[len(date_array) - 1]
                trends_year = str(now_datetime.year)
            elif (board_start_date_index == board_latest_index) & (len(date_array)) == 4:
                del date_array[len(date_array) - 4]
                del date_array[len(date_array) - 3]
                del date_array[len(date_array) - 2]
                del date_array[len(date_array) - 1]
                trends_year = str(now_datetime.year)
            elif (board_start_date_index == board_latest_index) & (len(date_array)) == 3:
                del date_array[len(date_array) - 3]
                del date_array[len(date_array) - 2]
                del date_array[len(date_array) - 1]
                trends_year = str(now_datetime.year)
            elif (board_start_date_index == board_latest_index) & (len(date_array)) == 2:
                del date_array[len(date_array) - 2]
                del date_array[len(date_array) - 1]
                trends_year = str(now_datetime.year)
            elif (board_start_date_index == board_latest_index) & (len(date_array)) == 1:
                del date_array[len(date_array) - 1]
                trends_year = str(now_datetime.year)

            # 爬每個文章日期後，比對開始和結束日期、定義
            for j in range(0, len(date_array)):

                # 且上一次執行的文章月份，和這一次文章的月份，相減小於0，把年份-1，因為進入各版文章列表所顯示的日期，只有月和日沒有年份
                # trends_month != 0 的用意是reset每個版計算方式
                if (trends_month - datetime.strptime(date_array[j].text, "%m/%d").month < 0) & (trends_month != 0):
                    trends_year = str(int(trends_year) - 1)

                # 將文章時間加讓年份，並且計算這篇文章和啟示日期的差距
                trends_datetime = datetime.strptime(trends_year + "/" + date_array[j].text, "%Y/%m/%d")
                trends_month = trends_datetime.month
                datetime_gap = start_datetime - trends_datetime

                # 取得結束日期的index
                if int((end_datetime - trends_datetime).days) < 0:
                    board_end_date_index = board_start_date_index

                # 判斷如果這個文章的日期已經超過起始日期，則is_beyond設定為真並調離for迴圈
                if int((start_datetime - trends_datetime).days) > 0:
                    is_beyond = True
                    break
                else:
                    is_beyond = False

            # 透過is_beyond判斷，如果這一index已經超過起始日期，就離跳離while，並且整理起始和結束日期Index
            if is_beyond:
                start_index_array_string += str(board_start_date_index) + ","
                end_index_array_string += str(board_end_date_index) + ","
                break

            # 如果還沒超過，使用差距日期判斷要一次翻幾頁，這一段很重要，寫法會影響效率
            else:
                if len(date_array) == 0:
                    board_start_date_index = board_start_date_index - 1
                elif int(datetime_gap.days) > -1:
                    board_start_date_index = board_start_date_index - 1
                elif int(datetime_gap.days) > -2:
                    board_start_date_index = board_start_date_index - 2
                elif int(datetime_gap.days) > -3:
                    board_start_date_index = board_start_date_index - 3
                elif int(datetime_gap.days) > -10:
                    board_start_date_index = board_start_date_index - 5
                else:
                    # print(int(datetime_gap.days/1.5))
                    board_start_date_index = board_start_date_index + int(datetime_gap.days / 1.5)

    # 關閉動態網頁
    driver.close()
    # 全部都找到後，開始找內容
    start_index_array_string = start_index_array_string[:-1]
    end_index_array_string = end_index_array_string[:-1]
    print("Get Index Success")
    # print(start_index_array_string)
    # print(end_index_array_string)
    # print(board_array_string)

    return start_index_array_string, end_index_array_string

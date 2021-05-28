# Crawler_ptt_trends

This is a crawler which can go through select ptt board(multi-selection) in selected time interval.
Save these Post content and reply to file

After setting jieba cut idf weight and dictionary (multi-selection).
Crawler_ptt_trends can using these file to do the function below ：
  1. Calculate top n trends key word of these ptt board in selected time interval.
  2. Get each post content's keyword.
  3. Predict reply emotion of each post content keyword.

By execute this program it'll generate a file folder which contain the file below:
  1. All Post Content file.
  2. All Reply Content file.
  3. All Post Content Keyword and Reply emotion predict.
  4. Top N Trends by each jieba dictionary

It could be using by social media markecting company, to demonstract to customer or making marketind dicision.

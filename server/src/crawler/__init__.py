import csv
import re
import requests
import bs4 as BeautifulSoup
headers = {"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36 Edg/118.0.2088.76"}
r = requests.get("https://book.douban.com/tag/?view=type&icn=index-sorttags-all",headers=headers)
soup = BeautifulSoup.BeautifulSoup(r.text,'lxml')
# 获取所有 <a> 标签
all_a_tags = soup.find_all('a')

# 提取所有 <a> 标签的 href 属性以'\tag'开头的链接
hrefs = [tag.get('href') for tag in all_a_tags if tag.get('href') and tag.get('href').startswith('/tag')] # /tag/小说
htmls = ["https://book.douban.com" + href  for href in hrefs] # https://book.douban.com/tag/小说

# 提取书码
ids = []
tags = []

for html in htmls:
    r = requests.get(html,headers=headers)
    soup = BeautifulSoup.BeautifulSoup(r.text, 'lxml')
    # 获取所有 <a> 标签
    all_a_tags = soup.find_all('a')
    # 提取所有id
    last_segment = html.rsplit('/', 1)[-1]
    for tag in all_a_tags:
        if(tag.get('href') and tag.get('href').startswith('https://book.douban.com/subject/')):
            href = tag.get('href')
            match = re.search(r'/(\d+)/$', href)
            if match:
                extracted_number = match.group(1)
                if(len(ids) ==0):
                    tags.append(last_segment)
                    ids.append(extracted_number)
                elif(not extracted_number==ids[-1]):
                    ids.append(extracted_number)
                    tags.append(last_segment)

# 指定要保存的 CSV 文件名
csv_filename = 'data.csv'

# 合并ID和标签
data = list(zip(ids, tags))

# 将数据写入 CSV 文件
with open(csv_filename, 'a', newline='', encoding='utf-8') as csvfile:
    csv_writer = csv.writer(csvfile)
    # 写入标题行（可选）
    csv_writer.writerow(['编号', '标签'])
    # 写入数据
    csv_writer.writerows(data)

print(f"数据已成功保存到 {csv_filename} 文件中。")

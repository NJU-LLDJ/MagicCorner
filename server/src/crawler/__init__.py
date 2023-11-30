# curl --location --request GET 'https://frodo.douban.com/api/v2/book/rank_list?apiKey=0ac44ae016490db2204ce0a042db2916'
# --header 'User-Agent: MicroMessenger/'
# --header 'Referer: https://servicewechat.com/wx2f9b06c1de1ccfca/91/page-frame.html'
# --data-raw ''


import requests

url = "https://frodo.douban.com/api/v2/book/36104107?apiKey=0ac44ae016490db2204ce0a042db2916"

payload = {}
headers = {
    "Cache-Control": "no-cache",
    "Accept": "*/*",
    "Accept-Encoding": "gzip, deflate",
    "Connection": "keep-alive",
    "User-Agent": "MicroMessenger/",
    "Referer": "https://servicewechat.com/wx2f9b06c1de1ccfca/91/page-frame.html",
}

response = requests.request("GET", url, headers=headers, data=payload)

print(response.text)

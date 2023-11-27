url = 'https://book.douban.com/tag/小说'

# 使用字符串分割获取最后一个字段
last_segment = url.rsplit('/', 1)[-1]

print("最后一个字段是:", last_segment)
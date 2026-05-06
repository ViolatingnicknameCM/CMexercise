import requests
from bs4 import BeautifulSoup
import time
import re

# 例子：https://curlconverter.com/python/
# https://www.sme-gov.cn/shandong-news-69941.html
# 公开数据网站，F12找到69941.html后复制curl格式填入上述网址，将网址输出内容替换下方语句即可。

cookies = {}

headers = {}

response = requests.get('', cookies=cookies, headers=headers)

with open('news_page.html', 'w', encoding='utf-8') as f:
    f.write(response.text)
print('完整HTML已保存为 news_page.html')


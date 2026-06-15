# 导入需要的库（新增pymysql连接MySQL）
import pandas as pd
import jieba
import pymysql  # 旧的连接数据库,不用了
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from sqlalchemy import create_engine #消除pandas警告

#注：以后用 pandas 读数据库时，直接用 SQLAlchemy 引擎连接

from dotenv import load_dotenv
import os

load_dotenv()

# 1. B站视频BV号
TARGET_BV = "BV1TC1jYmEve"
# 2. MySQL密码
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD")

# 1. 从 MySQL 读取指定BV号的评论数据
# 连接数据库
'''旧的
conn = pymysql.connect(
    host="localhost",
    port=3306,
    user=os.getenv("MYSQL_USER"),
    password=MYSQL_PASSWORD,
    database="bilibili",
    charset="utf8mb4"
)
'''
#新的
engine = create_engine(
    f"mysql+pymysql://root:{MYSQL_PASSWORD}@localhost:3306/bilibili?charset=utf8mb4"
)
# 查询指定BV号的所有评论
sql = f"SELECT content FROM comments WHERE bv = '{TARGET_BV}'"
df = pd.read_sql(sql, engine)  # 直接读SQL结果→DataFrame,将conn改为engine
# conn.close()  关闭连接，不必要的

# 3. 用jieba把句子切成词语
words = jieba.lcut(text)
stopwords = {"的", "了", "在", "是", "我", "有", "和", "就", "不", "人", "都", "一",
             "一个", "上", "也", "很", "到", "说", "要", "去", "你", "会", "着",
             "没有", "看", "好", "自己", "这", "他", "她", "它", "们", "那", "些",
             "什么", "怎么", "如何", "为什么", "因为", "所以", "但是", "可以",
             "这个", "那个", "还是", "只是", "已经", "还有", "觉得", "真的",
             "有点", "太", "吧", "吗", "呢", "啊", "哦", "嗯", "哈", "哇"}
word_text = " ".join(words)

# 过滤停用词 + 只保留长度≥2的词
filtered_words = [w for w in words if w not in stopwords and len(w.strip()) >= 2]
word_text = " ".join(filtered_words)

# 4. 生成词云热力图
wc = WordCloud(
    font_path="C:/Windows/Fonts/simhei.ttf",
    background_color="white",
    width=1200,
    height=800,
    max_words=200
).generate(word_text)

# 5. 保存+显示
wc.to_file(f"{TARGET_BV}_评论词云.png")  # 用BV号命名文件
print(f"视频{TARGET_BV} 词云已保存")

plt.imshow(wc)
plt.axis("off")
plt.show()

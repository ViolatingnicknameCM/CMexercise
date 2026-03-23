# 导入需要的库
import pandas as pd
import jieba
from wordcloud import WordCloud
import matplotlib.pyplot as plt

# 1. 读取爬虫生成的评论csv文件
df = pd.read_csv("评论.csv")
# 把所有评论合并成一段文本
text = " ".join(df["评论"].astype(str))

# 2. 用jieba把句子切成词语
words = jieba.lcut(text)
word_text = " ".join(words)

# 3. 生成词云热力图
wc = WordCloud(
    font_path="C:/Windows/Fonts/simhei.ttf",  # Windows系统黑体
    background_color="white",  # 白色背景
    width=1200,
    height=800,
    max_words=200  # 限制高频词数量
).generate(word_text)

# 4. 保存词云图片
wc.to_file("B站评论热力图.png")
print("已保存为B站评论热力图.png")

# 5. 显示图片（可选）
plt.imshow(wc)
plt.axis("off")
plt.show()
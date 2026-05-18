# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter


# pipelines.py
import pymysql

# 2026-5-18新增：导入 dotenv 和 os 库
from dotenv import load_dotenv
import os

# 2026-5-18新增：加载 .env 文件中的环境变量
load_dotenv()

class BilibiliMysqlPipeline:
    # 爬虫启动时：连接 MySQL
    def open_spider(self, spider):
        self.conn = pymysql.connect(
            host=host='localhost',       # 本地MySQL
            port=3306,                   # 默认端口
            user=os.getenv("MYSQL_USER"),            # MySQL用户名
            password=os.getenv("MYSQL_PASSWORD"),    # 密码
            database='bilibili',    # 创建的数据库
            charset='utf8mb4'       # 支持表情/中文
        )
        # 创建游标（操作数据库）
        self.cursor = self.conn.cursor()

    # 每一条评论都会从这里存入MySQL
    def process_item(self, item, spider):
        # 过滤空评论
        comment = item.get("评论", "").strip()
        bv = item.get("bv", "").strip()

        if not comment or not bv:
            return item

        # SQL插入语句
        sql = "INSERT INTO comments (bv,content) VALUES (%s,%s)"
        try:
            # 执行插入
            self.cursor.execute(sql, (bv,comment))
            self.conn.commit()
            spider.logger.info(f"已存入MySQL,视频{bv}：{comment}")
        except Exception as e:
            self.conn.rollback()
            spider.logger.error(f"存储失败：{e}")

        return item

    # 爬虫关闭
    def close_spider(self, spider):
        self.cursor.close()
        self.conn.close()

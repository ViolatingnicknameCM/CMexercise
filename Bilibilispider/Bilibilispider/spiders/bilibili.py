import scrapy
import json #B站接口返回JSON格式


class BilibiliSpider(scrapy.Spider):
    name = "bilibili"
    allowed_domains = ["bilibili.com"]
    videoBVID = 'BV1TC1jYmEve'
    # Cookie
    SESSDATA = ''

    def start_requests(self):
        api_url = f"https://api.bilibili.com/x/web-interface/view?bvid={self.videoBVID}"
        yield scrapy.Request(
            url=api_url,
            headers=self.get_headers(),
            callback=self.get_oid_parse
        )

    # 封装请求头
    def get_headers(self):
        return {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",#伪装为浏览器
            "Referer": "https://www.bilibili.com/",#来源页，不同网页填写不同
            "Cookie": f"SESSDATA={self.SESSDATA}"#登录凭证
        }

    # 获取OID（B站自定的视频唯一编号名
    def get_oid_parse(self, response):
        data = json.loads(response.text)
        oid = data['data']['aid']
        # 从第0页开始爬，把请求提交给Scrapy调度
        yield from self.start_crawl(oid, 0)

    # 爬取评论
    def start_crawl(self, oid, page):
        #mode=2是20条评论，观察发现是按照最新排序的前20条；mode=3才能爬到所有的评论
        comment_url = f"https://api.bilibili.com/x/v2/reply/main?next={page}&type=1&oid={oid}&mode=3"
        yield scrapy.Request(
            url=comment_url,
            headers=self.get_headers(),
            callback=self.parse_comment,   #解析评论
            meta={"oid": oid, "page": page},#跨函数传参
            dont_filter=True#关闭去重（Scrapy默认去重）
        )

    # 解析评论
    def parse_comment(self, response):
        data = json.loads(response.text)
        oid = response.meta["oid"]
        page = response.meta["page"]
        bv = self.videoBVID

        # 提取评论
        if "replies" in data.get("data", {}):#防止报错
            for reply in data["data"]["replies"]:
                comment = reply["content"]["message"]
                self.logger.info(f"评论：{comment}")
                yield {"评论": comment,
                    'bv': bv
                }

        # 自动翻页
        try:
            if not data["data"]["cursor"]["is_end"]:#b站结束标志
                yield from self.start_crawl(oid, page + 1)
        except:
            return
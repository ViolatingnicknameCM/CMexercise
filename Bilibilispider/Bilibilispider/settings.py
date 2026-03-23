# Scrapy settings for Bilibilispider project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://docs.scrapy.org/en/latest/topics/settings.html
#     https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://docs.scrapy.org/en/latest/topics/spider-middleware.html

# Scrapy 基础配置
BOT_NAME = 'Bilibilispider'
SPIDER_MODULES = [BOT_NAME + '.spiders']
NEWSPIDER_MODULE = [BOT_NAME + '.spiders']

ADDONS = {}


# Crawl responsibly by identifying yourself (and your website) on the user-agent
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36'

# Obey robots.txt rules
ROBOTSTXT_OBEY = False

# Concurrency and throttling settings
#同时发送有多少个请求  延迟是多少。
CONCURRENT_REQUESTS = 1
CONCURRENT_REQUESTS_PER_DOMAIN = 1
DOWNLOAD_DELAY = 1

# Disable cookies (enabled by default)
#COOKIES_ENABLED = False

# Disable Telnet Console (enabled by default)
#TELNETCONSOLE_ENABLED = False

# Override the default request headers:
#DEFAULT_REQUEST_HEADERS = {
#    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
#    "Accept-Language": "en",
#}
# DEFAULT_REQUEST_HEADERS = {
#     'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36',
#     'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
#     'Accept-Language': 'zh-CN,zh;q=0.9',
#     'Referer': 'https://www.bilibili.com/'
# }

# Enable or disable spider middlewares
# See https://docs.scrapy.org/en/latest/topics/spider-middleware.html
#SPIDER_MIDDLEWARES = {
#    "Bilibilispider.middlewares.BilibilispiderSpiderMiddleware": 543,
#}

# Enable or disable downloader middlewares
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#DOWNLOADER_MIDDLEWARES = {
#    "Bilibilispider.middlewares.BilibilispiderDownloaderMiddleware": 543,
#}

# Enable or disable extensions
# See https://docs.scrapy.org/en/latest/topics/extensions.html
#EXTENSIONS = {
#    "scrapy.extensions.telnet.TelnetConsole": None,
#}

# Configure item pipelines
# See https://docs.scrapy.org/en/latest/topics/item-pipeline.html
#注意名称对应
ITEM_PIPELINES = {
    "Bilibilispider.pipelines.BilibiliMysqlPipeline": 300,
}

# Enable and configure the AutoThrottle extension (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/autothrottle.html
#AUTOTHROTTLE_ENABLED = True
# The initial download delay
#AUTOTHROTTLE_START_DELAY = 5
# The maximum download delay to be set in case of high latencies
#AUTOTHROTTLE_MAX_DELAY = 60
# The average number of requests Scrapy should be sending in parallel to
# each remote server
#AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
# Enable showing throttling stats for every response received:
#AUTOTHROTTLE_DEBUG = False

# Enable and configure HTTP caching (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
#HTTPCACHE_ENABLED = True
#HTTPCACHE_EXPIRATION_SECS = 0
#HTTPCACHE_DIR = "httpcache"
#HTTPCACHE_IGNORE_HTTP_CODES = []
#HTTPCACHE_STORAGE = "scrapy.extensions.httpcache.FilesystemCacheStorage"

# Set settings whose default value is deprecated to a future-proof value
FEED_EXPORT_ENCODING = "utf-8"

#关闭冗余日志，方便查看输出
LOG_LEVEL = 'INFO'

# 配置CSV输出路径（保存到最外层根目录）
import os
# 获取当前settings文件的路径后往上跳一级到最外层根目录
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# 定义CSV保存路径：最外层根目录/评论.csv
FEED_EXPORT_FIELDS = ["评论", "bv"]  # 要导出的字段，需要和爬虫yield字段一致
FEEDS = {
    os.path.join(BASE_DIR, "评论.csv"): {  #指定到外层根目录
        "format": "csv",
        "encoding": "utf-8",
        "overwrite": True,  # 覆盖原有文件（避免重复）
    },
}

# ===================== Playwright （START） =====================
# 启用 playwright 下载器
DOWNLOAD_HANDLERS = {
    "http": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
    "https": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
}

# 浏览器配置（调试用显示窗口，正式爬取改为 True）
PLAYWRIGHT_LAUNCH_OPTIONS = {
    "headless": False, #False=显示浏览器（调试用），True=无界面（正式爬取）
    'slow_mo':1000 # 延迟1秒，模拟真人
}
# ===================== Playwright （END） =====================

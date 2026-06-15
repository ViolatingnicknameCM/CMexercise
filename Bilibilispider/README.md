# B 站视频 & 评论爬虫 (学习版)
基于 Scrapy + Playwright 开发的 B 站数据爬虫，支持动态页面渲染、API 接口抓取、自动翻页，用于 Python 爬虫技术学习与实践。

## 技术栈
- 语言：Python 3.13+
- 爬虫框架：Scrapy
- 动态渲染：Playwright
- 数据解析：XPath、JSON
- 数据存储：控制台输出 / 本地文件 / MySQL

## 功能特性
### 支持双模式抓取
- 1.静态 API 抓取：B 站评论、视频数据接口
- 2.动态页面渲染：支持 JS 渲染页面
### 自动翻页爬取，支持批量数据采集
### 请求头伪装、反爬规避
### 数据清洗与结构化输出

## 项目结构
- Bilibili-spider/
- ├── spiders/           # 爬虫核心文件
- │   ├── __init__.py
- │   └── bilibili.py  # 主爬虫代码
- ├── __init__.py
- ├── items.py           # 数据结构定义
- ├── middlewares.py     # 中间件配置
- ├── pipelines.py       # 管道配置
- ├── settings.py        # 项目配置
- ├── README.md          # 项目说明
- ├── 评论热力图sql.py     # 从SQL中导出数据来构建热力图
- ├── 评论词热力图(csv).py # 从csv取出数据来构建热力图

### 结构说明

#### spiders/bilibili.py
爬虫文件，由于b站评论可以直接通过查找接口后直接调出，所以并未启用playwright，如需启用需在爬虫文件的def start_requests(self)下添加`meta={"playwright": True}`。

#### items.py :
本爬虫未修改该文件，为Scrapy原生代码

#### middlewares.py 
本爬虫未修改该文件，选择在爬虫本体添加process_request与process_response，目的是为了在同一目录下编写复数爬虫时不被全局设置干扰，尽管爬虫内代码有更高的优先级。

#### pipelines.py
- 由于在学习爬虫的同时进行了SQL学习，所以修改了管道让其把数据输入至本机的MySQL中，如果不想存到MySQL中而是存为csv之类的格式请去cmd终端内输入`"scrapy crawl bilibili -o 评论.csv"`这样的Scrapy内置导出指令，JSON/XML都可以通过这种方式导出。
- 相应的，这条命令会同时运行pipelines，如果不想将数据插入SQL应去pipelines自行注释掉（短期）或者进入cmd终端中切换到爬虫所在目录后先配置环境，即输入`pip install scrapy scrapy-playwright`和`playwright install chromium`后，再输入`"自己的python环境" -m scrapy crawl bilibili -o comments.csv --set FEED_EXPORT_ENCODING=utf-8 --set ITEM_PIPELINES={}`运行爬虫。

![SQL效果](https://github.com/ViolatingnicknameCM/CMexercise/blob/main/Bilibilispider/images/MySQL.png)

除此之外，如果希望爬虫在运行时可以正确存到MySQL中，请在SQL终端内输入如下指令：
##### SQL指令
-- 创建数据库
- `CREATE DATABASE IF NOT EXISTS bilibili DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;`

-- 使用数据库
- `USE bilibili;`

-- 3. 创建评论表（自带BV号字段，从根源区分视频）
- CREATE TABLE IF NOT EXISTS comments ( 

id INT PRIMARY KEY AUTO_INCREMENT,  -- 自增ID

bv VARCHAR(50) NOT NULL,            -- 视频BV号（区分不同视频）

content TEXT NOT NULL,              -- 评论文本

created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP  -- 存储时间

) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

`USE bilibili;`

-- 删除重复的评论
- `DELETE t1 FROM comments t1, comments t2 `
- `WHERE t1.content = t2.content AND t1.bv = t2.bv AND t1.id > t2.id;`

再前往pipelines输入自己的账号与密码，也可自行修改数据库名称、储存逻辑等。

#### settings.py
与Scrapy自动生成的代码不同的是在结尾开启了playwright，并修改了csv保存位置、请求头、同时爬取的数量、爬取时间间隔等

#### 评论热力图sql.py
这里为了方便直接使用中文名称，在pipelines与sql中配置好环境后直接运行即可生成词云热力图

#### 评论词热力图(csv).py
和评论热力图sql.py使用方法相同，不同的地方是需要自行存为csv后才能使用

## 环境准备
1.安装依赖
- `pip install scrapy playwright`
- `playwright install chromium`
- `pip install pymysql`
- `pip install pandas`
- `pip install jieba`
- `pip install matplotlib`
- `pip install wordcloud`

## 运行方式
- 1.修改爬虫文件中的目标视频 URL/ID 以及找到自己账号的 SESSDATA，需要使用SQL的自行修改账号与密码，不需要则进入pipelines中注释掉即可
- 2.执行启动命令
- ①`scrapy crawl bilibili`，会插入至sql中，后续请使用评论热力图sql.py
- ②注释掉pipelines后输入`scrapy crawl bilibili -o 评论.csv`会生成csv格式，后续请使用评论词热力图(csv).py

## 运行结果：
![B站爬虫运行效果](https://github.com/ViolatingnicknameCM/ViolatingnicknameCMexercise/blob/87691ce4dcc7a4353f6a3e9aed4a7bba4098fc17/Bilibilispider/images/bilibili_run.png)

![词云运行效果](https://github.com/ViolatingnicknameCM/CMexercise/blob/main/Bilibilispider/images/WordCloud.png)

## 注意事项
1.本项目仅用于个人学习和技术研究
2.严格遵守 B 站 robots.txt 协议及用户协议
3.请勿用于商业用途、恶意爬取、数据滥用
4.爬取时控制频率，避免对目标服务器造成压力

## 免责声明
本项目仅为 Python 爬虫学习案例，所有爬取的数据版权归原平台所有。使用者因违规使用导致的任何法律责任，与开发者无关。

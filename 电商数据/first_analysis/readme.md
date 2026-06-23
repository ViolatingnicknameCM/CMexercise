\# 销售分析 — Olist 巴西电商数据集



&#x20;## 一、数据验证结果



&#x20;- 订单时间跨度：2016-09-04 \~ 2018-10-17（约25个月）

&#x20;- 有效订单（delivered）：96,478 笔

&#x20;- 订单明细：112,650 行

&#x20;- 品类数：73 个（71 个有英文翻译）



\## 二、技术栈



Python：pandas、matplotlib



\## 三、简要分析步骤



\### 1.数据加载与清洗



&#x20;- 读入4个CSV：orders, order\_items, products, category\_translation

&#x20;- 过滤 order\_status == 'delivered'

&#x20;- 合并：orders + items + products + translation

&#x20;- 提取 order\_month、order\_quarter 字段

&#x20;- 计算每笔订单的 GMV = price + freight\_value（或仅 price，可修改）



\### 2. 分析1：整体销售额趋势（按周/月）



&#x20;- df.groupby('order\_month')\['gmv'].sum() → 折线图



\### 3. 分析2：月度/季度 GMV



&#x20;- 月度：按月汇总 GMV 和订单量 → 柱状图+折线图

&#x20;- 季度：按月汇总基础上聚合为季度



\### 4.分析3：客单价（AOV）



&#x20;- 每笔订单 GMV = 该订单所有 item 的 price+freight 之和

&#x20;- orders.groupby('order\_id')\['gmv'].sum().mean() → 整体客单价

&#x20;- 按月 orders.groupby('month')\['gmv'].mean() → 客单价趋势



\### 5.各类目销售额排名



&#x20;- 选用条形图



\### 6.python终端中出图



\## 四、分析结果



\### 1.指标



&#x20;- GMV：约1,542万巴西雷亚尔币，汇率换算约等于2150万人民币



&#x20;- AOV：约224元人民币



&#x20;- 订单均商品数：1.1件



charts 编号1-3



&#x20;- top5品类|中文名称|GMV|占比



health\_beauty|健康美容|141万巴西雷亚尔币|9.2%

watches\_gifts|手表礼品|126万巴西雷亚尔币|8.2%

bed\_bath\_table|床品卫浴 |123万巴西雷亚尔币|7.9%

sports\_leisure|运动休闲|112万巴西雷亚尔币|7.3%

computers\_accessories|电脑配件|103万巴西雷亚尔币|6.7%



\### 2.总结



&#x20;- 月度GMV2017年稳步增长，2017Q3-2018Q2 是峰值期



&#x20;- 季度GMV最高249万巴西雷亚尔币



&#x20;- 客单价均值160巴西雷亚尔币，中位数波动小，整体稳定



&#x20;- 品类排名Top10贡献62%，头部集中度高



\## 数据来源



\-From Olist --Kaggle



\-https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce


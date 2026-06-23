# 销售分析 — Olist 巴西电商数据集



## 一、数据验证

- 订单时间跨度：2016-09-04 ~ 2018-10-17（约25个月）

- 有效订单（delivered）：96,478 笔

- 订单明细：112,650 行

- 品类数：73 个（71 个有英文翻译）



## 二、技术栈



Python：pandas、matplotlib

### 代码结构：

- 定义路径
- 定义函数load_data()        → 数据加载+清洗，返回一个干净的 df
- 定义函数print_summary()    → 输出汇总指标
- 定义函数plot_sales_trend() → 图1月度销售额趋势
- 定义函数plot_quarterly_gmv() → 图2季度GMV
- 定义函数plot_aov_trend()   → 图3客单价趋势
- 定义函数plot_category_ranking() → 图4品类销售额排名
- main()             → 按顺序调度

- 学习使用if __name__ == '__main__'，保证不自动执行

- 学习将每个分析独立成对应的函数，保证各模块代码可单独分块调试、不依赖全局变量，减少扩充难度

- 文件路径取自环境变量，而环境变量绑定了当前Python脚本文件的路径+dataset文件夹，由于版权相关故未提交到github中，需要自行在kaggle中下载（数据来源在最底部）

## 三、简要分析步骤



### 1.数据加载与清洗



- 读入4个CSV：orders, order_items, products, category_translation（数据来源位于结尾处）

- 过滤 order_status == 'delivered'

- 合并：orders + items + products + translation

- 提取 order_month、order_quarter 字段

- 计算每笔订单的 GMV = price + freight_value（或仅 price，可修改）



### 2. 分析1：整体销售额趋势（按周/月）



- df.groupby('order_month')['gmv'].sum() → 折线图



### 3. 分析2：月度/季度 GMV



- 月度：按月汇总 GMV 和订单量 → 柱状图+折线图

- 季度：按月汇总基础上聚合为季度



### 4.分析3：客单价（AOV）



- 每笔订单 GMV = 该订单所有 item 的 price+freight 之和

- orders.groupby('order_id')['gmv'].sum().mean() → 整体客单价

- 按月 orders.groupby('month')['gmv'].mean() → 客单价趋势



### 5.各类目销售额排名



- 选用条形图



### 6.python终端中出图



## 四、分析结果



### 1.指标



- GMV：约1,542万巴西雷亚尔币，汇率换算约等于2150万人民币



- AOV：约224元人民币



- 订单均商品数：1.1件



charts 编号1-3



- top5品类|中文名称|GMV|占比



health_beauty|健康美容|141万巴西雷亚尔币|9.2%

watches_gifts|手表礼品|126万巴西雷亚尔币|8.2%

bed_bath_table|床品卫浴 |123万巴西雷亚尔币|7.9%

sports_leisure|运动休闲|112万巴西雷亚尔币|7.3%

computers_accessories|电脑配件|103万巴西雷亚尔币|6.7%



### 2.总结



- 月度GMV2017年稳步增长，2017Q3-2018Q2 是峰值期



- 季度GMV最高249万巴西雷亚尔币



- 客单价均值160巴西雷亚尔币，中位数波动小，整体稳定



- 品类排名Top10贡献62%，头部集中度高



## 数据来源



-From Olist --Kaggle



-https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce


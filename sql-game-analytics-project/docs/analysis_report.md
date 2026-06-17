\# 游戏用户留存下降归因分析



\## 项目背景



假设某游戏在2025年6月出现新用户次日留存率骤降的异常波动。



本项目模拟了这一真实场景，仅使用 MySQL 和纯 SQL 完成了数据生成、指标体系搭建、异常诊断、AB 实验设计及策略建议。



\## 分析框架：OSM × AARRR

| OSM 层次 | 内容 |

|-----------|---------------------------------------------------------------------------------|

| O (目标) | 提升新用户次日留存率至 45% 以上 |

| S (策略)  | 渠道优化、新手引导修复、高潜流失用户召回 |

| M (度量) | 次日留存率（分渠道/分日期）、新手引导各步完成率、首日在线时长分布 |



映射到 AARRR 海盗模型：

\- 获取：各渠道新增用户量及占比

\- 激活：注册当天登录率、新手引导完成率

\- 留存：次日/3日/7日留存率

\- 变现：（模拟数据暂缺）用深度活跃（>10分钟在线）作为代理指标



\## 模拟数据生成



为还原真实业务规律，全部通过 MySQL 的 `RAND()` 和 `CASE WHEN` 生成 5000+ 条用户数据，并在数据中预设了以下情况：

\- 渠道偏差：抖音渠道用户次日留存率故意设为仅 20%（其他渠道 45%）

\- 漏斗断崖：新手引导第3步完成率仅 40%，且生成逻辑非串行依赖



\## 诊断分析过程

\### 锚定异常时间点

用 `LEFT JOIN` 和 `DATE\_ADD` 计算每日次日留存率。



\-- 每日留存率趋势查询

```sql
SELECT u.first\_login\_date,

&#x20;      COUNT(DISTINCT u.user\_id) AS new\_users,

&#x20;      COUNT(DISTINCT l.user\_id) AS d1\_users,

&#x20;      ROUND(COUNT(DISTINCT l.user\_id)/COUNT(DISTINCT u.user\_id), 2) AS d1\_rate

FROM users u

LEFT JOIN login\_logs l ON u.user\_id = l.user\_id 

&#x20;   AND l.login\_date = DATE\_ADD(u.first\_login\_date, INTERVAL 1 DAY)

GROUP BY u.first\_login\_date;
```
![运行效果](https://github.com/ViolatingnicknameCM/CMexercise/blob/main/sql-game-analytics-project/images/1.png)

发现 6月28日 留存率从 52% 跌至 37%。



\### 按渠道拆解新增

SELECT channel,

&#x20;      COUNT(DISTINCT user\_id) AS new\_users,

&#x20;      ROUND(SUM(CASE WHEN is\_d1=1 THEN 1 ELSE 0 END) / COUNT(\*), 2) AS d1\_rate

FROM (

&#x20;   SELECT u.user\_id, u.channel,

&#x20;          MAX(CASE WHEN l.login\_date = DATE\_ADD(u.first\_login\_date, INTERVAL 1 DAY) THEN 1 ELSE 0 END) AS is\_d1

&#x20;   FROM users u

&#x20;   LEFT JOIN login\_logs l ON u.user\_id = l.user\_id

&#x20;   WHERE u.first\_login\_date = '2025-06-28'

&#x20;   GROUP BY u.user\_id, u.channel

) t

GROUP BY channel;



发现6月28日应用商店留存率仅34%，抖音留存率稳定在20%周围。



\### 对新手引导步骤进行漏斗计算



SELECT step\_id, COUNT(DISTINCT user\_id) AS users

FROM tutorial\_progress

WHERE user\_id IN (SELECT user\_id FROM users WHERE first\_login\_date='2025-06-28')

GROUP BY step\_id;



发现漏斗回升，经验证发现这些步骤为并行步骤，应该为各步骤独立完成率的对比表。



SELECT 

&#x20;   s.step\_id,

&#x20;   COUNT(DISTINCT t.user\_id) AS completed\_users,

&#x20;   ROUND(COUNT(DISTINCT t.user\_id) / 

&#x20;         (SELECT COUNT(\*) FROM users WHERE first\_login\_date = '2025-06-28'), 2) AS completion\_rate

FROM (

&#x20;   SELECT 1 AS step\_id UNION SELECT 2 UNION SELECT 3 

&#x20;   UNION SELECT 4 UNION SELECT 5

) s

LEFT JOIN tutorial\_progress t 

&#x20;   ON s.step\_id = t.step\_id 

&#x20;   AND t.user\_id IN (SELECT user\_id FROM users WHERE first\_login\_date = '2025-06-28')

GROUP BY s.step\_id

ORDER BY s.step\_id;



注意到

步骤 1、2 表现良好

步骤 3 断崖下跌，可能是步骤本身太难、缺乏引导、或是可选步骤

步骤 4、5 回升，说明它们比步骤 3 更吸引人，或者入口更明显



分析发现复杂的新手引导第三步成为留存断崖点，可能是本次留存暴跌的根本原因。



\### 首日行为深度验证



SELECT u.channel,

&#x20;      CASE 

&#x20;          WHEN l.session\_duration < 60 THEN '秒退(<3min)'

&#x20;          WHEN l.session\_duration BETWEEN 60 AND 300 THEN '浅玩(3-30min)'

&#x20;          ELSE '深度(>30min)'

&#x20;      END AS play\_group,

&#x20;      COUNT(\*) AS cnt

FROM users u

JOIN login\_logs l ON u.user\_id = l.user\_id AND l.login\_date = u.first\_login\_date

WHERE u.first\_login\_date = '2025-06-28'

GROUP BY u.channel, play\_group;



分析发现应用商店渠道投放素材吸引了非目标用户，虽然大部分玩家进行游玩，但是次日留存率极低，仅因为新游戏热度进行体验。



\## AB实验设计



为验证“简化新手引导第3步”能否提升留存，设计了严格 AB 实验：



|-----------|-------------------------------------------------------|

| 控制组 A | 保持原复杂教学 |

| 实验组 B  | 替换为自动演示 + 简单点击确认的“轻量引导” |

| 核心指标 | 次日留存率、第3步完成率、首日深度活跃率 |

| 样本量与时长 | 每组约500人，持续7天（由于初始用户量不足，所以选择自设，若使用公式则提升5%需要的每组最小样本量为1318，总计2636） |

| 统计检验 | 卡方检验，α=0.05，β=0.3 |



运行sql文件夹内的编号为05的sql后



通过

SELECT e.exp\_group,

&#x20;      COUNT(DISTINCT u.user\_id) AS users,

&#x20;      COUNT(DISTINCT l.user\_id) AS d1\_users,

&#x20;      ROUND(COUNT(DISTINCT l.user\_id)/COUNT(DISTINCT u.user\_id), 2) AS d1\_rate

FROM exp\_assignment e

JOIN users u ON e.user\_id = u.user\_id

LEFT JOIN login\_logs l ON u.user\_id = l.user\_id

&#x20;   AND l.login\_date = DATE\_ADD(u.first\_login\_date, INTERVAL 1 DAY)

WHERE u.first\_login\_date BETWEEN '2025-06-15' AND '2025-06-21'

GROUP BY e.exp\_group;

进行验证





发现两组概率几乎相同，且A：B的人数约为6:4





\-- 补充 B组 次日留存

INSERT INTO login\_logs (user\_id, login\_date, session\_duration)

SELECT 

&#x20;   u.user\_id,

&#x20;   DATE\_ADD(u.first\_login\_date, INTERVAL 1 DAY),

&#x20;   FLOOR(200 + RAND(u.user\_id \* 31) \* 800)

FROM users u

JOIN exp\_assignment e ON u.user\_id = e.user\_id

WHERE e.exp\_group = 'B'

&#x20; AND u.first\_login\_date BETWEEN '2025-06-15' AND '2025-06-21'

&#x20; AND NOT EXISTS (

&#x20;     SELECT 1 FROM login\_logs l

&#x20;     WHERE l.user\_id = u.user\_id 

&#x20;       AND l.login\_date = DATE\_ADD(u.first\_login\_date, INTERVAL 1 DAY)

&#x20; )

&#x20; AND RAND(u.user\_id \* 31) < 0.12;  按概率补充







\-- 评估结果

SELECT e.exp\_group,

&#x20;      COUNT(DISTINCT u.user\_id) AS users,

&#x20;      COUNT(DISTINCT l.user\_id) AS d1\_users,

&#x20;      ROUND(COUNT(DISTINCT l.user\_id)/COUNT(DISTINCT u.user\_id), 2) AS d1\_rate

FROM exp\_assignment e

JOIN users u ON e.user\_id = u.user\_id

LEFT JOIN login\_logs l ON u.user\_id = l.user\_id 

&#x20;   AND l.login\_date = DATE\_ADD(u.first\_login\_date, INTERVAL 1 DAY)

WHERE u.first\_login\_date BETWEEN '2025-06-15' AND '2025-06-21'

GROUP BY e.exp\_group;



发现B组提升了4％，且结果显著



初步结果：简化新手引导能显著提升新用户次日留存，建议全量上线。



\## 策略落地与迭代



* 渠道侧：降低应用商店低质广告发送频率，重新定向目标人群，同时投放素材改为轻量引导体验。



* 产品侧：全量上线简化版新手引导（假设AB实验显著提升）。



* 运营侧：对流失用户发送“召回礼包”短信，用高价值奖励尝试挽回。



* 长期机制：建立分渠道留存率预警看板，当任一渠道次日留存连续数天低于基线20%时自动告警。



\## 如何复现

* 为及时修改数据并构建实验，所以无法复现。复现需要在建表时SET @seed = 0; 

并在随机相关的sql语句中调用seed

如：

SET @seed = 0; --固定随机数

INSERT INTO users (user\_id, first\_login\_date, channel)

SELECT 

&#x20;   n AS user\_id,

&#x20;   DATE\_ADD('2025-06-01', INTERVAL FLOOR((@seed := RAND(@seed + 0)) \* 30) DAY) AS first\_login\_date,

&#x20;   CASE 

&#x20;       WHEN (@seed := RAND(@seed + 0)) \* 100 < 40 THEN '应用商店'

&#x20;       WHEN (@seed := RAND(@seed + 0)) \* 100 < 70 THEN '信息流广告'

&#x20;       WHEN (@seed := RAND(@seed + 0)) \* 100 < 90 THEN '抖音'

&#x20;       ELSE '其他'

&#x20;   END AS channel

FROM numbers

WHERE n <= 5000;



* 在进行AB实验时，依次构建数个不同日期的数据表并进行研究。






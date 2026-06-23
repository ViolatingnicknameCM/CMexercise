# 游戏用户留存下降归因分析



## 项目背景



假设某游戏在2025年6月出现新用户次日留存率骤降的异常波动。



本项目模拟了这一真实场景，仅使用 MySQL 和纯 SQL 完成了数据生成、指标体系搭建、异常诊断、AB 实验设计及策略建议。



## 分析框架：OSM × AARRR

| OSM 层次 | 内容 |

|-----------|---------------------------------------------------------------------------------|

| O (目标) | 提升新用户次日留存率至 45% 以上 |

| S (策略)  | 渠道优化、新手引导修复、高潜流失用户召回 |

| M (度量) | 次日留存率（分渠道/分日期）、新手引导各步完成率、首日在线时长分布 |



映射到 AARRR 海盗模型：

- 获取：各渠道新增用户量及占比

- 激活：注册当天登录率、新手引导完成率

- 留存：次日/3日/7日留存率

- 变现：（模拟数据暂缺）用深度活跃（在线时长）作为代理指标



## 模拟数据生成



为还原真实业务规律，全部通过 MySQL 的 `RAND()` 和 `CASE WHEN` 生成 5000+ 条用户数据，并在数据中预设了以下情况：

- 渠道偏差：抖音渠道用户次日留存率故意设为仅 20%（其他渠道 45%）

- 漏斗断崖：新手引导第3步完成率仅 40%，且生成逻辑非串行依赖

- 按顺序依次运行sql文件夹内前四个文件可获得初始数据


## 诊断分析过程

### 锚定异常时间点

用 `LEFT JOIN` 和 `DATE_ADD` 计算每日次日留存率。



-- 每日留存率趋势查询

```sql
SELECT u.first_login_date,

      COUNT(DISTINCT u.user_id) AS new_users,

      COUNT(DISTINCT l.user_id) AS d1_users,

      ROUND(COUNT(DISTINCT l.user_id)/COUNT(DISTINCT u.user_id), 2) AS d1_rate

FROM users u

LEFT JOIN login_logs l ON u.user_id = l.user_id 

   AND l.login_date = DATE_ADD(u.first_login_date, INTERVAL 1 DAY)

GROUP BY u.first_login_date;
```
![运行效果](https://github.com/ViolatingnicknameCM/CMexercise/blob/main/sql-game-analytics-project/images/1.png)

发现 6月28日 留存率从 52% 跌至 37%。



### 按渠道拆解新增

```sql
SELECT channel,

      COUNT(DISTINCT user_id) AS new_users,

      ROUND(SUM(CASE WHEN is_d1=1 THEN 1 ELSE 0 END) / COUNT(*), 2) AS d1_rate

FROM (

   SELECT u.user_id, u.channel,

          MAX(CASE WHEN l.login_date = DATE_ADD(u.first_login_date, INTERVAL 1 DAY) THEN 1 ELSE 0 END) AS is_d1

   FROM users u

   LEFT JOIN login_logs l ON u.user_id = l.user_id

   WHERE u.first_login_date = '2025-06-28'

   GROUP BY u.user_id, u.channel

) t

GROUP BY channel;
```

![运行效果](https://github.com/ViolatingnicknameCM/CMexercise/blob/main/sql-game-analytics-project/images/2.png)

发现6月28日应用商店留存率仅34%;抖音留存率稳定在20%周围，为17%


### 对新手引导步骤进行漏斗计算

```sql
SELECT step_id, COUNT(DISTINCT user_id) AS users

FROM tutorial_progress

WHERE user_id IN (SELECT user_id FROM users WHERE first_login_date='2025-06-28')

GROUP BY step_id;
```

![运行效果](https://github.com/ViolatingnicknameCM/CMexercise/blob/main/sql-game-analytics-project/images/3.png)

发现漏斗回升，注意到这些步骤为并行步骤，应该为各步骤独立完成率的对比表。


```sql
SELECT 

   s.step_id,

   COUNT(DISTINCT t.user_id) AS completed_users,

   ROUND(COUNT(DISTINCT t.user_id) / 

         (SELECT COUNT(*) FROM users WHERE first_login_date = '2025-06-28'), 2) AS completion_rate

FROM (

   SELECT 1 AS step_id UNION SELECT 2 UNION SELECT 3 

   UNION SELECT 4 UNION SELECT 5

) s

LEFT JOIN tutorial_progress t 

&#x20;   ON s.step_id = t.step_id 

&#x20;   AND t.user_id IN (SELECT user_id FROM users WHERE first_login_date = '2025-06-28')

GROUP BY s.step_id

ORDER BY s.step_id;
```

![运行效果](https://github.com/ViolatingnicknameCM/CMexercise/blob/main/sql-game-analytics-project/images/4.png)

注意到

步骤 1、2 表现良好

步骤 3 断崖下跌，可能是步骤本身太难、缺乏引导、或是可选步骤

步骤 4、5 回升，说明它们比步骤 3 更吸引人，或者入口更明显



分析发现复杂的新手引导第三步成为留存断崖点，可能是本次留存暴跌的根本原因。



### 首日行为深度验证


```sql
SELECT u.channel,

      CASE 

          WHEN l.session_duration < 60 THEN '秒退(<3min)'

          WHEN l.session_duration BETWEEN 60 AND 300 THEN '浅玩(3-30min)'

          ELSE '深度(>30min)'

      END AS play_group,

      COUNT(*) AS cnt

FROM users u

JOIN login_logs l ON u.user_id = l.user_id AND l.login_date = u.first_login_date

WHERE u.first_login_date = '2025-06-28'

GROUP BY u.channel, play_group;
```

![运行效果](https://github.com/ViolatingnicknameCM/CMexercise/blob/main/sql-game-analytics-project/images/5.png)

分析发现应用商店渠道投放素材吸引了非目标用户，虽然大部分玩家进行游玩，但是次日留存率极低，仅因为新游戏热度进行体验。

# 发现错误，没有及时修改参数导致查询区间与显示区间不一致  2026-6-23



## AB实验设计



为验证“简化新手引导第3步”能否提升留存，设计了严格 AB 实验：



|-----------|-------------------------------------------------------|

| 控制组 A | 保持原复杂教学 |

| 实验组 B  | 替换为自动演示 + 简单点击确认的“轻量引导” |

| 核心指标 | 次日留存率、第3步完成率、首日深度活跃率 |

| 样本量与时长 | 每组约500人，持续7天（由于初始用户量不足，所以选择自设，若使用公式则提升5%需要的每组最小样本量为1318，总计2636） |

| 统计检验 | 卡方检验，α=0.05，β=0.3 |



运行sql文件夹内的编号为05的sql后



通过
```sql
SELECT e.exp_group,

      COUNT(DISTINCT u.user_id) AS users,

      COUNT(DISTINCT l.user_id) AS d1_users,

      ROUND(COUNT(DISTINCT l.user_id)/COUNT(DISTINCT u.user_id), 2) AS d1_rate

FROM exp_assignment e

JOIN users u ON e.user_id = u.user_id

LEFT JOIN login_logs l ON u.user_id = l.user_id

&#x20;   AND l.login_date = DATE_ADD(u.first_login_date, INTERVAL 1 DAY)

WHERE u.first_login_date BETWEEN '2025-06-15' AND '2025-06-21'

GROUP BY e.exp_group;
```

![运行效果](https://github.com/ViolatingnicknameCM/CMexercise/blob/main/sql-game-analytics-project/images/6.png)

发现两组概率几乎相同，且A：B的人数约为6:4





-- 补充 B组 次日留存

```sql
INSERT INTO login_logs (user_id, login_date, session_duration)

SELECT 

   u.user_id,

   DATE_ADD(u.first_login_date, INTERVAL 1 DAY),

   FLOOR(200 + RAND(u.user_id * 31) * 800)

FROM users u

JOIN exp_assignment e ON u.user_id = e.user_id

WHERE e.exp_group = 'B'

 AND u.first_login_date BETWEEN '2025-06-15' AND '2025-06-21'

 AND NOT EXISTS (

     SELECT 1 FROM login_logs l

     WHERE l.user_id = u.user_id 

       AND l.login_date = DATE_ADD(u.first_login_date, INTERVAL 1 DAY)

 )

 AND RAND(u.user_id * 31) < 0.12;  按概率补充
```

-- 评估结果

```sql
SELECT e.exp_group,

      COUNT(DISTINCT u.user_id) AS users,

      COUNT(DISTINCT l.user_id) AS d1_users,

      ROUND(COUNT(DISTINCT l.user_id)/COUNT(DISTINCT u.user_id), 2) AS d1_rate

FROM exp_assignment e

JOIN users u ON e.user_id = u.user_id

LEFT JOIN login_logs l ON u.user_id = l.user_id 

   AND l.login_date = DATE_ADD(u.first_login_date, INTERVAL 1 DAY)

WHERE u.first_login_date BETWEEN '2025-06-15' AND '2025-06-21'

GROUP BY e.exp_group;
```

![运行效果](https://github.com/ViolatingnicknameCM/CMexercise/blob/main/sql-game-analytics-project/images/7.png)

发现B组提升了4％，且结果显著



初步结果：简化新手引导能显著提升新用户次日留存，建议全量上线。


## 策略落地与迭代

* 渠道侧：降低应用商店低质广告发送频率，重新定向目标人群，同时投放素材改为轻量引导体验。

* 产品侧：全量上线简化版新手引导（假设AB实验显著提升）。

* 运营侧：对流失用户发送“召回礼包”短信，用高价值奖励尝试挽回。

* 长期机制：建立分渠道留存率预警看板，当任一渠道次日留存连续数天低于基线20%时自动告警。


## 如何复现

* 为及时获取随机数据并构建实验，所以无法复现同样的初始数据，但可用相同的初始数据复现同样的结论(构建数据未确定随机数，AB实验确定随机数)。若需复现需要在建表时SET @seed = 0; 

并在所有随机相关的sql语句中调用seed

如：

SET @seed = 0; --固定随机数

```sql
INSERT INTO users (user_id, first_login_date, channel)

SELECT 

   n AS user_id,

   DATE_ADD('2025-06-01', INTERVAL FLOOR((@seed := RAND(@seed + 0)) * 30) DAY) AS first_login_date,

   CASE 

       WHEN (@seed := RAND(@seed + 0)) * 100 < 40 THEN '应用商店'

       WHEN (@seed := RAND(@seed + 0)) * 100 < 70 THEN '信息流广告'

       WHEN (@seed := RAND(@seed + 0)) * 100 < 90 THEN '抖音'

       ELSE '其他'

   END AS channel

FROM numbers

WHERE n <= 5000;
```

* 在进行AB实验时，依次构建数个不同日期的数据表并进行研究。






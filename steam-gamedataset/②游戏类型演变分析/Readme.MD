 ---
# Steam 游戏类型演变分析

> 数据集：`02_genre_evolution.csv`
> 工具：Jupyter Notebook (Python)


  **列结构：**

  | 列名 | 类型  | 说明                                 |
  |---|-----|------------------------------------|
  | `genre_name` | 字符串 | 游戏类型名称 (如 Indie, Action, Strategy) |
  | `release_year` | 小数  | 发行年份，小数为源数据集的问题                    |  
  | `game_count` | 整数  | 该类型当年游戏数量                          |
  | `avg_price` | 浮点数 | 该类型当年平均价格 (USD)，部分为空               |
  | `free_count` | 整数  | 该类型当年免费游戏数量                        |

  # 主要模块介绍

  ## 模块1：数据加载与预处理

  ### 目标
  - 读取 CSV，检查缺失值和数据类型
  - 输出数据概览（行数、列名、年份/类型覆盖范围）
  - 为后续可视化准备干净的 DataFrame

  ## 模块2：类型热力图

  - 以 genre_name 为行、release_year 为列、game_count 为颜色深度
  - 直观展示游戏类型的年度分布变化

  - 交互式图表演示,点击路径即可查看(https://violatingnicknamecm.github.io/CMexercise/blob/main/steam-gamedataset/png/bubble_animation.html)
  

  ## 模块3：动画气泡图

  - 以气泡位置/大小展示各类型每年游戏数量的动态变化

  - 气泡度演示

  ## 模块4：对独立游戏的一些分析

  - 独立游戏在哪一年爆发？
  - steam市场份额发生了什么变化？

  ### 分析指标
  
  - 同比增长率 (YoY)，公式为  (当年 - 前年) / 前年 × 100%   用于确定   增速快慢
  - 市场份额     公式为   Indie数量 / 全年总游戏数 × 100%   用于确定 占比高低

  ## 运行
  - 确认 02_genre_evolution.csv 在项目目录中
  - 确认代码中文件路径正确
  - 确认保存文件夹存在
  
  ## 数据来源

  - from VintageDon - GitHub 仅用作学习

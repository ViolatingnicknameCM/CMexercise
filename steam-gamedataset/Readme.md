# 项目结构（待更新）

- steam-gamedataset/
- ├── data storage/01-platform-evolution/  # from VintageDon - GitHub 
- │ ├── 01_temporal_growth.csv
- │ ├── 02_genre_evolution.csv
- │ ├── 03_platform_support.csv
- │ ├── 04_pricing_strategy.csv
- │ ├── 05_publisher_portfolios.csv
- │ ├── 06_achievement_evolution.csv
- │ ├── 初步分析.txt       
- │ └── 工作簿 1.twb       #tableau工作薄，对应①steam28年增长曲线
- │ 
- ├── png/                              #保存了所有需要在github内引用的图片等
- │ ├── bubble_animation.html           #②游戏类型演变分析中的气泡图
- │ ├── steam_growth.png                #①steam28年增长曲线中的折线图
- │ └── steam_heatmap_interactive.html  #②游戏类型演变分析中的热力图
- │ 
- ├── ①steam28 年增长曲线 /              #steam28年增长曲线的juypter主代码
- │ ├──Readme.MD
- │ └──Steam游戏数量增长曲线可视化.ipynb
- │ 
- ├── ②游戏类型演变分析 /                #游戏类型演变分析的juypter主代码
- │ ├──Readme.MD
- │ └──Steam游戏类型演变分析.ipynb
- │ 
- ├── Readme.txt                        
- │ 
- └── 获取 steam 数据.py                 #VintageDon 仓库的获取代码

## 具体内容

###  ① Steam 28年增长曲线可视化
  - 用 01_temporal_growth.csv 画出 Steam 从1997年2款游戏到年发行上万的全过程
  - 标注关键节点：2005年第三方开放、2012年绿光、2018年Direct等


###  ② 游戏类型演变
  - 用 02_genre_evolution.csv 做热力图或动画气泡图
  - 展示"策略游戏→独立游戏→动作游戏"的类型重心迁移
  - 分析「独立游戏」爆发于哪一年、现在是否饱和

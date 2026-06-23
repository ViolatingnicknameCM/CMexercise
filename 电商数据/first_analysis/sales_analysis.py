# -*- coding: utf-8 -*-
"""
Olist 巴西电商销售分析
分析维度：整体GMV趋势 / 月度&季度GMV / 客单价 / 品类销售额排名
"""

import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import os
import sys

# 尝试用系统自带字体，失败则回退英文
plt.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

#  路径设置
DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'dataset')
OUT_DIR = os.path.join(os.path.dirname(__file__), 'charts')
os.makedirs(OUT_DIR, exist_ok=True)


def load_data():
    """加载并清洗数据，返回合并后的DataFrame"""
    orders = pd.read_csv(os.path.join(DATA_DIR, 'olist_orders_dataset.csv'))
    items = pd.read_csv(os.path.join(DATA_DIR, 'olist_order_items_dataset.csv'))
    products = pd.read_csv(os.path.join(DATA_DIR, 'olist_products_dataset.csv'))
    translation = pd.read_csv(os.path.join(DATA_DIR, 'product_category_name_translation.csv'))

    # 只保留已交付订单
    delivered = orders[orders['order_status'] == 'delivered'].copy()
    delivered['order_purchase_timestamp'] = pd.to_datetime(delivered['order_purchase_timestamp'])
    delivered['order_month'] = delivered['order_purchase_timestamp'].dt.to_period('M')
    delivered['order_quarter'] = delivered['order_purchase_timestamp'].dt.to_period('Q')

    # 关联链：orders → items → products → translation
    df = delivered.merge(items, on='order_id', how='inner')
    df = df.merge(products[['product_id', 'product_category_name']], on='product_id', how='left')
    df = df.merge(translation, on='product_category_name', how='left')
    df['category_en'] = df['product_category_name_english'].fillna('unknown')

    # GMV = 商品价格 + 运费 (顾客实际支付)
    df['gmv'] = df['price'] + df['freight_value']

    return df


def print_summary(df):
    """终端输出汇总指标"""
    total_gmv = df['gmv'].sum()
    order_gmv = df.groupby('order_id')['gmv'].sum()
    aov = order_gmv.mean()
    total_orders = order_gmv.count()
    total_customers = df['customer_id'].nunique()
    date_min = df['order_purchase_timestamp'].min().strftime('%Y-%m-%d')
    date_max = df['order_purchase_timestamp'].max().strftime('%Y-%m-%d')

    print('=' * 60)
    print('  Olist 巴西电商销售分析')
    print('=' * 60)
    print(f'  数据范围      : {date_min} ~ {date_max}')
    print(f'  已交付订单数  : {total_orders:,}')
    print(f'  顾客数        : {total_customers:,}')
    print(f'  总 GMV        : R$ {total_gmv:,.2f}')
    print(f'  客单价 (AOV)  : R$ {aov:,.2f}')
    print(f'  订单均商品数  : {len(df) / total_orders:.1f}')
    print('=' * 60)


def plot_sales_trend(df):
    """分析1：月度销售额趋势"""
    monthly = df.groupby('order_month').agg(
        gmv=('gmv', 'sum'),
        orders=('order_id', 'nunique')
    ).reset_index()
    monthly['order_month'] = monthly['order_month'].astype(str)

    fig, ax1 = plt.subplots(figsize=(16, 6))
    ax1.fill_between(range(len(monthly)), monthly['gmv'] / 1e6, alpha=0.3, color='#2196F3')
    ax1.plot(range(len(monthly)), monthly['gmv'] / 1e6, color='#2196F3', linewidth=2, marker='o', markersize=4)
    ax1.set_ylabel('GMV (百万 BRL)', color='#2196F3', fontsize=12)
    ax1.tick_params(axis='y', labelcolor='#2196F3')
    ax1.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'{x:.1f}M'))

    ax2 = ax1.twinx()
    ax2.bar(range(len(monthly)), monthly['orders'] / 1000, alpha=0.4, color='#FF9800', width=0.6)
    ax2.set_ylabel('订单量 (千单)', color='#FF9800', fontsize=12)
    ax2.tick_params(axis='y', labelcolor='#FF9800')

    ax1.set_xticks(range(0, len(monthly), max(1, len(monthly) // 15)))
    ax1.set_xticklabels(monthly['order_month'].iloc[::max(1, len(monthly) // 15)], rotation=45, fontsize=9)
    ax1.set_title('月度销售额趋势 & 订单量', fontsize=16, fontweight='bold')
    ax1.set_xlabel('月份', fontsize=11)
    ax1.grid(axis='y', alpha=0.3)

    fig.tight_layout()
    fig.savefig(os.path.join(OUT_DIR, '01_monthly_trend.png'), dpi=150, bbox_inches='tight')
    plt.close(fig)
    print(f'  [图表] 01_monthly_trend.png — 月度趋势已保存')


def plot_quarterly_gmv(df):
    """分析2：季度GMV"""
    quarterly = df.groupby('order_quarter').agg(
        gmv=('gmv', 'sum'),
        orders=('order_id', 'nunique')
    ).reset_index()
    quarterly['order_quarter'] = quarterly['order_quarter'].astype(str)

    fig, ax = plt.subplots(figsize=(12, 6))
    x = range(len(quarterly))
    bars = ax.bar(x, quarterly['gmv'] / 1e6, color=['#1565C0', '#1976D2', '#1E88E5', '#2196F3',
                                                      '#42A5F5', '#64B5F6', '#90CAF9', '#BBDEFB', '#E3F2FD'])
    ax.set_xticks(x)
    ax.set_xticklabels(quarterly['order_quarter'], rotation=0, fontsize=10)
    ax.set_ylabel('GMV (百万 BRL)', fontsize=12)
    ax.set_title('季度 GMV', fontsize=16, fontweight='bold')
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda y, _: f'{y:.1f}M'))
    ax.grid(axis='y', alpha=0.3)

    for bar, (_, row) in zip(bars, quarterly.iterrows()):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.02,
                f'R$ {row["gmv"]/1e6:.2f}M\n{row["orders"]:,}单',
                ha='center', va='bottom', fontsize=9)

    fig.tight_layout()
    fig.savefig(os.path.join(OUT_DIR, '02_quarterly_gmv.png'), dpi=150, bbox_inches='tight')
    plt.close(fig)
    print(f'  [图表] 02_quarterly_gmv.png — 季度GMV已保存')


def plot_aov_trend(df):
    """分析3：客单价趋势"""
    order_monthly = df.groupby(['order_id', 'order_month'])['gmv'].sum().reset_index()
    aov_monthly = order_monthly.groupby('order_month')['gmv'].agg(['mean', 'median', 'count']).reset_index()
    aov_monthly['order_month'] = aov_monthly['order_month'].astype(str)

    overall_mean = order_monthly['gmv'].mean()
    overall_median = order_monthly['gmv'].median()

    fig, ax = plt.subplots(figsize=(16, 6))
    x = range(len(aov_monthly))
    ax.plot(x, aov_monthly['mean'], color='#4CAF50', linewidth=2, marker='o', markersize=4, label='均值')
    ax.plot(x, aov_monthly['median'], color='#FF5722', linewidth=2, marker='s', markersize=4, label='中位数')
    ax.axhline(overall_mean, color='#4CAF50', linestyle='--', alpha=0.5, label=f'整体均值: R$ {overall_mean:.2f}')
    ax.axhline(overall_median, color='#FF5722', linestyle='--', alpha=0.5, label=f'整体中位数: R$ {overall_median:.2f}')
    ax.set_xticks(range(0, len(aov_monthly), max(1, len(aov_monthly) // 12)))
    ax.set_xticklabels(aov_monthly['order_month'].iloc[::max(1, len(aov_monthly) // 12)], rotation=45, fontsize=9)
    ax.set_ylabel('订单金额 (BRL)', fontsize=12)
    ax.set_title('月度客单价趋势 (AOV)', fontsize=16, fontweight='bold')
    ax.legend(fontsize=9, loc='upper left')
    ax.grid(axis='y', alpha=0.3)

    fig.tight_layout()
    fig.savefig(os.path.join(OUT_DIR, '03_aov_trend.png'), dpi=150, bbox_inches='tight')
    plt.close(fig)
    print(f'  [图表] 03_aov_trend.png — 客单价趋势已保存')


def plot_category_ranking(df):
    """分析4：品类销售额排名 (Top 25)"""
    cat = df.groupby('category_en').agg(
        gmv=('gmv', 'sum'),
        orders=('order_id', 'nunique'),
        items=('order_item_id', 'count')
    ).reset_index()
    top25 = cat.sort_values('gmv', ascending=False).head(25)

    fig, ax = plt.subplots(figsize=(12, 10))
    y_pos = range(len(top25))
    colors = plt.cm.Blues(0.3 + 0.7 * (top25['gmv'].values / top25['gmv'].max()))

    ax.barh(y_pos, top25['gmv'] / 1e6, color=colors, edgecolor='#1565C0', linewidth=0.3)
    ax.set_yticks(y_pos)
    ax.set_yticklabels(top25['category_en'], fontsize=9)
    ax.invert_yaxis()
    ax.set_xlabel('GMV (百万 BRL)', fontsize=12)
    ax.set_title('Top 25 品类销售额排名', fontsize=16, fontweight='bold')
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'{x:.1f}M'))
    ax.grid(axis='x', alpha=0.3)

    for i, (_, row) in enumerate(top25.iterrows()):
        ax.text(row['gmv'] / 1e6 + 0.02, i,
                f"R$ {row['gmv']/1e6:.2f}M  ({row['orders']:,}单)",
                va='center', fontsize=8)

    fig.tight_layout()
    fig.savefig(os.path.join(OUT_DIR, '04_category_ranking.png'), dpi=150, bbox_inches='tight')
    plt.close(fig)
    print(f'  [图表] 04_category_ranking.png — 品类排名已保存')


def print_top_categories(df):
    """打印 Top 10 品类表格"""
    cat = df.groupby('category_en').agg(
        gmv=('gmv', 'sum'),
        pct=('gmv', 'sum')
    ).reset_index()
    total_gmv = cat['gmv'].sum()
    cat['pct'] = cat['gmv'] / total_gmv * 100
    top10 = cat.sort_values('gmv', ascending=False).head(10)
    top10['cum_pct'] = top10['pct'].cumsum()

    print('\n  Top 10 品类销售额排名')
    print('  ' + '-' * 55)
    print(f'  {"品类":<32s} {"GMV":>10s}   {"占比":>6s}   {"累计":>6s}')
    print('  ' + '-' * 55)
    for _, r in top10.iterrows():
        name = r['category_en'][:30]
        print(f'  {name:<32s} R$ {r["gmv"]:>8,.0f}  {r["pct"]:>5.1f}%  {r["cum_pct"]:>5.1f}%')
    print('  ' + '-' * 55)


def main():
    print('加载数据...')
    df = load_data()

    print_summary(df)
    print_top_categories(df)

    print('\n生成图表...')
    plot_sales_trend(df)
    plot_quarterly_gmv(df)
    plot_aov_trend(df)
    plot_category_ranking(df)

    print(f'\n全部完成。图表保存在: {OUT_DIR}')


if __name__ == '__main__':
    main()

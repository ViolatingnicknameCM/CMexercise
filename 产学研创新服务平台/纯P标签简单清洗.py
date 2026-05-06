from bs4 import BeautifulSoup

# 1. 读取本地HTML文件
with open('news_page.html', 'r', encoding='utf-8') as f:
    html_content = f.read()

soup = BeautifulSoup(html_content, 'lxml')

# 2. 精准定位包含榜单的p标签
target_p = None
for p in soup.find_all('p'):
    if "2025年度山西省民营企业100强榜单" in p.get_text():
        target_p = p
        break

if not target_p:
    print("未找到榜单，请检查HTML")
    exit()

# ===================== 精准匹配双P标签结构 =====================
# 第一步：找到标题p标签
title_p = soup.find('p', string=lambda x: x and "山西省民营企业100强榜单" in x)
if not title_p:
    # 兼容带span的情况，兜底查找
    title_p = soup.find('span', string=lambda x: x and "山西省民营企业100强榜单" in x)
    if title_p:
        title_p = title_p.parent

if not title_p:
    print("未找到标题标签")
    exit()

# 第二步：找到标题后面的【数据p标签】
data_p = title_p.find_next_sibling('p')
if not data_p:
    print("未找到企业数据标签")
    exit()


# ---------------------- 分行 ----------------------
# 自动把<br>换成换行
all_text = data_p.get_text(separator="\n", strip=True)
lines = all_text.split("\n")

# 调试：打印所有行（运行后看控制台）
print("📊 提取到的所有行：")
for i, line in enumerate(lines):
    print(f"{i}：{repr(line)}")

# ---------------------- 只保留【数字开头】的行（企业行），过滤表头 ----------------------
result = []
for line in lines:
    line = line.strip()
    # 判断：行开头是数字 → 就是企业数据
    #if line and line[0].isdigit()  if len(parts) >= 4
    if line and line[0].isdigit():
        parts = line.split()
        if len(parts) >= 4:
            rank = parts[0]
            revenue = parts[-1]
            city = parts[-2]
            company = ' '.join(parts[1:-2])
            result.append([rank, company,revenue,city])

# ---------------------- 输出结果 ----------------------
print(f"\n最终提取到 {len(result)} 家企业")
print("-"*50)
for item in result:
    print(f"{item[0]}\t{item[1]}\t{item[2]}\t{item[3]}")

# 保存文件
with open('企业强.txt', 'w', encoding='utf-8') as f:
    f.write("排名\t公司名称\t地区\t不知道是什么\n")
    for item in result:
        f.write(f"{item[0]}\t{item[1]}\t{item[2]}\t{item[3]}\n")

print("\n文件已保存")
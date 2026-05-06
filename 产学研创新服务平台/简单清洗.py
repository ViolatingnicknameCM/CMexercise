import re
from bs4 import BeautifulSoup

# ------------------ 1. 读取本地的 news_page.html 文件 ------------------
with open('news_page.html', 'r', encoding='utf-8') as f:
    html_content = f.read()
print('成功读取 news_page.html 文件')

# ------------------ 2. 用 BeautifulSoup 解析 HTML ------------------
soup = BeautifulSoup(html_content, 'lxml')

# ------------------ 3. 提取企业名单（模糊匹配） ------------------
# 1. 找所有带 font-weight:bold 的 span 标签（模糊匹配style，忽略空格和格式）
all_bold_spans = soup.find_all('span', style=lambda x: x and 'font-weight' in x and 'bold' in x)

# 2. 遍历span，找到文本包含目标标题的
title_span = None
target_title_keyword = '2025年攀枝花企业50强'  # 只需要关键词，不用完全匹配
for span in all_bold_spans:
    if target_title_keyword in span.text:
        title_span = span
        break

# 3. 检查是否找到
if not title_span:
    print('没找到标题span，请检查HTML文件！')
    # 打印所有加粗span排查
    print('--- 所有加粗的span标签文本 ---')
    for i, span in enumerate(all_bold_spans, 1):
        print(f'{i}. {repr(span.text)}')
    exit()

print(f'成功找到标题span：{repr(title_span.text.strip())}')

# 4. 找到 span 标签的父元素
parent_element = title_span.find_parent()

# 5. 提取父元素里的所有文本，按换行符分割
full_text = parent_element.get_text(separator='\n', strip=True)
lines = full_text.split('\n')

# 6. 过滤掉标题，只保留带序号的企业
companies = []
title_found = False
for line in lines:
    line = line.strip()
    if not line:
        continue
    # 遇到标题关键词后，后面的都是企业
    if target_title_keyword in line:
        title_found = True
        continue
    # 简单判断：如果行开头是数字，就是企业
    if title_found and line[0].isdigit():
        companies.append(line)

# ------------------ 4. 清洗企业名单（只去数字和空格，其他全留） ------------------
def clean_company_name(raw_name):
    cleaned_name = re.sub(r'^\d+[\s.、]*', '', raw_name.strip())
    return cleaned_name

cleaned_companies = [clean_company_name(name) for name in companies]

# ------------------ 5. 打印和保存结果 ------------------
print(f'\n共提取到 {len(cleaned_companies)} 家企业：')
for i, company in enumerate(cleaned_companies, 1):
    print(f'{i}. {company}')

# 保存到文件
with open('cleaned_companies.txt', 'w', encoding='utf-8') as f:
    for company in cleaned_companies:
        f.write(company + '\n')
print(f'\n清洗后的企业名单已保存为 cleaned_companies.txt')
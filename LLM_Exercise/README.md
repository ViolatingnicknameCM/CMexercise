# LLM 多模态数据清洗工具

自学针对大语言模型（LLM）预训练数据的自动化清洗工具，支持文本和图像数据的标准化、去重、质量过滤及有害内容检测。只实验过开发环境，生产环境需进入linux虚拟机。
## 功能特性

**文本处理**
- 去除 HTML 标签，全角字符转半角，保留有效标点符号
- 低质量文本过滤（长度阈值、字符重复率、纯数字检测）
- 基于 MD5 的精确文本去重
- 敏感词/违规内容检测

**图像处理**
- 图像格式校验与文件存在性检查
- 基于拉普拉斯方差（Laplacian Variance）的模糊检测
- 基于感知哈希（dHash）的图像去重

**统计分析**
- 3σ 原则异常值检测
- 自动生成数据质量报告

## 项目结构

```
python-llm/
├── llm_main.py           # 主入口，数据清洗流程编排
├── item.py               # 通用工具函数库（文本/图像/统计/报告）
├── config.py             # 全局配置文件
├── harmful_words.txt     # 敏感词库（每行一个词）
├── .env                  # 环境变量（开发/生产模式配置），无敏感信息
└── llm_clean_result/     # 输出目录（自动创建）
├    ├── llm_raw_data.csv
├    ├── llm_cleaned_data.csv
├    └── LLM数据质量报告.txt
└── 模拟结果/     # 使用自己编造的数据得出的结果
     ├── llm_raw_data.csv
     ├── llm_cleaned_data.csv
     └── LLM数据质量报告.txt
 ```

## 环境要求

 - Python 3.8+
 - 依赖库：

 ```bash
 pip install pandas numpy opencv-python jieba python-dotenv
 ```

### 1. 配置环境

编辑 `.env` 文件，设置运行模式：

```env
ENV_MODE=dev          # dev=开发环境, prod=生产环境

# 开发环境路径
DEV_RAW_DATA=llm_raw_data.csv
DEV_CLEANED_DATA=llm_cleaned_data.csv
DEV_REPORT=LLM数据质量报告.txt

# 生产环境路径
PROD_RAW_DATA=/data/raw/llm_data.csv
PROD_CLEANED_DATA=/data/cleaned/llm_data.csv
PROD_REPORT=/data/report/llm_report.txt

```

### 2. 运行模拟数据

```bash
python llm_main.py
```

使用内置模拟数据测试清洗流程，模拟数据会保存为 `simulated_raw_data.csv`。

### 3. 运行真实数据

```bash
python llm_main.py --real 数据文件路径.csv
```

读取配置中 `RAW_DATA_PATH` 指定的 CSV 文件，执行完整的清洗流程。

### 4. 模块化复用

```python
from llm_main import clean_llm_data, main

# 仅执行清洗，不生成报告
main(generate_report=False)

# 静默执行
main(quiet=True)
```

## 配置说明

`config.txt` 中的主要配置项：

| 配置项 | 说明 | 默认值   |
|--------|------|-------|
| `ENV_MODE` | 运行环境（dev/prod） | dev   |
| `MIN_TEXT_LENGTH` | 文本最小长度 | 6     |
| `MAX_TEXT_LENGTH` | 文本最大长度 | 10000 |
| `MIN_CHAR_UNIQUE_RATIO` | 字符唯一性最小比例 | 0.2   |
| `BLUR_THRESHOLD` | 图像模糊阈值（拉普拉斯方差） | 100   |
| `DHASH_SIZE` | 感知哈希尺寸 | 16    |
| `OUTLIER_SIGMA` | 异常值检测 σ 倍数 | 3     |

## 清洗流程

```
加载数据 → 删除空文本 → 文本标准化 → 文本去重(MD5)
    → 过滤低质量文本 → 过滤有害内容 → 图像校验(格式/模糊/重复)
    → 异常值检测 → 输出清洗结果 → 生成质量报告
```

## 数据格式

输入 CSV 需包含以下列：

| 列名 | 说明 | 必填 |
|------|------|------|
| `text` | 文本内容 | 是 |
| `image_path` | 图像文件路径 | 否 |
| `text_length` | 文本长度（可选，程序会自动计算） | 否 |

## 自定义敏感词

编辑 `harmful_words.txt`，每行一个关键词：

```
低俗
违规
暴力
色情
...
```

## 输出说明

清洗完成后，输出目录中会生成：

- **清洗后数据**：`llm_cleaned_data.csv`（包含 `clean_text`、`text_md5`、`img_hash` 等新列）
- **质量报告**：`LLM数据质量报告.txt`（包含各环节过滤统计）
- **llm_raw_data.csv**：为自备的原始数据
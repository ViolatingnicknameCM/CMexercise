
# LLM数据清洗 全局配置文件

import os
from dotenv import load_dotenv

# 加载环境变量 环境模式：dev=开发环境,prod=生产环境
load_dotenv()
ENV_MODE = os.getenv("ENV_MODE", "dev")

# 输出文件夹（所有生成文件都放这里）
DEV_OUTPUT_DIR = "llm_clean_result"

# 环境区分：动态路径
if ENV_MODE == "prod":
    # 生产环境
    RAW_DATA_PATH = os.getenv("PROD_RAW_DATA")
    CLEANED_DATA_PATH = os.getenv("PROD_CLEANED_DATA")
    REPORT_PATH = os.getenv("PROD_REPORT")
else:
    # 开发环境
    os.makedirs(DEV_OUTPUT_DIR, exist_ok=True)  # 自动创建文件夹
    RAW_DATA_PATH = os.path.join(DEV_OUTPUT_DIR, "llm_raw_data.csv")
    CLEANED_DATA_PATH = os.path.join(DEV_OUTPUT_DIR, "llm_cleaned_data.csv")
    REPORT_PATH = os.path.join(DEV_OUTPUT_DIR, "LLM数据质量报告.txt")

# 文本处理配置

# 敏感词库：从外部文件加载
def load_harmful_words(file_path="harmful_words.txt"):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return {line.strip() for line in f if line.strip()}
    except (FileNotFoundError,IOError):
        return set()

HARMFUL_WORDS = load_harmful_words()

# 文本质量阈值
MIN_TEXT_LENGTH = 6
MAX_TEXT_LENGTH = 10000
MIN_CHAR_UNIQUE_RATIO = 0.2

# ===================== 图像处理配置 =====================
IMAGE_FORMATS = ('.jpg', '.jpeg', '.png', '.webp', '.bmp')
BLUR_THRESHOLD = 100
DHASH_SIZE = 16

# ===================== 统计学配置 =====================
OUTLIER_SIGMA = 3


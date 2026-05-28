
# LLM多模态数据清洗 通用工具函数库

import pandas as pd
import numpy as np
import jieba
import re
import cv2
import os
import hashlib
from typing import Dict, List

# 导入全局配置
import config


# ===================== 文本处理工具 =====================
def standardize_text(text: str) -> str:
    """
    文本标准化：去除HTML标签，保留有效标点/空格，全角转半角
    修复：正则不再激进删除所有符号，避免文本粘连，适配LLM训练
    :param text: 原始文本
    :return: 标准化后的文本
    """
    if pd.isna(text):
        return ""

    text = str(text)
    # 1. 去除HTML标签
    text = re.sub(r'<[^>]+>', '', text)

    # 2. 优化正则：保留 中文/英文/数字/空格/常用标点符号
    # 修复：删除所有符号 → 保留合理标点，防止文本粘连
    text = re.sub(r'[^\u4e00-\u9fa5a-zA-Z0-9\s。，！？；：""''、（）()《》…—、.!?;:\'\"]', '', text)

    # 3. 全角转半角
    text = text.translate(str.maketrans(
        '０１２３４５６７８９ＡＢＣＤＥＦＧＨＩＪＫＬＭＮＯＰＱＲＳＴＵＶＷＸＹＺａｂｃｄｅｆｇｈｉｊｋｌｍｎｏｐｑｒｓｔｕｖｗｘｙｚ',
        '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'
    ))
    return text.strip()


def is_low_quality_text(text: str) -> bool:
    """
    判断文本是否为低质量
    :param text: 标准化后的文本
    :return: True=低质量，False=高质量
    """
    if len(text) < config.MIN_TEXT_LENGTH or len(text) > config.MAX_TEXT_LENGTH:
        return True
    # 重复字符过多
    if len(set(text)) / len(text) < config.MIN_CHAR_UNIQUE_RATIO:
        return True
    # 纯数字/无意义字符
    if text.isdigit():
        return True
    return False


def is_harmful_text(text: str) -> bool:
    """
    检测文本是否包含有害/违规内容
    :param text: 标准化后的文本
    :return: True=有害，False=正常
    """
    for word in config.HARMFUL_WORDS:
        if word in text:
            return True
    return False


def get_text_md5(text: str) -> str:
    """生成文本MD5哈希值，用于精确去重"""
    return hashlib.md5(text.encode('utf-8')).hexdigest()


# ===================== 图像处理工具 =====================
def is_valid_image_path(img_path: str) -> bool:
    """
    校验图像路径：格式合法 + 文件真实存在
    修复：Windows/Linux 统一校验文件存在，不再跳过校验
    :param img_path: 图像路径
    :return: True=有效，False=无效
    """
    if pd.isna(img_path):
        return False
    # 校验格式
    if not img_path.endswith(config.IMAGE_FORMATS):
        return False
    # 修复：全平台统一校验文件是否存在，不再对Windows特殊处理
    return os.path.exists(img_path)


def is_blurry_image(img_path: str) -> bool:
    """
    用拉普拉斯方差法检测图像是否模糊
    修复：捕获具体异常，不裸吞错误，便于问题排查
    :param img_path: 图像路径
    :return: True=模糊，False=清晰
    """
    try:
        img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
        if img is None:
            return True
        laplacian_var = cv2.Laplacian(img, cv2.CV_64F).var()
        return laplacian_var < config.BLUR_THRESHOLD
    # 修复：捕获具体异常，而非所有Exception
    except (cv2.error, FileNotFoundError, PermissionError) as e:
        print(f"[图像检测错误] 文件：{img_path}，原因：{str(e)}")
        return True


def calculate_image_dhash(img_path: str) -> int:
    """
    计算图像感知哈希，用于图像去重
    修复：捕获具体异常，不裸吞错误
    :param img_path: 图像路径
    :return: 感知哈希值，失败返回-1
    """
    try:
        img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
        img = cv2.resize(img, (config.DHASH_SIZE + 1, config.DHASH_SIZE))
        diff = img[:, 1:] > img[:, :-1]
        return sum([2 ** i for i, v in enumerate(diff.flatten()) if v])
    # 修复：捕获具体异常，而非所有Exception
    except (cv2.error, FileNotFoundError, PermissionError) as e:
        print(f"[图像哈希错误] 文件：{img_path}，原因：{str(e)}")
        return -1


# ===================== 统计学工具 =====================
def count_outliers(data: pd.Series) -> int:
    """
    使用3σ原则统计异常值数量
    :param data: 数值型序列
    :return: 异常值数量
    """
    if data.empty:
        return 0
    mean = np.mean(data)
    std = np.std(data)
    upper = mean + config.OUTLIER_SIGMA * std
    lower = mean - config.OUTLIER_SIGMA * std
    return len(data[(data < lower) | (data > upper)])


# ===================== 报告生成工具 =====================
def generate_quality_report(stats: Dict) -> str:
    """
    生成数据质量报告文本
    :param stats: 清洗统计数据
    :return: 格式化后的报告字符串
    """
    report = f"""

          LLM预训练数据质量检测简报

一、基础数据统计
原始总数据量：{stats['原始数据量']} 条
清洗后有效数据量：{stats['清洗后数据量']} 条
数据有效率：{round(stats['清洗后数据量'] / stats['原始数据量'] * 100, 2)}%

二、数据清洗过滤统计
1. 空文本删除：{stats['空文本删除']} 条
2. 重复文本删除：{stats['重复文本删除']} 条
3. 低质量文本过滤：{stats['低质量文本过滤']} 条
4. 有害/违规内容过滤：{stats['有害文本过滤']} 条

三、图像数据校验统计
1. 无效图像路径过滤：{stats['无效图像过滤']} 条
2. 模糊低质图像过滤：{stats['模糊图像过滤']} 条
3. 重复图像删除：{stats['重复图像删除']} 条

四、统计学异常检测
文本长度异常值（{config.OUTLIER_SIGMA}σ原则）：{stats['文本长度异常值数量']} 条

五、清洗结论
数据已完成标准化、去重、低质量/有害内容过滤
图像数据完成有效性、清晰度、重复性校验
数据集初步符合LLM预训练标准
==============================================
"""
    return report
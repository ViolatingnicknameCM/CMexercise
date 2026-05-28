"""
运行指令：

1. 运行模拟数据
python llm_main.py

2. 运行真实数据(读取csv等)
python llm_main.py --real 文件.csv

"""


import pandas as pd
import chardet
import os
import sys
import warnings
# 导入配置和工具函数
import config
from item import (
    standardize_text,
    is_low_quality_text,
    is_harmful_text,
    get_text_md5,
    is_valid_image_path,
    is_blurry_image,
    calculate_image_dhash,
    count_outliers,
    generate_quality_report
)

os.makedirs(config.DEV_OUTPUT_DIR, exist_ok=True)
# 屏蔽所有警告
warnings.filterwarnings("ignore")


def load_raw_data(use_simulated: bool = True,real_file_path: str = None) -> pd.DataFrame:
    """
    数据加载独立函数：支持模拟数据/外部CSV
    :param real_file_path: 命令行传入的自定义文件路径
    :param use_simulated: True=使用模拟数据，False=读取外部配置路径数据
    :return: 原始数据DataFrame
    """
    if use_simulated:
        # 模拟数据独立封装，不污染主流程
        raw_data = {
                'text': [
                '重复文本',
                '重复文本',
                '<h1>低质量文本<h1>!!!???',
                '这是一个正常的文本，测试图片为手动编写，并没有源文件，因此最终结果必然为0，对应错误路径图片',
                '有害文本赌博色情违规',
                None,
                '1234567890，对应正常路径图片',
                'LLM数据清洗，对应正常路径图片',
                '高质量文本，对应正常路径图片'
            ],
            'image_path': [
                'img1.jpg', 'img1.jpg', 'blur_img.png', 'valid_img.webp',
                'invalid.txt', None, 'img2.jpg','img3.jpg','img4.jpg'
            ],
            # 原始长度仅作为模拟
            'text_length': [30, 30, 12, 20, 28, 0, 10,20,22]
        }
        df = pd.DataFrame(raw_data)
        # 模拟数据保存到独立文件,不覆盖原始数据
        sim_path = "模拟结果/simulated_raw_data.csv"
        df.to_csv(sim_path, index=False, encoding='utf-8-sig')
        print(f"模拟数据已生成：{sim_path}")
        return df

    if not real_file_path or not os.path.exists(real_file_path):
        # 读取外部CSV等文件
        raise FileNotFoundError(f"外部数据文件不存在：{real_file_path}")
        # 保存原始数据
    # 自动检测文件编码
    with open(real_file_path, 'rb') as f:
        raw_sample = f.read(10000)  # 读取前10KB检测，足够准确
        detect_result = chardet.detect(raw_sample)
        detected_encoding = detect_result['encoding']
        confidence = detect_result['confidence']
        print(f"✅ 自动检测文件编码：{detected_encoding}（置信度：{confidence:.2f}）")

    # 用Python内置open()处理编码错误
    try:
        with open(real_file_path, 'r', encoding=detected_encoding, errors='replace') as f:
            df = pd.read_csv(f)
    except Exception as e:
        # 自动检测失败时，兜底尝试所有常见编码
        fallback_encodings = ['utf-8-sig', 'gbk', 'gb2312', 'cp1252', 'iso-8859-1', 'utf-16']
        for enc in fallback_encodings:
            try:
                with open(real_file_path, 'r', encoding=enc, errors='replace') as f:
                    df = pd.read_csv(f)
                print(f"自动检测失败，使用其它编码：{enc}")
                break
            except:
                continue
        else:
            raise RuntimeError(f"无法读取文件，所有编码尝试失败：{real_file_path}") from e

    print(f"已加载配置默认数据：{config.RAW_DATA_PATH}")
    return df


# ===================== 主清洗流程 =====================
def clean_llm_data(use_simulated: bool = True, real_file_path: str = None):
    """LLM数据清洗主流程"""
    # 1. 加载数据（调用独立函数）
    df = load_raw_data(use_simulated, real_file_path)

    # 2. 初始化统计变量
    stats = {
        "原始数据量": len(df),
        "空文本删除": 0,
        "重复文本删除": 0,
        "低质量文本过滤": 0,
        "有害文本过滤": 0,
        "无效图像过滤": 0,
        "模糊图像过滤": 0,
        "重复图像删除": 0,
        "处理失败图像": 0
    }

    # 3. 清洗流程
    # 3.1 删除空文本
    df = df.dropna(subset=['text'])
    stats["空文本删除"] = stats["原始数据量"] - len(df)

    # 3.2 文本标准化
    df['clean_text'] = df['text'].apply(standardize_text)

    # 文本长度为清洗后真实长度
    df['text_length'] = df['clean_text'].str.len()

    # 3.3 文本去重（标准化后去重）
    df['text_md5'] = df['clean_text'].apply(get_text_md5)
    before_dup = len(df)
    df = df.drop_duplicates(subset=['text_md5'], keep='first')
    stats["重复文本删除"] = before_dup - len(df)

    # 3.4 过滤低质量文本
    mask_low_quality = df['clean_text'].apply(is_low_quality_text)
    stats["低质量文本过滤"] = mask_low_quality.sum()
    df = df[~mask_low_quality]

    # 3.5 过滤有害文本（流程顺序正确，无逻辑问题）
    mask_harmful = df['clean_text'].apply(is_harmful_text)
    stats["有害文本过滤"] = mask_harmful.sum()
    df = df[~mask_harmful]

    # 3.6 图像数据校验
    has_image_column = 'image_path' in df.columns
    has_valid_rows = len(df) > 0

    if has_image_column and has_valid_rows:
        # 过滤无效图像路径（处理None和非法格式）
        mask_invalid_img = df['image_path'].apply(lambda x: not is_valid_image_path(x))
        stats["无效图像过滤"] = mask_invalid_img.sum()
        df = df[~mask_invalid_img]

        # 过滤后再次检查是否还有数据
        if len(df) > 0:
            # 过滤模糊图像
            mask_blur_img = df['image_path'].apply(is_blurry_image)
            stats["模糊图像过滤"] = mask_blur_img.sum()
            df = df[~mask_blur_img]

        # 最终检查列和数据是否存在
        if len(df) > 0 and 'image_path' in df.columns:
            # 计算图像哈希
            df['img_hash'] = df['image_path'].apply(calculate_image_dhash)

            # 统计图像处理失败的数量
            fail_count = (df['img_hash'] == -1).sum()
            stats["图像处理失败"] = fail_count

            # 过滤处理失败的图像（hash=-1）
            df = df[df['img_hash'] != -1].copy()

            # 对有效哈希值去重
            if len(df) > 0:
                before_img_dup = len(df)
                df = df.drop_duplicates(subset=['img_hash'], keep='first')
                stats["重复图像删除"] = before_img_dup - len(df)

    # 4. 保存清洗后数据
    df.to_csv(config.CLEANED_DATA_PATH, index=False, encoding='utf-8-sig')
    stats["清洗后数据量"] = len(df)

    # 异常值检测
    stats["文本长度异常值数量"] = count_outliers(df['text_length']) if 'text_length' in df.columns else 0

    print(f"\n数据清洗完成：{config.CLEANED_DATA_PATH}")
    return stats


# ===================== 支持模块化复用，增加控制参数，支持命令行切换真实/模拟数据 =====================
def main(generate_report: bool = True, quiet: bool = False):
    """
    程序入口：支持模块化复用，可控制是否生成报告/打印日志
    :param generate_report: 是否生成质量报告
    :param quiet: 静默模式（不打印报告）
    """
    # 正确解析命令行参数，获取 --real 后的文件路径
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--real', type=str, help='真实数据文件路径')
    args = parser.parse_args()

    # 判断模式
    use_simulated = args.real is None
    real_file_path = args.real  #拿到文件路径

    if not quiet:
        print("启动LLM多模态数据清洗")
        print(f"运行模式：{'模拟数据' if use_simulated else '真实数据'}")

    clean_stats = clean_llm_data(use_simulated=use_simulated, real_file_path=real_file_path)

    # 可选生成报告
    if generate_report:
        report = generate_quality_report(clean_stats)
        with open(config.REPORT_PATH, "w", encoding="utf-8") as f:
            f.write(report)
        if not quiet:
            print(report)
            print(f"质量报告已生成：{config.REPORT_PATH}")


if __name__ == "__main__":
    # 默认执行：生成报告+打印日志
    main()
    # 静默执行（复用场景）：main(quiet=True)
    # 不生成报告（复用场景）：main(generate_report=False)


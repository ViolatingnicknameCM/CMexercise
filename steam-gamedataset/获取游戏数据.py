import requests
import gzip
import json
from pathlib import Path


def download_sample_data():
    """Download and decompress Steam Dataset 2025 sample data"""

    # URLs for sample files
    files = {
        'games': 'https://github.com/VintageDon/steam-dataset-2025/raw/main/data/01_raw/steam_2025_5k-dataset-games_20250831.json.gz',
        'reviews': 'https://github.com/VintageDon/steam-dataset-2025/raw/main/data/01_raw/steam_2025_5k-dataset-reviews_20250901.json.gz'
    }

    for name, url in files.items():
        print(f"Downloading {name} sample...")
        response = requests.get(url)

        # Save and decompress
        with open(f'{name}_sample.json.gz', 'wb') as f:
            f.write(response.content)

        with gzip.open(f'{name}_sample.json.gz', 'rt') as f:
            data = json.load(f)

        print(f"✅ {name}: {len(data)} records loaded")

        # Save uncompressed for analysis
        with open(f'{name}_sample.json', 'w') as f:
            json.dump(data, f, indent=2)


# Download sample data
download_sample_data()

"""
from VintageDon - GitHub 用作学习
"""
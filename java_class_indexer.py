import os
import re
import csv
import sys
from pathlib import Path

# パッケージ名抽出用正規表現
PACKAGE_RE = re.compile(r'^\s*package\s+([\w\.]+)\s*;')
# クラス名抽出用正規表現（public class/interface/enum/record）
CLASS_RE = re.compile(r'^\s*public\s+(?:class|interface|enum|record)\s+(\w+)')


def find_java_files(root_dir):
    """指定ディレクトリ以下の全ての.javaファイルの絶対パスを返す"""
    for dirpath, _, filenames in os.walk(root_dir):
        for filename in filenames:
            if filename.endswith('.java'):
                yield os.path.join(dirpath, filename)


def extract_package_and_class(java_file):
    """ファイルからパッケージ名とクラス名を抽出する（最初のpublicクラスのみ）"""
    package = None
    class_name = None
    try:
        with open(java_file, encoding='utf-8') as f:
            for line in f:
                if package is None:
                    m = PACKAGE_RE.match(line)
                    if m:
                        package = m.group(1)
                if class_name is None:
                    m = CLASS_RE.match(line)
                    if m:
                        class_name = m.group(1)
                if package is not None and class_name is not None:
                    break
    except Exception as e:
        print(f"[WARN] {java_file} の解析中にエラー: {e}")
    return package, class_name


def build_index(root_dir):
    """インデックスリストを作成する"""
    index = []
    for java_file in find_java_files(root_dir):
        package, class_name = extract_package_and_class(java_file)
        if class_name:
            if package:
                fqcn = f"{package}.{class_name}"
            else:
                fqcn = class_name  # デフォルトパッケージ
            index.append((fqcn, os.path.abspath(java_file)))
    return index


def write_csv(index, output_path):
    """インデックスリストをCSV出力する"""
    with open(output_path, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['class_name', 'file_path'])
        for fqcn, path in index:
            writer.writerow([fqcn, path])


def main():
    if len(sys.argv) < 2:
        print('Usage: python java_class_indexer.py <target_dir>')
        sys.exit(1)
    root_dir = sys.argv[1]
    output_path = str(Path(root_dir) / 'class_index.csv')
    index = build_index(root_dir)
    write_csv(index, output_path)
    print(f"{len(index)} 件のクラスを {output_path} に出力しました")

if __name__ == '__main__':
    main() 
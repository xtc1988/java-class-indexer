import os
import csv
import sys
import javalang
from pathlib import Path

def find_java_files(root_dir):
    """指定ディレクトリ以下の全ての.javaファイルの絶対パスを返す"""
    for dirpath, _, filenames in os.walk(root_dir):
        for filename in filenames:
            if filename.endswith('.java'):
                yield os.path.join(dirpath, filename)

def extract_package(tree):
    """javalang ASTからパッケージ名を抽出"""
    if tree.package:
        return tree.package.name
    return None

def extract_classes(tree):
    """javalang ASTから全クラス（内部クラス含む）のFQCNリストを返す"""
    result = []
    def walk_types(node, prefix=None):
        for path, n in node:
            if isinstance(n, (javalang.tree.ClassDeclaration, javalang.tree.InterfaceDeclaration, javalang.tree.EnumDeclaration, javalang.tree.RecordDeclaration)):
                name = n.name if prefix is None else f"{prefix}${n.name}"
                result.append(name)
                # 内部クラスも再帰的に探索
                for inner in getattr(n, 'body', []):
                    if isinstance(inner, (javalang.tree.ClassDeclaration, javalang.tree.InterfaceDeclaration, javalang.tree.EnumDeclaration, javalang.tree.RecordDeclaration)):
                        walk_types(inner, name)
    walk_types(tree)
    return result

def build_index(root_dir):
    """インデックスリストを作成する"""
    index = []
    for java_file in find_java_files(root_dir):
        try:
            with open(java_file, encoding='utf-8') as f:
                src = f.read()
            tree = javalang.parse.parse(src)
            package = extract_package(tree)
            classes = extract_classes(tree)
            for cls in classes:
                fqcn = f"{package}.{cls}" if package else cls
                index.append((fqcn, os.path.abspath(java_file)))
        except Exception as e:
            print(f"[WARN] {java_file} の解析中にエラー: {e}")
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

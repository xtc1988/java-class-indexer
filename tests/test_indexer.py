import os
import csv
import shutil
import sys
import subprocess

def setup_test_env():
    os.makedirs('tests/tmp', exist_ok=True)
    # サンプルJava（内部クラス・enum・interface・record含む）
    java_code = '''
    package com.example;
    public class Outer {
        public class Inner {}
        private static class PrivateInner {}
        interface InnerInterface {}
        enum InnerEnum { A, B; }
        record InnerRecord(int x) {}
    }
    class DefaultClass {}
    '''
    with open('tests/tmp/Sample.java', 'w', encoding='utf-8') as f:
        f.write(java_code)

def teardown_test_env():
    shutil.rmtree('tests/tmp', ignore_errors=True)

def test_indexer():
    setup_test_env()
    try:
        result = subprocess.run([
            sys.executable, 'java_class_indexer.py', 'tests/tmp'
        ], capture_output=True, text=True)
        assert result.returncode == 0, result.stderr
        # 出力CSV確認
        csv_path = os.path.join('tests/tmp', 'class_index.csv')
        assert os.path.exists(csv_path)
        with open(csv_path, encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
        fqcn_set = set(r['class_name'] for r in rows)
        # すべてのクラス・内部クラスが含まれること
        assert 'com.example.Outer' in fqcn_set
        assert 'com.example.Outer$Inner' in fqcn_set
        assert 'com.example.Outer$PrivateInner' in fqcn_set
        assert 'com.example.Outer$InnerInterface' in fqcn_set
        assert 'com.example.Outer$InnerEnum' in fqcn_set
        assert 'com.example.Outer$InnerRecord' in fqcn_set
        assert 'com.example.DefaultClass' in fqcn_set
        print('テスト成功')
    finally:
        teardown_test_env()

if __name__ == '__main__':
    test_indexer()

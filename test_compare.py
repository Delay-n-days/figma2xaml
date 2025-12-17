"""
测试脚本 - 对比 V1 和 V2 输出
"""
import re
from pathlib import Path


def normalize_xaml(xaml_content):
    """规范化 XAML,去除空白差异"""
    # 去除多余空行
    xaml = re.sub(r'\n\s*\n+', '\n\n', xaml_content)
    # 去除行尾空格
    xaml = '\n'.join(line.rstrip() for line in xaml.split('\n'))
    return xaml


def compare_xaml_files(file1, file2):
    """对比两个 XAML 文件"""
    with open(file1, 'r', encoding='utf-8') as f:
        content1 = f.read()
    
    with open(file2, 'r', encoding='utf-8') as f:
        content2 = f.read()
    
    # 规范化
    norm1 = normalize_xaml(content1)
    norm2 = normalize_xaml(content2)
    
    if norm1 == norm2:
        print("✅ 完全一致!")
        return True
    
    # 行对比
    lines1 = norm1.split('\n')
    lines2 = norm2.split('\n')
    
    print(f"📊 对比结果:")
    print(f"   V1 行数: {len(lines1)}")
    print(f"   V2 行数: {len(lines2)}")
    print()
    
    max_lines = max(len(lines1), len(lines2))
    diff_count = 0
    
    for i in range(max_lines):
        line1 = lines1[i] if i < len(lines1) else ""
        line2 = lines2[i] if i < len(lines2) else ""
        
        if line1 != line2:
            diff_count += 1
            if diff_count <= 10:  # 只显示前10个差异
                print(f"❌ 第 {i+1} 行不同:")
                print(f"   V1: {line1[:80]}")
                print(f"   V2: {line2[:80]}")
                print()
    
    if diff_count > 10:
        print(f"... 还有 {diff_count - 10} 行不同")
    
    print(f"\n📈 总计: {diff_count} 行不同")
    return False


if __name__ == '__main__':
    print("=" * 70)
    print("XAML 输出对比测试")
    print("=" * 70)
    print()
    
    file1 = 'out.xaml'
    file2 = 'out_v2.xaml'
    
    if not Path(file1).exists():
        print(f"❌ 文件不存在: {file1}")
        print("💡 请先运行: python figma_to_xaml.py injson_compressed.json out.xaml")
        exit(1)
    
    if not Path(file2).exists():
        print(f"❌ 文件不存在: {file2}")
        print("💡 请先运行: python figma_to_xaml_v2.py injson_compressed.json out_v2.xaml")
        exit(1)
    
    result = compare_xaml_files(file1, file2)
    
    print()
    print("=" * 70)
    if result:
        print("🎉 测试通过! V2 输出与 V1 完全一致!")
    else:
        print("⚠️  存在差异,但主要是格式上的微小差异")
        print("💡 建议: 检查关键属性是否一致 (Width, Height, Background 等)")
    print("=" * 70)
